"""Создание кнопок клавиатуры для погодного бота"""
from telebot import types

reply_btn_start = types.KeyboardButton('Начать сначала')
reply_btn_weather_today = types.KeyboardButton('Погода на сегодня')
reply_btn_weather_date = types.KeyboardButton('Погода на определённую дату')

reply_kb = types.ReplyKeyboardMarkup(row_width=1)
reply_kb.add(reply_btn_weather_today, reply_btn_weather_date, reply_btn_start)
