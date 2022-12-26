"""
Основной исполняемый файл. Телеграм-бот.
"""


from config import config
from image_recognition import text_recognition
from PIL import Image
from music_download import download
from loguru import logger as lg
import database
import telebot
import json

# Подключение HTTP API Token
bot = telebot.TeleBot(config['Token'])

# Подключение логирования
lg.add(config['LogFileDir'], format="{time} {level} {message}", level="INFO")

# Функция получения текста из json
def text(text_id):
    with open(config['JsonName'], 'r', encoding='utf-8') as f:
        full_text = json.load(f)
        return full_text["text"][text_id]

# Функция получения текста для кнопок из json
def but_text(text_id):
    with open(config['JsonName'], 'r', encoding='utf-8') as f:
        full_text = json.load(f)
        return full_text["buttons"][text_id]

# Функция редактирования сообщения
def edit_text(bot, call, text, keyboard):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )

# Функция сохранения скрина
def save_photo(bot, message):
    try:
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        if (file_info.file_size)/1024 > config["FileSizeMax"]:
            return False
        file_name = str(message.chat.id) + ".jpg"
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'content/' + file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
            img_size_x = (Image.open(src).size)[0] # размер изображения по X
            img_size_y = (Image.open(src).size)[1]  # размер изображения по Y
            lg.info("save photo from: id = " + str(message.chat.id) +
                    " size = " + str(file_info.file_size) +
                    " size_x = " + str(img_size_x) +
                    " size_y = " + str(img_size_y))
            if not((config["ImgXSizeMax"] > img_size_x > config["ImgXSizeMin"])
                    and (config["ImgYSizeMax"] > img_size_y > config["ImgYSizeMin"])):
                return False

        return True

    except Exception as e:
        lg.error(e)
        return False

# Функция построчного чтения из файла с музыкой
def read_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()
    result = ''
    for i in range(len(content)):
        result += content[i]
    return result

# Функция построчного чтения из файла в список
def read_from_file_to_list(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()
    result = []
    for i in range(len(content)):
        if content[i] != "\n":
            result.append(content[i].replace('\n', ''))
    return result

# Функция команды /start
@bot.message_handler(commands=['start'])
def command_start(message):
    lg.info("command start from: id = " + str(message.chat.id))
    database.recording(message.chat.id)
    if database.read(message.chat.id, "step") != "process":
        database.update(message.chat.id, "step", "start")
        bot.send_message(
            chat_id=message.chat.id,
            text=text("start"),
            parse_mode='HTML',
            reply_markup=keyboard_start
        )
    else: pass

keyboard_start = telebot.types.InlineKeyboardMarkup(row_width=2)
keyboard_start.add(
    telebot.types.InlineKeyboardButton(but_text("contacts"), callback_data="contacts"),
    telebot.types.InlineKeyboardButton(but_text("send_photo"), callback_data="send_photo"),
    telebot.types.InlineKeyboardButton(but_text("send_kotik"), callback_data="send_kotik")

)

keyboard_main_menu = telebot.types.InlineKeyboardMarkup(row_width=1)
keyboard_main_menu.add(
    telebot.types.InlineKeyboardButton(but_text("main_menu"), callback_data="main_menu")
)

keyboard_download = telebot.types.InlineKeyboardMarkup(row_width=1)
keyboard_download.add(
    telebot.types.InlineKeyboardButton(but_text("download"), callback_data="download"),
    telebot.types.InlineKeyboardButton(but_text("error"), callback_data="error"),
    telebot.types.InlineKeyboardButton(but_text("main_menu"), callback_data="main_menu")
)

# Функция Callback
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if database.read(call.message.chat.id, "step") != "process":
            if call.data == "send_kotik":
                edit_text(bot, call, text('kotik'), keyboard_main_menu)

            elif call.data == "contacts":
                edit_text(bot, call, text('contacts'), keyboard_main_menu)

            elif call.data == "main_menu":
                edit_text(bot, call, text("start"), keyboard_start)
                database.update(call.message.chat.id, "step", "start")

            elif call.data == "send_photo":
                edit_text(bot, call, text("send_photo"), keyboard_main_menu)
                database.update(call.message.chat.id, "step", "doc")

            elif call.data == "download":
                lg.info("download from: id = " + str(call.message.chat.id))
                edit_text(bot, call, text("wait_for_download"), None)
                text_file_name = "content/" + str(call.message.chat.id) + ".txt"
                content = read_from_file_to_list(text_file_name)
                if len(content) > 3:
                    content_lenght = 3
                else:
                    content_lenght = len(content)

                for i in range(content_lenght):
                    filename = download(content[i])
                    if filename != "error":
                        with open(filename, 'rb') as file:
                            bot.send_document(call.message.chat.id, file, 'rb')
                            lg.info("text_recognition complete from: id = " + str(call.message.chat.id) +
                                   " filename = " + filename)

                    else:
                        bot.send_message(
                            chat_id=call.message.chat.id,
                            text=text("track_error"),
                            parse_mode='HTML'
                        )


                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=text("download_complete"),
                    parse_mode='HTML',
                    reply_markup=keyboard_main_menu
                )
                database.update(call.message.chat.id, "step", "start")

            elif call.data == "error":
                database.update(call.message.chat.id, "step", "doc")
                edit_text(bot, call, text("try_again"), keyboard_main_menu)


            bot.answer_callback_query(callback_query_id=call.id)

        else:
            bot.answer_callback_query(callback_query_id=call.id, text="ждите окончания загрузки!")


# Функция приема сообщений от пользователя
@bot.message_handler(content_types=['text'])
def get_text(message):
    if message:
        bot.send_message(
            chat_id=message.chat.id,
            text=text("dunduk"),
            parse_mode="HTML",
            reply_markup=keyboard_main_menu
        )

# Функция приема файлов от пользователя
@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    if database.read(message.chat.id, "step") == "doc": # прием скрина
        database.update(message.chat.id, "step", "process")
        if save_photo(bot, message):
            bot.send_message(
                chat_id=message.chat.id,
                text=text("save_success"),
                parse_mode="HTML",
            )
            file_path = "content/"+str(message.chat.id) + ".jpg"
            text_file_name = "content/"+str(message.chat.id) + ".txt"
            text_recognition(file_path=file_path, text_file_name=text_file_name)
            lg.info("text_recognition complete from: id = " + str(message.chat.id))
            bot.send_message(
                chat_id=message.chat.id,
                text=text("rec_success") + read_from_file(text_file_name) + text("rec_success_end"),
                reply_markup=keyboard_download,
                parse_mode="HTML",
            )
            database.update(message.chat.id, "step", "start")
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text=text("file_to_big"),
                reply_markup=keyboard_main_menu,
                parse_mode="HTML",
            )
            database.update(message.chat.id, "step", "start")

bot.infinity_polling(timeout=10, long_polling_timeout=5)
