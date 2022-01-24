# flat-manager-ocr

### Overview

Python service capable of extracting transactions from receipts send over RabbitMQ.

### Getting started

#### Requirements

Service is contenerized, therefore you need to setup `docker` and `docker-compose` for convenience.

#### Start

To start the service, you first need to prepare your `.env` file.

Next, start the app using `docker-compose`:
```shell
$ docker-compose up --build -d
```
