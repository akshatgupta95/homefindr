import json

cities = ['chicago', 'new_york', 'san_francisco', 'boston']
with open('normalized_data/normalized_aggregated_school_data.json') as a:
    school = json.load(a)
with open('normalized_data/normalized_pricing_data.json') as b:
    pricing = json.load(b)
with open('normalized_data/restaurants-scores.json') as c:
    restaurants = json.load(c)
with open('normalized_data/zipcode_crime.json') as d:
    crime = json.load(d)

with open('zipcodes_by_city.json') as e:
    zipcodes_by_city = json.load(e)

composite_scores = {}

for city in cities:
    composite_scores[city] = {}
    for zipcode in zipcodes_by_city[city]:
        composite_scores[city][zipcode] = {}
        try:
            composite_scores[city][zipcode]['school'] = school[city][zipcode]
            if city == "new_york":
                print "School"
            composite_scores[city][zipcode]['pricing'] = pricing[city][zipcode]
            if city == "new_york":
                print "Pricing"
            composite_scores[city][zipcode]['crime'] = crime[city][zipcode]
            if city == "new_york":
                print "Crime"
            composite_scores[city][zipcode]['restaurants'] = restaurants[city][zipcode]
            if city == "new_york":
                print "Restaurants"
        except Exception as e:
            composite_scores[city].pop(zipcode)
            #composite_scores[city][zipcode]['school'] = -1
            continue
        # try:
        #     composite_scores[city][zipcode]['pricing'] = pricing[city][zipcode]
        # except Exception as e:
        #     composite_scores[city][zipcode]['pricing'] = -1
        # try:
        #     composite_scores[city][zipcode]['restaurants'] = restaurants[city][zipcode]
        # except Exception as e:
        #     composite_scores[city][zipcode]['restaurants'] = -1
        # try:
        #     composite_scores[city][zipcode]['crime'] = crime[city][zipcode]
        # except Exception as e:
        #     composite_scores[city][zipcode]['crime'] = -1

with open('normalized_data/composite_scores.json', 'w') as fp:
    json.dump(composite_scores, fp)




