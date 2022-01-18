from PIL import Image
import base64
import pytesseract
from pytesseract import Output
import io


class DataExtractor:
    __language: str

    def __init__(self, language: str = "pol") -> None:
        self.__language = language

    def extract_data(self, b64_str: str) -> list:
        img = self.__b64_to_image(b64_str)
        found_text = self.__get_data_from_image(img)
        return self.__data_to_products_list(found_text)

    def __b64_to_image(self, data: str) -> Image:
        img_bytes = base64.b64decode(data)
        return Image.open(io.BytesIO(img_bytes))

    def __get_data_from_image(self, image: Image) -> list:
        ocr_data = pytesseract.image_to_data(
            image, output_type=Output.DICT, lang=self.__language
        )
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
                        "conf": ocr_data["conf"][i],
                    }
                )
        return results

    def __data_to_products_list(self, found_text: str) -> list:
        products = []
        temp = []
        for i, item in enumerate(found_text):
            if len(temp) == 0:
                temp.append(item)
                continue

            if item["left"] < temp[len(temp) - 1]["left"]:
                if temp[len(temp) - 1]["text"] == "PLN":
                    products.append(temp)
                temp = [item]
            else:
                temp.append(item)

            if item["text"] == "PLN" and len(found_text) - 1 == i:
                products.append(temp)

        final_values = []
        for item in products:
            final_values.append(
                dict(name=item[0]["text"], price=item[2]["text"].replace(",", "."))
            )
        return final_values
