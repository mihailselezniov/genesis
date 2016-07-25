# -*- coding: utf-8 -*-
from app import *


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def check_city_attr(city_attr):
    def decorator(func):
        @wraps(func)
        def newfn(*args, **kwargs):
            var = 'city_{}'.format(city_attr)
            if not request.json or not var in request.json:
                abort(400)
            var_city = request.json.get(var, "")
            if not var_city:
                abort(400)
            if city_attr == "name":
                if var_city.isdigit():
                    abort(400)
            elif city_attr == "id":
                if not var_city.isdigit():
                    abort(400)
            return func(*args, **kwargs)
        return newfn
    return decorator


def replace_loads_cookie(cookie):
    cookie_quoting_map = [
        [b'\\054', b','],
        [b'\\073', b';'],
        [b'\\"', b'"'],
        [b'\\\\', b'\\'],
    ]
    for old, new in cookie_quoting_map:
        cookie = cookie.replace(old, new)
    return cookie


@app.route('/get-cities')
def get_cities():
    if not redis_server.get('get_cities'):
        redis_server.setex('get_cities', 'Ok', 30*60)
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
            c = Cities(id=region, name=city_name.lower())
            db.session.add(c)
        db.session.commit()
    return jsonify('Ok')


def change_cookies_cities(resp, operation, city_id):
    cities = request.cookies.get('cities')
    cities_row = int(city_id)
    cities_json = json.dumps([])
    if cities:
        cities_list = json.loads(replace_loads_cookie(cities))
        if not type(cities_list).__name__ == 'list':
            cities_list = []
        if operation == "remove":
            cities_list.remove(cities_row)
        elif operation == "append":
            cities_list.append(cities_row)
        cities_list = list(set(cities_list))
        cities_json = json.dumps(cities_list)
    resp.set_cookie('cities', cities_json)
    return resp


def fetch_city_weather(city_id):
    r_key = "city_id_{}".format(city_id)
    city_saved = redis_server.get(r_key)
    if city_saved:
        city_yandex = json.loads(city_saved)
    else:
        req = requests.get("https://export.yandex.ru/bar/reginfo.xml?region={}".format(city_id))
        city_yandex = xmltodict.parse(req.text)
        wait_time = 30*60
        redis_server.setex(r_key, json.dumps(city_yandex), wait_time)
    return city_yandex


@app.route('/remove-city', methods=['POST'])
@check_city_attr('name')
def remove_city():
    city = Cities.query.filter(Cities.name.like(u"%{}%".format(request.json.get('city_name', '').lower()))).first()
    if not city:
        print "*"*20
        abort(400)
    resp = make_response(jsonify("Ok"))
    return change_cookies_cities(resp, "remove", city.id)


@app.route('/weather', methods=['POST'])
@check_city_attr('name')
def get_weather():
    city = Cities.query.filter(Cities.name.like(u"%{}%".format(request.json.get('city_name', '').lower()))).first()
    if not city:
        abort(400)
    city_yandex = fetch_city_weather(city.id)
    resp = make_response(jsonify(city_yandex))
    return change_cookies_cities(resp, "append", city.id)


@app.route('/weather_cid', methods=['POST'])
@check_city_attr('id')
def get_weather_cid():
    city = Cities.query.filter_by(id=int(request.json.get('city_id', ''))).first()
    if not city:
        abort(400)
    return jsonify(fetch_city_weather(city.id))
    
#curl -i -H "Content-Type: application/json" -X POST -d '{"city_name":"ялтА"}' https://genesis-mihailselezniov.c9users.io/weather
#curl -i -H "Content-Type: application/json" -X POST -d '{"city_id":"11470"}' https://genesis-mihailselezniov.c9users.io/weather_cid


@app.route('/')
def main():
    cities = request.cookies.get('cities')
    cities=json.loads(replace_loads_cookie(cities)) if cities else []
    return render_template("main.html", cities=cities)
