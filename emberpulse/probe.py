import os
import re
import time
import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from influxdb import InfluxDBClient

def push_points(args, solar_data):
  json_body = []
  for metric_key, metric_value in solar_data.items():
    json_body.append(
      {
        "measurement": "electricity",
        "tags": {
          "metric": metric_key
        },
        "fields": {
          "value": metric_value
        }
      }
    )
  if args.debug:
    print(json.dumps(json_body))
  client = InfluxDBClient(args.influx_host, args.influx_port, args.influx_user)
  client.write_points(json_body, database=args.influx_database)

def selenium_firefox():
  return webdriver.Firefox()

def ember_login(args, driver):
  driver.get('https://emberpulse.com.au/login')
  elem_id = driver.find_element_by_id('username')
  elem_pwd = driver.find_element_by_id('password')
  elem_btn = driver.find_element_by_css_selector('.btn')
  elem_id.send_keys(args.ember_user)
  elem_pwd.send_keys(args.ember_pass)
  elem_btn.click()
  assert "Home" in driver.title

def ember_read_solar(driver):
  elem_solar = driver.find_element_by_id('solar-icon-readout')
  return re.match('^([0-9]+)', elem_solar.text).group(0)

def ember_read_home_load(driver):
  elem_load = driver.find_element_by_id('home-icon-readout')
  return re.match('^([0-9]+)', elem_load.text).group(0)

def main():
  parser = argparse.ArgumentParser(description="Usage for solar system probe")
  parser.add_argument('--influx-host', type=str, default='localhost')
  parser.add_argument('--influx-port', type=int, default=8086)
  parser.add_argument('--influx-user', type=str, default='')
  parser.add_argument('--influx-database', type=str, default='energy')
  parser.add_argument('--ember-user', type=str, default=os.environ['EMBERUSER'])
  parser.add_argument('--ember-pass', type=str, default=os.environ['EMBERPASS'])
  parser.add_argument('--debug', action='store_true')


  args = parser.parse_args()

  driver = selenium_firefox()
  try:
    ember_login(args, driver)
    while True:
      solar_data = {
        'solar': ember_read_solar(driver),
        'load': ember_read_home_load(driver)
      }
      push_points(args, solar_data=)
      time.sleep(15)
  finally:
    driver.close()
