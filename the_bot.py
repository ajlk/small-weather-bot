"""- Бот умеет смотреть погоду на сегодня для любого города. Ограничение: города, находящиеся за пределами России или
Белоруссии, должны быть заданы на английском языке. По всей видимости проблема вызвана неполной локализацией под
русский язык;
- Запросы реализованы через библиотеку pyowm;
- Использован API от OWM."""

import keyboards_weather_bot as kb  # клавиатура
import defs_weather_bot as defs  # проверка погоды
import telebot
import pyowm
import json
import os

token = os.environ['TELEGRAM_TOKEN']
BOT = telebot.TeleBot(token)

degree_sign = u'\N{DEGREE SIGN}'

try:
    data = json.load(open('data.json', 'r', encoding='utf-8'))
except FileNotFoundError:
    data = {
        'states': {}
    }


# изменение состояний
def change_data(key, user_id, value):
    data[key][user_id] = value
    json.dump(
        data,
        open('data.json', 'w', encoding='utf-8'),
        indent=2,
        ensure_ascii=False
    )


@BOT.message_handler(commands=['help'])
def process_help_command(message):
    BOT.send_message(
        message.from_user.id,
        'Я - бот, помогающий узнать погоду в интересующем тебя городе.\n\n'
        'Необходимо выбрать один из предложенных '
        'вариантов взаимодействия со мной.\n\n'
        'После выполнения каждого запроса ты снова должны выбрать погоду либо на сегодня, либо на определённую дату.'
    )


@BOT.message_handler(commands=['start'])
def process_start_command(message):
    BOT.send_message(
        message.from_user.id,
        "Привет! Это бот-погода. Я помогу узнать погоду в любом городе.\n\n"
        "Выбери один из доступных вариантов:",
        reply_markup=kb.reply_kb)


@BOT.message_handler(func=lambda message: True)
def dispatcher(message):
    user_id = str(message.from_user.id)

    if message.text == 'Начать сначала':
        change_data('states', user_id, 0)
        process_start_command(message)
        return

    if data['states'][user_id]:
        current_user_state = data['states'][user_id]
    else:
        current_user_state = 0
    # ===============================================
    # 0 - параметр не определён;
    # 1 - погода на сегодня;
    # 2 - погода на определённую дату.
    # ===============================================

    # =============ОПРЕДЕЛЯЕМ ПАРАМЕТР ЗАПРОСА============= #
    if current_user_state == 0:
        if message.text == 'Погода на сегодня':
            change_data('states', user_id, 1)
            BOT.send_message(
                message.from_user.id,
                'Для какого города ты хотел бы узнать погоду на сегодня?\n\n'
                'Города, находящиеся за пределами России, должны быть заданы на английском языке.'
            )
        elif message.text == 'Погода на определённую дату':
            change_data('states', user_id, 2)
            BOT.send_message(
                message.from_user.id,
                'Какой город и какая дата тебя интересуют?\n\n'
                'Формат запроса: ГОРОД DD.MM\n\n'
                'Запрашиваемая дата не может быть позднее 4-х дней от текущей.\n'
                'Город должен быть задан на английском языке!'
            )
        else:
            BOT.send_message(
                message.from_user.id,
                'Я тебя не понял.\n'
                'Выбери один из предложенных вариантов:'
            )
            return
    # =============КОНЕЦ ОПРЕДЕЛЕНИЯ ПАРАМЕТРА ЗАПРОСА============= #

    if current_user_state != 0:
        city_handler(message, current_user_state, user_id)


def city_handler(message, user_state, user_id):
    if user_state == 1:
        try:
            weather = defs.current_weather(message.text.lower())
        except pyowm.exceptions.api_response_error.NotFoundError:
            BOT.send_message(
                message.from_user.id,
                'Я тебя не понял. Попробуй ввести название города ещё раз.'
            )
            return
        the_city = message.text.lower()

        # ======== ОСНОВНОЙ ОБРАБОТЧИК ================================
        the_message = defs.answer_constructor_today(the_city, weather)

        BOT.send_message(message.from_user.id, the_message)
        change_data('states', user_id, 0)  # обнуление состояния
        # =============================================================

    else:  # user_state==2
        # =============================================================
        # Проверяем корректность введённой даты
        try:
            day = int(message.text[-5:-3])
            month = int(message.text[-2:])
        except ValueError:
            BOT.send_message(
                message.from_user.id,
                'Формат даты неверен.\n'
                'Попробуй ещё раз.'
            )
            return

        delta_and_date = defs.date_checker(day, month)
        if delta_and_date[0] > 4 or delta_and_date[0] < 1:
            BOT.send_message(
                message.from_user.id,
                'Запрашиваемая дата выходит за допустимые пределы.\n\n'
                'Пожалуйста повтори запрос с другой датой, лежащей в пределах 4-х дней от текущей.'
            )
            return
        # =============================================================

        weather = defs.forecast(message.text[:-5].lower(), delta_and_date[1])
        if weather == 404:
            BOT.send_message(
                message.from_user.id,
                'Я тебя не понял. Попробуй ввести название города ещё раз (на английском языке).'
            )
            return

        the_city = message.text[:-5].lower()
        the_date = message.text[-5:]

        # ======== ОСНОВНОЙ ОБРАБОТЧИК ================================
        the_message = defs.answer_constructor_forecast(the_city, the_date, weather)

        BOT.send_message(message.from_user.id, the_message)
        change_data('states', user_id, 0)  # обнуление состояния
        # =============================================================


BOT.polling()
