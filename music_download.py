"""
Файл, отвечающий за скачивание музыки.
"""

import sys
import os
from config import config
from loguru import logger as lg
from youtubesearchpython import VideosSearch
from pytube import YouTube

# Подключение логирования
lg.add(config['LogFileDir'], format="{time} {level} {message}", level="INFO")

# Функция получения ссылки на видео (трек) по названию
def get_link(title):
        videosSearch = VideosSearch(title, limit = 1)
        if len(videosSearch.result()['result']) > 0:
                return videosSearch.result()['result'][0]['link']
        else:
                return "error"

# Функция сохранения видео (трека) по ссылке
def download(title):
        try:
                link = get_link(title)
                if link != "error":
                        yt_obj = YouTube(get_link(title))
                else:
                        return "error"
                if yt_obj.length < config["AudioLengthLimit"]:
                        video = yt_obj.streams.get_audio_only()
                        filename = ''.join(char for char in yt_obj.title if char.isalnum()) # Избавляемся от спец. символов
                        video.download(output_path=config["ContentDir"], filename=filename + ".mp3")
                        new_file_name = "content\\" + filename + ".mp3"

                        return new_file_name
                else:
                        return "error"
        except Exception as e:
                lg.error(e)
                return "error"



"""
Библиотека устарела для новой версии YouTube, в которой отсутствуют лайки и дизлайки.

I propose to change the lines 53 and 54 of file * backend_youtube_dl.py * to :

self._likes = self._ydl_info.get('like_count',0)
self._dislikes = self._ydl_info.get('dislike_count',0)
"""