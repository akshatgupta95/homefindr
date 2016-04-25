from bs4 import BeautifulSoup
from urllib2 import urlopen
import urllib
import time
import json

def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html, 'html.parser')

city_state = []
city_state.append({"city": "New+York", "state": "NY"})
city_state.append({"city": "San+Francisco", "state": "CA"})
city_state.append({"city": "Boston", "state": "MA"})
city_state.append({"city": "Chicago", "state": "IL"})

zip_codes = {}

url = "http://www.getzips.com/cgi-bin/ziplook.exe?What=2&City=%s&State=%s&Submit=Look+It+Up"

for cs in city_state:
    custom_url = url % (cs['city'], cs['state'])
    print cs['city']
    html_comp = make_soup(custom_url)
    zip_comps = html_comp.findAll('td', {'width': '15%'})
    zip_codes[cs['city'].replace("+", " ")] = []
    for zip_comp in zip_comps:
        zip = zip_comp.find('p').text
        if zip != "ZIP":
            zip_codes[cs['city'].replace("+", " ")].append(zip)

with open('zipcodes_by_city.json', 'w') as fp:
    json.dump(zip_codes, fp)
