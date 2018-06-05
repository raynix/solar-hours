import requests
import json
import time
import os

from datetime import datetime, timedelta

def main():
    """
    {
      "results": {
        "sunrise":"9:31:31 PM",
        "sunset":"7:18:24 AM",
        "solar_noon":"2:24:58 AM",
        "day_length":"09:46:53",
        "civil_twilight_begin":"9:02:43 PM",
        "civil_twilight_end":"7:47:13 AM",
        "nautical_twilight_begin":"8:30:15 PM",
        "nautical_twilight_end":"8:19:40 AM",
        "astronomical_twilight_begin":"7:58:36 PM",
        "astronomical_twilight_end":"8:51:19 AM"
      },
      "status":"OK"
    }
    """
    sd = SunData()
    if sd.has_solar():
        print("There should be sun light!")
        exit(0)
    else:
        print("There's no sun light!")
        exit(1)

class SunData:
    def __init__(self, lat=-37.9845511, lng=145.2645971):
        self.today = datetime.today()
        self.cache = '/tmp/cache'
        self.sun_data = self.sun_api(lat, lng)
        self.tz_delta = timedelta(hours=self.get_tz_delta())

    def get_sun_rise(self):
        sun_rise_time = datetime.strptime(self.sun_data['sunrise'], "%I:%M:%S %p")
        sun_rise_datetime = (sun_rise_time + self.tz_delta).replace(
            year=self.today.year,
            month=self.today.month,
            day=self.today.day
        )
        return sun_rise_datetime

    def get_sun_set(self):
        sun_rise_time = datetime.strptime(self.sun_data['sunset'], "%I:%M:%S %p")
        sun_rise_datetime = (sun_rise_time + self.tz_delta).replace(
            year=self.today.year,
            month=self.today.month,
            day=self.today.day
        )
        return sun_rise_datetime

    def has_solar(self):
        now = datetime.now()
        return now > self.get_sun_rise() and now < self.get_sun_set()

    def sun_api(self, lat, lng):
        cache_result = self.check_cache()
        if cache_result:
            result = json.loads(cache_result)
        else:
            rest_url = "https://api.sunrise-sunset.org/json?lat={0}&lng={1}&date=today".format(lat, lng)
            response = requests.get(rest_url)
            result = json.loads(response.content.decode('utf8'))
            self.update_cache(response.content)
        return result['results']

    def check_cache(self):
        if os.path.exists(self.cache) and self.today < datetime.fromtimestamp(os.path.getmtime(self.cache)) + timedelta(hours=24):
            with open(self.cache) as f:
                cache_result = f.read()
            return cache_result
        else:
            return False

    def update_cache(self, content):
        with open(self.cache, 'w') as f:
            f.write(content.decode('utf8'))

    def get_tz_delta(self):
        offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
        return offset / -3600


if __name__ == '__main__':
    main()
