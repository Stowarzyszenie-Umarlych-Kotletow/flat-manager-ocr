# flat-manager-ocr

### Overview

Python service capable of extracting transactions from receipts send over RabbitMQ.

### Getting started

#### Requirements

Service is contenerized, therefore you need to setup `docker` and `docker-compose` for convenience.

#### Start

To start the service, you first need to prepare your `.env` file.


```OCR_USERNAME``` - rabbitMQ username

```OCR_PASSWORD``` - password for the rabbitMQ user

```OCR_ADDRESS``` - address of the rabbitMQ instance

```OCR_QUEUE_NAME``` - name of the queue directed towards this service

```SERVICE_QUEUE_NAME``` - name of the queue directed towards the spring backend



Next, start the app using `docker-compose`:
```shell
$ docker-compose up --build -d
```
