import json

with open('pricing_data.json') as data_file:
    cities = json.load(data_file)

max = 0
aggregated_cities = {}
for city in cities:
    if city == "austin":
        continue
    aggregated_cities[city] = []
    for region in cities[city]:
        try:
            val = float(region['zindex']['#text'])
            aggregated_cities[city].append(val)
            if val > max:
                max = val
        except Exception as e:
            continue

normalized_cities = {}
city_averages = {}
for city in aggregated_cities:
    city_averages[city] = float(sum(aggregated_cities[city]))/len(aggregated_cities[city])

for city in cities:
    if city == "austin":
        continue
    normalized_cities[city] = {}
    for region in cities[city]:
        try:
          val = float(region['zindex']['#text'])
        except:
            val = city_averages[city]

        zipcode = region['name']
        normalized_cities[city][zipcode] = val/max

with open('normalized_pricing_data.json', 'w') as fp:
    json.dump(normalized_cities, fp)

