import pika
import json
import threading
import logging
from pika.adapters.blocking_connection import BlockingChannel
from redis import BlockingConnectionPool
from data_extractor import DataExtractor
import os


class AMQPConnector:

    username = os.getenv('OCR_USERNAME', "ocr")
    password = os.getenv('OCR_PASSWORD', "ocrPassword")
    address = os.getenv('OCR_ADDRESS', "127.0.0.1")
    port = 5672
    read_queue_name = os.getenv('OCR_QUEUE_NAME', "ocr_service")
    send_queue_name = os.getenv('SERVICE_QUEUE_NAME', "manager_service")

    extractor = DataExtractor()
    logger = logging.getLogger("AMQPConnector")
    logging.getLogger("pika").setLevel(logging.CRITICAL)

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
        connection: pika.BlockingConnection
        try:
            connection = pika.BlockingConnection(parameters)
            AMQPConnector.logger.info(
                "Connected with RabbitMQ on (%s:%s)",
                AMQPConnector.address,
                AMQPConnector.port,
            )
        except Exception as e:
            AMQPConnector.logger.error(
                "Could not establish connection with RabbitMQ on (%s:%s).",
                AMQPConnector.address,
                AMQPConnector.port,
            )
            raise e

        try:
            channel = connection.channel()

            channel.basic_consume(
                queue=AMQPConnector.read_queue_name,
                auto_ack=True,
                on_message_callback=AMQPConnector.consume,
            )

            AMQPConnector.logger.info(
                'Started listening on "%s" queue', AMQPConnector.read_queue_name
            )
            channel.start_consuming()

            connection.close()
        except Exception as e:
            AMQPConnector.logger.error("Unexpected error occured!", exc_info=e)
