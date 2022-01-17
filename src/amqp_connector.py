import pika
import json
import threading
from pika.adapters.blocking_connection import BlockingChannel
from data_extractor import DataExtractor


class AMQPConnector:

    username = "ocr"
    password = "ocrPassword"

    extractor = DataExtractor()

    @staticmethod
    def prepare_body(body: str) -> dict:
        return json.loads(body)

    @staticmethod
    def process(body: str, channel: BlockingChannel, extractor: DataExtractor) -> None:
        try:
            prepared_body: dict = AMQPConnector.prepare_body(body)
            data = extractor.extract_data(prepared_body["data"])
            print(data)
            message = json.dumps(dict(message=data))
        except Exception as e:
            message = json.dumps(dict(message=str(e)))
        finally:
            channel.basic_publish(
                exchange="",
                routing_key="manager_service",
                body=message,
            )

    @staticmethod
    def consume(ch: BlockingChannel, method, properties, body) -> None:
        thread = threading.Thread(
            target=AMQPConnector.process,
            args=(body, ch, AMQPConnector.extractor),
        )
        thread.daemon = True
        thread.run()
        # AMQPConnector.process(body, ch, AMQPConnector.extractor)

    @staticmethod
    def start():
        credentials = pika.PlainCredentials(
            AMQPConnector.username, AMQPConnector.password
        )
        parameters = pika.ConnectionParameters("127.0.0.1", 5672, "/", credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.basic_consume(
            queue="ocr_service",
            auto_ack=True,
            on_message_callback=AMQPConnector.consume,
        )

        channel.start_consuming()

        connection.close()
