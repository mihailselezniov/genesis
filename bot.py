# -*- coding: utf-8 -*-
import telebot, requests

token = '265784305:AAEyapE7qBFPvObRUIvhWyIMSoIpbv6JvRE'
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=["text"])
def main(message):
    if "p24" == message.text:
        p24_url = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=3"
        r = requests.get(p24_url)
        response = r.json()
        msg = "Exchange: buy / sale\n"
        for row in response:
            msg += "{0}: {2} {1} / {3} {1}\n".format(row["ccy"], row["base_ccy"], row["buy"], row["sale"])
        bot.send_message(message.chat.id, msg)
    elif not sum(map(lambda x: int(x.isalpha()), message.text)):
        msg = str(eval(message.text))
        bot.send_message(message.chat.id, msg)
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
    
    
if __name__ == '__main__':
    bot.polling(none_stop=True)