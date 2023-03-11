import json

from flask import Flask, request, jsonify, make_response
import requests
import urllib.parse

app = Flask(__name__)

# Python list
dishes_list = []

def check_if_name_exists_in_list(name):
    if name in dishes_list:
        return True
    return False

def check_if_ninjas_recognize_name(dish_name):
    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(dish_name)
    response = requests.get(api_url, headers={'X-Api-Key': 'j5GLOwZ/nqeLvuK8bUn00w==0p7X3UH2sBwzMYva'})
    json_dict = response.json()
    if response.status_code == requests.codes.ok:
        if len(json_dict) > 0 and "name" in json_dict[0] and json_dict[0]["name"] == dish_name:
            return True
    return False



def check_for_errors(data):
    # Request content-type is not application/json
    content_type = request.headers.get("Content-Type")
    if content_type != 'application/json':
        return make_response(jsonify(0), 415)

    # Name parameter was not specified
    if "name" not in data:
        output = make_response(jsonify(-1), 400)
        return output

    # That dish of given name already exists
    name_exists_in_list = check_if_name_exists_in_list(data['name'])
    if name_exists_in_list is True:
        output = make_response(jsonify(-2), 400)
        return output

    # API was not reachable, or some server error
    api_url = 'https://api.api-ninjas.com/v1/nutrition'
    response = requests.get(api_url, headers={'X-Api-Key': 'j5GLOwZ/nqeLvuK8bUn00w==0p7X3UH2sBwzMYva'})
    if response.status_code // 100 != 2 and response.status_code // 100 != 3 and response.status_code // 100 != 4:
        return make_response(jsonify(-4), 400)

    # Ninjas API doesn't recognize dish name
    name_exists_in_ninjas_api = check_if_ninjas_recognize_name(data['name'])
    if name_exists_in_ninjas_api is False:
        output = make_response(jsonify(-3), 400)
        return output

    return None

@app.post('/dishes')
def add_dish():
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json':
        return make_response(jsonify(0), 415)
    data = request.get_json()
    response = check_for_errors(data)
    if response is not None:
        return response
    dish_name = data['name']
    dishes_list.append(dish_name)
    index = dishes_list.index(dish_name)

    return make_response(jsonify(index), 201)


@app.get('/dishes')
def get_json_all_dishes():
    # Scan the array, and for every name in it - get details from ninjasAPI and add it to a json file.
    # At the end, return the json file.
    combined_json = {}
    for index, dish_name in enumerate(dishes_list):
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(dish_name)
        response = requests.get(api_url, headers={'X-Api-Key': 'j5GLOwZ/nqeLvuK8bUn00w==0p7X3UH2sBwzMYva'})
        json_dict = response.json()
        combined_json[str(index)] = json_dict[0]
    return json.dumps(combined_json, indent=4)


app.run(host="localhost", port="8496", debug=True)
