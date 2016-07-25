# -*- coding: utf-8 -*-
import unittest, requests, json, time

main_url = "https://genesis-mihailselezniov.c9users.io/"

class Test(unittest.TestCase):
    
    
    def get_json_from_url(self, url, data):
        get_url = main_url + url
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(get_url, data=json.dumps(data), headers=headers)
        return json.loads(r.text)
    
    
    def test_check_variables_in_response(self):
        json = self.get_json_from_url("weather", {"city_name":"ялтА"})
        self.assertEqual("info" in json, True)
        info = json["info"]
        self.assertEqual("region" in info, True)
        self.assertEqual("weather" in info, True)
        self.assertEqual("traffic" in info, True)
        weather = info["weather"]
        self.assertEqual("@region" in weather, True)
        self.assertEqual("url" in weather, True)
        self.assertEqual("day" in weather, True)
        day = weather["day"]
        self.assertEqual("day_part" in day, True)
        day_part = day["day_part"]
        self.assertEqual(len(day_part) == 5, True)
        day_part0 = day_part[0]
        self.assertEqual("wind_speed" in day_part0, True)
        self.assertEqual("dampness" in day_part0, True)
        self.assertEqual("pressure" in day_part0, True)
        for i in range(5):
            part = day_part[i]
            self.assertEqual("@typeid" in part, True)
            self.assertEqual("@type" in part, True)


    def test_variant_spellings_city(self):
        variants = ["ялта", "ЯЛТА", "Ялта", "ялтА", "яЛта", "ялТа", "ЯлтА", "яЛтА", "ЯлТа", "яЛТа"]
        for variant in variants:
            json = self.get_json_from_url("weather", {"city_name":variant})
            self.assertEqual(int(json["info"]["weather"]["@region"]) == 11470, True)
    
    
    def test_check_city_regions(self):
        variants = [[10282, u"Пицунда"], [113, u"Вена"], [20544, u"Киев"], [213, u"Москва"]]
        for id, city in variants:
            json = self.get_json_from_url("weather_cid", {"city_id":str(id)})
            self.assertEqual(json["info"]["weather"]["day"]["title"] == city, True)
            

if __name__ == "__main__":
    unittest.main()