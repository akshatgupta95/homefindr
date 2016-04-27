import json

weights = [[1],[.6,.4],[.5,.35,.15],[.4,.3,.2,.1]]

def generate_composite_score(city, rankings):
	multiples = weights[len(rankings)-1]

	with open('normalized_data/composite_scores.json') as f:
		agg_data = json.load(f)
		output_dict = {}
		output_dict[city] = {}

		for zipcode, obj in agg_data[city].iteritems():
			score = 0
			for i in range(len(rankings)):
				score += (multiples[i]*obj[rankings[i]])

			output_dict[city][zipcode] = score

	with open('composite_score_by_city.json', 'w') as f:
		json.dump(output_dict, f)


if __name__ == "__main__":
	rankings = ["crime", "school"]
	generate_composite_score("san_francisco", rankings)