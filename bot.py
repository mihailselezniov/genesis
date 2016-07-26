# -*- coding: utf-8 -*-
import telebot, requests


token = '265784305:AAEyapE7qBFPvObRUIvhWyIMSoIpbv6JvRE'
bot = telebot.TeleBot(token)


@bot.message_handler(content_types=["text"])
def main(message):
    # Exchange rates with Privat24
    if "p24" == message.text.lower():
        p24_url = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=3"
        r = requests.get(p24_url)
        response = r.json()
        msg = "Exchange: buy / sale\n"
        for row in response:
            msg += "{0}: {2} {1} / {3} {1}\n".format(row["ccy"], row["base_ccy"], row["buy"], row["sale"])
        bot.send_message(message.chat.id, msg)
    # Calculator
    elif not sum(map(lambda x: int(x.isalpha()), message.text)):
        msg = str(eval(message.text))
        bot.send_message(message.chat.id, msg)
    # Weather
    else:
        r = requests.post('https://genesis-mihailselezniov.c9users.io/weather', json={"city_name":message.text})
        response = r.json()
        if not 'error' in response:
            city_name = response['info']["weather"]["day"]['title']
            day_part = response['info']["weather"]["day"]["day_part"][0]
            temperature = day_part["temperature"]["#text"]
            dampness = day_part["dampness"]
            pressure = day_part["pressure"]
            wind_speed = day_part["wind_speed"]
            msg = u"{}\n{}°\nВлажность: {}%\nДавление: {} мм\nСкорость ветра: {} м/сек".format(
                city_name, temperature, dampness, pressure, wind_speed)
            bot.send_message(message.chat.id, msg)
        # Translation suggestions
        else:
            msg = message.text
            ru, en = 0, 0
            for i in msg:
                if u'а'<=i<=u'я' or u'А'<=i<=u'Я':
                    ru += 1
                elif u'a'<=i<=u'z' or u'A'<=i<=u'Z':
                    en += 1
            if ru > en:
                lang="ru-en"
            else:
                lang="en-ru"
            key = "trnsl.1.1.20160725T230300Z.5c6a542dc27e3a7d.3baed373aed1a3a990ad18f8e652adea67d14f72"
            url_translate_yandex = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
            r = requests.post(url_translate_yandex, data = {'key':key, 'text':msg, 'lang':lang})
            r_json = r.json()
            if r_json["code"] == 200:
                translate_msg = r_json["text"][0]
                bot.send_message(message.chat.id, translate_msg)
    
    
if __name__ == '__main__':
    bot.polling(none_stop=True)
