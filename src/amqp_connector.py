import pika
import json
import threading
import logging
from pika.adapters.blocking_connection import BlockingChannel
from data_extractor import DataExtractor


class AMQPConnector:

    username = "ocr"
    password = "ocrPassword"
    address = "127.0.0.1"
    port = 5672
    read_queue_name = "ocr_service"
    send_queue_name = "manager_service"

    extractor = DataExtractor()
    logger = logging.getLogger("AMQPConnector")
    logging.getLogger("pika").setLevel(logging.WARNING)

    @staticmethod
    def prepare_body(body: str) -> dict:
        return json.loads(body)

    @staticmethod
    def process(body: str, channel: BlockingChannel, extractor: DataExtractor) -> None:
        try:
            prepared_body: dict = AMQPConnector.prepare_body(body)
            data = extractor.extract_data(prepared_body["data"])
            AMQPConnector.logger.info("Data extracted.")
            message = json.dumps(dict(message=data))
        except Exception as e:
            message = json.dumps(dict(message=str(e)))
            AMQPConnector.logger.error("Error occured", exc_info=e)
        finally:
            channel.basic_publish(
                exchange="",
                routing_key=AMQPConnector.send_queue_name,
                body=message,
            )
            AMQPConnector.logger.info("Published message to manager_service queue")

    @staticmethod
    def consume(ch: BlockingChannel, method, properties, body) -> None:
        thread = threading.Thread(
            target=AMQPConnector.process,
            args=(body, ch, AMQPConnector.extractor),
        )
        thread.daemon = True
        thread.run()

    @staticmethod
    def start():
        credentials = pika.PlainCredentials(
            AMQPConnector.username, AMQPConnector.password
        )
        parameters = pika.ConnectionParameters(
            AMQPConnector.address, AMQPConnector.port, "/", credentials
        )
        connection = pika.BlockingConnection(parameters)
        logging.error(
            "Established connection on (%s:%s)",
            AMQPConnector.address,
            AMQPConnector.port,
        )
        channel = connection.channel()

        channel.basic_consume(
            queue=AMQPConnector.read_queue_name,
            auto_ack=True,
            on_message_callback=AMQPConnector.consume,
        )

        AMQPConnector.logger.info(
            "Started listining on %s queue", AMQPConnector.read_queue_name
        )
        channel.start_consuming()

        connection.close()
