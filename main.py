import collections

from flask import Flask, request, jsonify, make_response
from collections import OrderedDict
import requests
import json
app = Flask(__name__)

# Python list
dishes_list = [{}]

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
    # "None" means no errors in the previous checks.
    if response is not None:
        return response

    dish_name = data['name']
    dishes_list.append(dish_name)
    index = dishes_list.index(dish_name)

    return make_response(jsonify(index), 201)


@app.get('/dishes')
def get_json_all_dishes():
    combined_json = {}
    for index, dish_name in enumerate(dishes_list):
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(dish_name)
        response = requests.get(api_url, headers={'X-Api-Key': 'j5GLOwZ/nqeLvuK8bUn00w==0p7X3UH2sBwzMYva'})
        json_dict = response.json()
        if json_dict:
            combined_json[str(index)] = show_only_requested_json_keys(json_dict[0])
    return json.dumps(combined_json, indent=4)

@app.get('/dishes/<id_or_name>')
def get_specific_dish(id_or_name):
    if "0" <= str(id_or_name[0]) <= "9":
        return get_dish_by_id(id_or_name)
    else:
        return get_dish_by_name(id_or_name)

@app.get('/dishes/')
def name_or_id_not_specified_GET():
    return make_response(jsonify(-1), 400)

@app.delete('/dishes/')
def name_or_id_not_specified_DELETE():
    return make_response(jsonify(-1), 400)

@app.delete('/dishes/<id_or_name>')
def delete_specific_dish(id_or_name):
    if "0" <= str(id_or_name[0]) <= "9":
        return delete_dish_by_id(id_or_name)
    else:
        return delete_dish_by_name(id_or_name)


def delete_dish_by_id(dish_id):
    dish_id = int(dish_id)
    if dish_id == 0 or dish_id >= len(dishes_list) or dishes_list[dish_id] == {}:
        return make_response(jsonify(-5), 404)
    else:
        # del dishes_list[dish_id]
        dishes_list[dish_id] = {}
        return jsonify(dish_id)

def delete_dish_by_name(dish_name):
    try:
        index_of_dish = dishes_list.index(dish_name)
        # del dishes_list[index_of_dish]
        dishes_list[index_of_dish] = {}
        return jsonify(index_of_dish)
    except ValueError:
        return make_response(jsonify(-5), 404)


def get_dish_by_id(dish_id):
    dish_id = int(dish_id)
    if dish_id == 0 or dish_id >= len(dishes_list) or dishes_list[dish_id] == {}:
        return make_response(jsonify(-5), 404)
    else:
        dictforjson = get_dictionary_for_json(dish_id)
        return json.dumps(dictforjson, indent=4)

def get_dish_by_name(name):
    try:
        index_of_dish = dishes_list.index(name)
        dictforjson = get_dictionary_for_json(index_of_dish)
        return json.dumps(dictforjson, indent=4)
    except ValueError:
        return make_response(jsonify(-5), 404)

def get_dictionary_for_json(dish_index):
    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(dishes_list[dish_index])
    response = requests.get(api_url, headers={'X-Api-Key': 'j5GLOwZ/nqeLvuK8bUn00w==0p7X3UH2sBwzMYva'})
    json_dict = response.json()
    return show_only_requested_json_keys(json_dict[0])

def show_only_requested_json_keys(original_dict):
    new_dict = OrderedDict()
    index_of_dish = dishes_list.index(original_dict["name"])
    new_dict["name"] = original_dict["name"]
    new_dict["ID"] = index_of_dish
    new_dict["cal"] = original_dict["calories"]
    new_dict["size"] = original_dict["serving_size_g"]
    new_dict["sodium"] = original_dict["sodium_mg"]
    new_dict["sugar"] = original_dict["sugar_g"]

    return new_dict


app.run(host="localhost", port="8496", debug=True)
