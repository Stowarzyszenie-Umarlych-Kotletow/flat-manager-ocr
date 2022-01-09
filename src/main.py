import pytesseract
from pytesseract import Output
from PIL import Image
from typing import BinaryIO
import pika
import json
import cv2
import time
import threading
import base64
import io


def get_ocr_data(image) -> dict:
    return pytesseract.image_to_data(image, output_type=Output.DICT, lang="pol")


def get_results(image) -> list:
    return calculate_boxes_coords(image)


def calculate_boxes_coords(image) -> list:
    ocr_data = get_ocr_data(image)
    results = []
    for i in range(len(ocr_data["level"])):
        if ocr_data["text"][i] != "":
            results.append(
                {
                    "left": ocr_data["left"][i],
                    "top": ocr_data["top"][i],
                    "right": ocr_data["left"][i] + ocr_data["width"][i],
                    "bottom": ocr_data["top"][i] + ocr_data["height"][i],
                    "text": ocr_data["text"][i],
                }
            )
    return results


def prepare_body(body) -> dict:
    try:
        return json.loads(body)
    except Exception as e:
        print("Exception occured!" + e.__str__())


def process(body, channel) -> None:
    prepared_body = prepare_body(body)
    imgdata = base64.b64decode(prepared_body["data"])
    img = Image.open(io.BytesIO(imgdata))
    result = get_results(img)
    print(result)
    channel.basic_publish(
        exchange="",
        routing_key="manager_service",
        body=json.dumps(result),
    )


def consume(ch, method, properties, body) -> None:
    thread = threading.Thread(
        target=process,
        args=(
            body,
            channel,
        ),
    )
    thread.daemon = True
    thread.run()


credentials = pika.PlainCredentials("ocr", "ocrPassword")
parameters = pika.ConnectionParameters("127.0.0.1", 5672, "/", credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.basic_consume(queue="ocr_service", auto_ack=True, on_message_callback=consume)

channel.start_consuming()

connection.close()
