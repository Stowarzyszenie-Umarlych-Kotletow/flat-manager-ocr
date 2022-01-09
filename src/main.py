import pytesseract
from pytesseract import Output
from PIL import Image
from typing import BinaryIO
import pika
import json

def consume(ch, method, properties, body):
    print(body)
    channel.basic_publish(exchange='', routing_key='manager_service', body=json.dumps({'name': 'Received'}))

credentials = pika.PlainCredentials('ocr', 'ocrPassword')
parameters = pika.ConnectionParameters(
    '127.0.0.1', 5672, '/', credentials
)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.basic_consume(queue='ocr_service', auto_ack=True, on_message_callback=consume)

channel.start_consuming()

connection.close()