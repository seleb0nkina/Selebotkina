"""
Конфиг файл.
"""


config = {
    "Token": '5741930145:AAFTu9kv1-kNXDSmpELwnZS_qCelj7kFq1I', #Токен телеграм-бота
    "JsonName": 'text.json', # Путь к файлу с текстом
    "FileSizeMax": 1024, # Ограничение по размеру файла в Кб
    "ImgXSizeMax": 1024, # Ограничение на размер изображения max по X
    "ImgXSizeMin": 128, # Ограничение на размер изображения min по X
    "ImgYSizeMax": 512,  # Ограничение на размер изображения max по Y
    "ImgYSizeMin": 128,  # Ограничение на размер изображения min по Y
    "TrackLimit": 3, # Ограничение на колво треков
    "AudioLengthLimit": 420, # Ограничение на длину аудио в секундах
    "LogFileDir": "sample.log", # Путь к файлу логирования
    "ContentDir": "content\\" # Путь к файлу с контентом

}
