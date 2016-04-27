from flask import Flask, render_template, request
import urllib2
from subprocess import Popen, PIPE
import json, time, pandas



app = Flask(__name__)

weights = [[1], [.6, .4], [.5, .35, .15], [.4, .3, .2, .1]]


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

    with open(city + "_comp.json", 'w') as f:
        json.dump(output_dict, f)


@app.route("/")
def main():
    # p = Popen([
    #         "curl", "-v", "-F",
    #         "file=@/Users/Chris/cs467/test/test.csv",
    #         "https://cmathew95.cartodb.com/api/v1/imports/?api_key=5dd7d4fbb908ce5cf73f33cb2d3c7e621bb7a8ca&create_vis=true"
    #         ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    #
    # item_queue_id = json.loads(p.stdout.readline())['item_queue_id']
    # time.sleep(10)

    # url = "https://cmathew95.cartodb.com/api/v1/imports/" + item_queue_id + "?api_key=5dd7d4fbb908ce5cf73f33cb2d3c7e621bb7a8ca"
    url = "https://cmathew95.cartodb.com/api/v1/imports/96800783-f93e-4081-b6e5-6b12f9b25d9a?api_key=5dd7d4fbb908ce5cf73f33cb2d3c7e621bb7a8ca"
    r1 = urllib2.urlopen(url).read()
    vis_url = str(json.loads(r1)['visualization_id'])
    print(vis_url)
    return render_template("chicago.html", vis_url=vis_url)


@app.route("/process", methods=['POST'])
def process_form():
    dict = {}
    rankings = []
    priority_list = ["pricing", "schools", "crime", "restaurants"]
    for priority in priority_list:
        value = request.form[priority]
        if len(value) == 0:
            continue

        dict[value] = priority

    for i in range(1, len(dict) + 1):
        rankings.append(dict[str(i)])

    generate_composite_score("chicago", rankings)

    return "Hello"


if __name__ == "__main__":
    # p
    app.run(debug=True)
