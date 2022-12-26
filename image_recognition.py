"""
Файл, отвечающий за распознование текста.
"""


import easyocr

# Функция распознования текста с картинки
def text_recognition(file_path, text_file_name):
    reader = easyocr.Reader(["ru", "en"])
    result = reader.readtext(file_path, detail=0, paragraph=True)

    with open(text_file_name, "w") as file:
        for line in result:
            file.write(f"{line}\n\n")

    return f"Result wrote into {text_file_name}"