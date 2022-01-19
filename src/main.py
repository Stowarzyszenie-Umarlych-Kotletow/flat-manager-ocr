from amqp_connector import AMQPConnector
import logging
import time


def main():
    logging.basicConfig(level="INFO", format="%(asctime)s %(message)s")
    while True:
        try:
            AMQPConnector.start()
        except Exception as e:
            logging.error("Retrying in 15 seconds...")
            logging.debug("Exception:", exc_info=e)
            time.sleep(15)


if __name__ == "__main__":
    main()
