"""All possible functions"""

from datetime import datetime
import requests
import pyowm
import os

OWM_API_KEY = os.environ['OWM_API_KEY']

# локализация
owm = pyowm.OWM(OWM_API_KEY, language='RU')


# смотрим погоду на сегодня
def current_weather(city):
    obs = owm.weather_at_place(city)
    return weather_details_today(obs)


# смотрим погоду на указанную дату
def forecast(city, date):
    api_url = 'http://api.openweathermap.org/data/2.5/forecast'
    params = {
        'q': city,
        'appid': OWM_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }

    res = requests.get(api_url, params=params)
    if res.status_code == 404:
        return 404
    month_from_date = int(date.month)
    day_from_date = int(date.day)

    weather_night = []
    weather_day = []

    for i in range(len(res.json()['list'])):
        month_then = int(res.json()['list'][i]['dt_txt'][5:7])
        day_then = int(res.json()['list'][i]['dt_txt'][8:10])

        if month_from_date == month_then and day_from_date == day_then:
            # погода ночью
            if int(res.json()['list'][i]['dt_txt'][11:13]) == 3:
                weather_night = weather_details_forecast(res.json()['list'][i])

            # погода днём
            if int(res.json()['list'][i]['dt_txt'][11:13]) == 15:
                weather_day = weather_details_forecast(res.json()['list'][i])
    return [weather_night, weather_day]


# определение средней температуры, направления и силы ветра, краткого дополнительного описания
def weather_details_today(w):
    city_weather = w.get_weather()

    if city_weather.get_temperature('celsius').get('temp'):
        temperature = city_weather.get_temperature('celsius').get('temp')
    else:
        temperature = None

    if city_weather.get_wind()['speed']:
        wind_speed = city_weather.get_wind()['speed']
    else:
        wind_speed = None

    if 'deg' in city_weather.get_wind():  # для некоторых городов направление ветра не указано
        compassSector = ["Северный ветер",
                         "Северный, северо-восточный ветер",
                         "Северо-восточный ветер",
                         "Восточный, северо-восточный ветер",
                         "Восточный ветер",
                         "Восточный, юго-восточный ветер",
                         "Юго-восточный ветер",
                         "Южный ветер",
                         "Южный, юго-западный ветер",
                         "Юго-западный ветер",
                         "Западный, юго-западный ветер",
                         "Западный ветер",
                         "Западный, северо-западный ветер",
                         "Северо-западный ветер",
                         "Северный, северо-западный ветер",
                         "Северный ветер"
                         ]
        wind_direction = compassSector[int(city_weather.get_wind()['deg'] / 22.5) - 1]
    else:
        wind_direction = None
    detailed_status = city_weather.get_detailed_status()
    # ===================================WEATHER-END===================================

    return [temperature, wind_direction, wind_speed, detailed_status.capitalize()]


# детали погоды для прогноза
def weather_details_forecast(raw_data):
    reply = []
    if raw_data['main']['temp']:
        reply.append(raw_data['main']['temp'])
    else:
        reply.append(None)
    if raw_data['main']['humidity']:
        reply.append(raw_data['main']['humidity'])
    else:
        reply.append(None)
    if raw_data['wind']['deg']:
        compassSector = ["Северный ветер",
                         "Северный, северо-восточный ветер",
                         "Северо-восточный ветер",
                         "Восточный, северо-восточный ветер",
                         "Восточный ветер",
                         "Восточный, юго-восточный ветер",
                         "Юго-восточный ветер",
                         "Южный ветер",
                         "Южный, юго-западный ветер",
                         "Юго-западный ветер",
                         "Западный, юго-западный ветер",
                         "Западный ветер",
                         "Западный, северо-западный ветер",
                         "Северо-западный ветер",
                         "Северный, северо-западный ветер",
                         "Северный ветер"
                         ]
        reply.append(compassSector[int(raw_data['wind']['deg'] / 22.5) - 1])
    else:
        reply.append(None)
    if raw_data['wind']['speed']:
        reply.append(raw_data['wind']['speed'])
    else:
        reply.append(None)
    if raw_data['weather'][0]['description']:
        reply.append(raw_data['weather'][0]['description'])
    else:
        reply.append(None)
    return reply


