FROM python:3.10-buster

WORKDIR /app

RUN apt update
RUN apt install -y tesseract-ocr
RUN apt install -y tesseract-ocr-pol

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]