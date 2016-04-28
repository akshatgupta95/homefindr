from flask import Flask, render_template, request
import urllib2
from subprocess import Popen, PIPE
import json, time
import pandas as pd

app = Flask(__name__)

weights = [[1], [.6, .4], [.5, .35, .15], [.4, .3, .2, .1]]
thresholds = []

global_dict = {"restaurants": {
    "san_francisco": "402a1b54-0cc8-11e6-a0df-0ecd1babdde5",
    "chicago": "6482a8dc-0cc7-11e6-9822-0e787de82d45",
    "boston": "fac45e4e-0cc7-11e6-b75f-0e3ff518bd15",
    "new_york": "1ad71b58-0cc9-11e6-ad91-0ea31932ec1d"},
                  "school": {
                      "new_york": "54f63588-0cc1-11e6-88fd-0e3a376473ab",
                      "chicago": "fca8fd5c-0cc0-11e6-8f9e-0e8c56e2ffdb",
                      "san_francisco": "dd5720dc-0cc0-11e6-b4ac-0ef24382571b",
                      "boston": "7f06dfae-0cc0-11e6-96ed-0e31c9be1b51"}
              }

long_lat_mapping = {"chicago": [41.8781, -87.6298], "new_york": [40.7128, -74.0059], "san_francisco": [37.7749, -122.4194], "boston": [42.3601, -71.0589]}

def json_to_csv(city):
    config = json.loads(open('./composite_scores.json').read())
    zips = [map(str, config[key].keys()) for key in config.keys()]

    sf = pd.read_csv('./San_francisco_toappend.csv')
    sf = sf.rename(columns={'zcta5ce10': 'zip_code'})

    boston = pd.read_csv('./Boston_toappend.csv')
    boston = boston.rename(columns={'zcta5ce10': 'zip_code'})

    chicago = pd.read_csv('./chicago_toappend.csv')
    chicago = chicago.rename(columns={'zcta5ce10': 'zip_code'})

    ny = pd.read_csv('./new_york_toappend.csv')
    ny = ny.rename(columns={'zcta5ce10': 'zip_code'})

    city_dict = {"san_francisco": sf, "boston": boston, "chicago": chicago, "new_york": ny}
    return merge_by_city(city, city_dict[city])


def merge_by_city(city, city_df):
    city_comp = open("./" + city + "_comp.json").read()
    city_comp = json.loads(city_comp)
    print (city_comp)
    zips_city = map(int, city_comp[city].keys())
    zips_city_str = map(str, city_comp[city].keys())
    # zips_city = [curr_zip.zfill(5) for curr_zip in zips_city if city=='boston']
    # zips_city = city_comp[city].keys()
    scores_city = map(float, [city_comp[city][str(zip_city)] for zip_city in zips_city_str])
    city_df_zipcode = pd.DataFrame({'zip_code': zips_city, "score": scores_city})
    # city_df_zipcode['zip_code'] = city_df_zipcode['zip_code'].astype(str)
    city_score_added = pd.merge(city_df, city_df_zipcode, how="outer", on='zip_code')
    filename_csv = city + "_scored_added.csv"
    city_score_added.to_csv(filename_csv)

    scores_city = sorted(scores_city)
    print(scores_city)
    sandeep = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
    global thresholds
    if (city=="san_francisco"):
        scores_city = scores_city[:-1]

    thresholds = [list[0] for list in sandeep(scores_city, len(scores_city)/6)]
    print (thresholds)

    return get_viz_url(filename_csv)


def get_viz_url(filename_csv):
    file_to_curl = "file=@" + filename_csv
    p = Popen([
        "curl", "-v", "-F",
        file_to_curl,
        "https://cmathew95.cartodb.com/api/v1/imports/?api_key=5dd7d4fbb908ce5cf73f33cb2d3c7e621bb7a8ca&create_vis=true"
    ], stdin=PIPE, stdout=PIPE, stderr=PIPE)

    item_queue_id = json.loads(p.stdout.readline())['item_queue_id']
    time.sleep(10)

    url = "https://cmathew95.cartodb.com/api/v1/imports/" + item_queue_id + "?api_key=5dd7d4fbb908ce5cf73f33cb2d3c7e621bb7a8ca"
    # url = "https://cmathew95.cartodb.com/api/v1/imports/96800783-f93e-4081-b6e5-6b12f9b25d9a?api_key=5dd7d4fbb908ce5cf73f33cb2d3c7e621bb7a8ca"
    r1 = urllib2.urlopen(url).read()
    vis_url = str(json.loads(r1)['visualization_id'])
    return vis_url

    # return render_template("chicago.html", vis_url=vis_url)


def generate_composite_score(city, rankings):
    multiples = weights[len(rankings) - 1]

    with open('composite_scores.json') as f:
        agg_data = json.load(f)
        output_dict = {}
        output_dict[city] = {}

        for zipcode, obj in agg_data[city].iteritems():
            score = 0
            for i in range(len(rankings)):
                score += (multiples[i] * obj[rankings[i]])

            output_dict[city][zipcode] = score
    file_name = city + "_comp.json"

    with open(file_name, 'w') as f:
        json.dump(output_dict, f)


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/city/<city>")
def choose_city(city):
    city = str(city)
    city_name = '_'.join(city.lower().split(" "))
    print(city_name)
    return render_template("pre_city.html", utility_dict = {"city_name": city_name, "long": long_lat_mapping[city_name][1], "lat": long_lat_mapping[city_name][0], "viz_url": global_dict["restaurants"][city_name]})


@app.route("/process", methods=['POST'])
def process_form():
    city_name = request.form["city_name"]
    print ("________________________")
    dict = {}
    rankings = []
    priority_list = ["pricing", "school", "crime", "restaurants"]
    for priority in priority_list:
        value = request.form[priority]
        if (len(value) == 0):
            continue
        dict[value] = priority
    for i in range(1, len(dict) + 1):
        rankings.append(dict[str(i)])

    viz_url = ""
    school_restaurants = False
    dots_or_choropleths = ""
    if (len(rankings) == 1):
        if ("school" in rankings or "restaurants" in rankings):
            key = rankings[0]
            viz_url = global_dict[key][city_name]
            dots_or_choropleths = "dots"
            school_restaurants = "school" if ("school" in rankings) else "rests"
        else:
            generate_composite_score(city_name, rankings)
            viz_url = json_to_csv(city_name)
            dots_or_choropleths = "choropleth"
    else:
        generate_composite_score(city_name, rankings)
        viz_url = json_to_csv(city_name)
    print ("VIZ URL", viz_url)
    utility_dict = {"city_name": city_name, "long": long_lat_mapping[city_name][1], "lat": long_lat_mapping[city_name][0], "viz_url" : viz_url, "type" : dots_or_choropleths, "is_school": school_restaurants}
    polygon_fills = ["#D6301D", "#E31A1C", "#FC4E2A", "#FD8D3C", "#FEB24C", "#FED976", "#FFFFB2"]
    return render_template("post_city.html", utility_dict=utility_dict, thresholds=reversed(thresholds), polygon_fills=polygon_fills)

if __name__ == "__main__":
    app.run(debug=True)
