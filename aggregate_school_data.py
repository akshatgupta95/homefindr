import json

with open('school_data.json') as data_file:
    cities = json.load(data_file)

aggregating_dict = {}
for city in cities:
    aggregating_dict[city] = {}
    for school in cities[city]:
        zipcode = school['zipcode']
        rating = school['rating']
        if rating == "No Review":
            continue
        if zipcode not in aggregating_dict[city]:
            aggregating_dict[city][zipcode] = []
        aggregating_dict[city][zipcode].append(school['rating'])

average_ratings_dict = {}
for city in aggregating_dict:
    average_ratings_dict[city] = {}
    for zipcode in aggregating_dict[city]:
        schools = map(int,aggregating_dict[city][zipcode])
        average_ratings_dict[city][zipcode] = (float(sum(schools))/len(schools))/10
        print average_ratings_dict[city][zipcode]

with open('aggregated_school_data.json', 'w') as fp:
    json.dump(average_ratings_dict, fp)