# проверка даты
def date_checker(day, month):
    now = datetime.now()
    then = datetime(now.year, month, day)
    delta = then.day - now.day
    if delta < 0:
        then = datetime(now.year + 1, month, day)
        delta = then - now
        delta = delta.days
    return [delta, then]


# собираем ответ пользователю
def answer_constructor_today(the_city, weather):
    degree_sign = u'\N{DEGREE SIGN}'  # знак градуса

    city_details_string = f'Погода на сегодня для города {the_city.capitalize()}:\n\n'

    temperature = weather[0]
    if temperature is not None:
        temperature_string = f'Температура воздуха {temperature} {degree_sign}C;\n'
    else:
        temperature_string = ''

    wind_direction = weather[1]
    if wind_direction is not None:
        wind_direction_string = f'{wind_direction};\n'
    else:
        wind_direction_string = ''

    wind_speed = weather[2]
    if wind_speed is not None:
        wind_speed_string = f'Скорость ветра {wind_speed} м/с;\n'
    else:
        wind_speed_string = ''

    detailed_info = weather[3]
    if detailed_info is not None:
        detailed_info_string = f'{detailed_info}.\n'
    else:
        detailed_info_string = ''

    the_message = f'{city_details_string}' \
                  f'{temperature_string}' \
                  f'{wind_direction_string}' \
                  f'{wind_speed_string}' \
                  f'{detailed_info_string}'
    return the_message


def answer_constructor_forecast(the_city, the_date, weather):
    degree_sign = u'\N{DEGREE SIGN}'  # знак градуса

    city_details_string = f'Погода на {the_date} для города {the_city.capitalize()}:\n\n'

    # =================== НОЧЬ ========================================
    temperature_night = weather[0][0]
    if temperature_night is not None:
        temperature_night_string = f'Температура воздуха {temperature_night} {degree_sign}C;\n'
    else:
        temperature_night_string = ''

    humidity_night = weather[0][1]
    if humidity_night is not None:
        humidity_night_string = f'Влажность воздуха {humidity_night} %;\n'
    else:
        humidity_night_string = ''

    wind_direction_night = weather[0][2]
    if wind_direction_night is not None:
        wind_direction_night_string = f'{wind_direction_night};\n'
    else:
        wind_direction_night_string = ''

    wind_speed_night = weather[0][3]
    if wind_speed_night is not None:
        wind_speed_night_string = f'Скорость ветра {wind_speed_night} м/с;\n'
    else:
        wind_speed_night_string = ''

    detailed_info_night = weather[0][4].capitalize()
    if detailed_info_night is not None:
        detailed_info_night_string = f'{detailed_info_night}.\n\n'
    else:
        detailed_info_night_string = '\n\n'
    # =================================================================
    # =================== ДЕНЬ ========================================
    temperature_day = weather[1][0]
    if temperature_day is not None:
        temperature_day_string = f'Температура воздуха {temperature_day} {degree_sign}C;\n'
    else:
        temperature_day_string = ''

    humidity_day = weather[1][1]
    if humidity_day is not None:
        humidity_day_string = f'Влажность воздуха {humidity_day} %;\n'
    else:
        humidity_day_string = ''

    wind_direction_day = weather[1][2]
    if wind_direction_day is not None:
        wind_direction_day_string = f'{wind_direction_day};\n'
    else:
        wind_direction_day_string = ''

    wind_speed_day = weather[1][3]
    if wind_speed_day is not None:
        wind_speed_day_string = f'Скорость ветра {wind_speed_day} м/с;\n'
    else:
        wind_speed_day_string = ''

    detailed_info_day = weather[1][4].capitalize()
    if detailed_info_day is not None:
        detailed_info_day_string = f'{detailed_info_day}.'
    else:
        detailed_info_day_string = ''

    the_message = f'{city_details_string}' \
                  f'Погода ночью:\n' \
                  f'{temperature_night_string}' \
                  f'{humidity_night_string}' \
                  f'{wind_direction_night_string}' \
                  f'{wind_speed_night_string}' \
                  f'{detailed_info_night_string}' \
                  f'Погода днём:\n' \
                  f'{temperature_day_string}' \
                  f'{humidity_day_string}' \
                  f'{wind_direction_day_string}' \
                  f'{wind_speed_day_string}' \
                  f'{detailed_info_day_string}'
    return the_message
