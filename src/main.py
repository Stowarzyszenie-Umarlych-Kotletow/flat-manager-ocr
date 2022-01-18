from amqp_connector import AMQPConnector
import logging


def main():
    logging.basicConfig(level="INFO", format="%(asctime)s %(message)s")
    AMQPConnector.start()


if __name__ == "__main__":
    main()
