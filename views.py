# -*- coding: utf-8 -*-
from app import *


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)
    
    
@app.route('/get-cities')
def get_cities():
    cities = Cities.query.all()
    for city in cities:
        db.session.delete(city)
    req = requests.get("https://pogoda.yandex.ru/static/cities.xml")
    cities_yandex = xmltodict.parse(req.text)
    cities_store = {}
    for country in cities_yandex["cities"]["country"]:
        for city in country["city"]:
            if type(city).__name__ == 'OrderedDict':
                cities_store[int(city["@region"])] = city["#text"]
    for region, city_name in cities_store.items():
        c = Cities(id=region, name=city_name)
        db.session.add(c)
    db.session.commit()
    return jsonify('Ok')
    

def get_city_request(attr_city):
    var = 'city_{}'.format(attr_city)
    if not request.json or not var in request.json:
        abort(400)
    var_city = request.json.get(var, "")
    if not var_city:
        abort(400)
    if attr_city == "name":
        city = Cities.query.filter(Cities.name.like(u"%{}%".format(var_city.capitalize()))).first()
    elif attr_city == "id":
        if not var_city.isdigit():
            abort(400)
        city = Cities.query.filter_by(id=int(var_city)).first()
    if not city:
        abort(400)
    return city


def change_cookies_cities(resp, operation, city_id):
    cities = request.cookies.get('cities')
    cities_row = str(city_id)
    if cities:
        cities_list = cities.split('_')
        if operation == "remove":
            cities_list.remove(cities_row)
        elif operation == "append":
            cities_list.append(cities_row)
        cities_list = list(set(cities_list))
        cities_row = '_'.join(cities_list)
    resp.set_cookie('cities', cities_row)
    return resp


def get_city_yandex(city_id):
    r_key = "city_id_{}".format(city_id)
    city_saved = r_server.get(r_key)
    if city_saved:
        city_yandex = json.loads(city_saved)
    else:
        req = requests.get("https://export.yandex.ru/bar/reginfo.xml?region={}".format(city_id))
        city_yandex = xmltodict.parse(req.text)
        wait_time = 30*60
        r_server.get(r_key)
        r_server.setex(r_key, json.dumps(city_yandex), wait_time)
    return city_yandex


@app.route('/remove-city', methods=['POST'])
def remove_city():
    city = get_city_request('name')
    resp = make_response(jsonify("Ok"))
    return change_cookies_cities(resp, "remove", city.id)


@app.route('/weather', methods=['POST'])
def get_weather():
    city = get_city_request('name')
    city_yandex = get_city_yandex(city.id)
    resp = make_response(jsonify(city_yandex))
    return change_cookies_cities(resp, "append", city.id)


@app.route('/weather_cid', methods=['POST'])
def get_weather_cid():
    city = get_city_request('id')
    return jsonify(get_city_yandex(city.id))
    
#curl -i -H "Content-Type: application/json" -X POST -d '{"city_name":"ялтА"}' https://genesis-mihailselezniov.c9users.io/weather
#curl -i -H "Content-Type: application/json" -X POST -d '{"city_id":"11470"}' https://genesis-mihailselezniov.c9users.io/weather_cid


@app.route('/')
def main():
    cities = request.cookies.get('cities')
    cities=cities.split("_") if cities else []
    return render_template("main.html", cities=cities)
