
import requests
from requests.exceptions import MissingSchema
import json
import time
import random
import pandas as pd
import os



# Helper fuctions

def get_json_data(url):
    response = requests.get(url)
    return response.json()

def read_json_from_file(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data

def write_json_to_file(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ========= TERMS ========= 
# Get info on parliamentary terms

def get_term_info_from_api(from_, to):
    terms = []
    for term_num in range(from_, to):
        url = f"https://api.sejm.gov.pl/sejm/term{term_num}"
        data = get_json_data(url)
        terms.append(data)
    
    return terms

# ========= COMMITTEES =========
# Get information on all committees from all terms
def get_committees_info_from_api():
    committees_info = []

    for term in range(1, 11):
        committees_url = f"https://api.sejm.gov.pl/sejm/term{term}/committees"
        committees = get_json_data(committees_url)
        committees_info.append(committees)

    #with open("data/committees_info.json", "w") as f:
    #    json.dump(all_committees, f)

    all_committee_codes = [c["code"] for t in committees_info for c in t]
    unique_codes = list(set(all_committee_codes))
    return committees_info, unique_codes

# Creating a log of urls tried

def get_urls_tried():
    try:
        urls_tried = pd.read_csv("data/urls_tried.csv", header=None, names=["url"]) 
        urls_tried = urls_tried["url"].tolist()
    except FileNotFoundError:
        print("File not found. Returning an emtpy list.")
        return []
    return urls_tried

# Get committee info data from the API
def get_sittings_info():

    sittings_info = {}

        
    for term in range(10, 11): # there are 10 terms
        sittings_info[term] = sittings_info.get(term, {}) 
        for code in unique_codes[10:40]:

            if not sittings_info[term].get(code, False): # if committee not already in the term dict...
                # The data is returned at once for all sittings of a given committee    
                url = f"https://api.sejm.gov.pl/sejm/term{term}/committees/{code}/sittings"
                try:
                    data = get_json_data(url)
                    try:
                        data[0]["code"] = code # insert committee code to data 
                        data[0]["term"] = term # insert term to data
                        sittings_info[term][code] = data
                    except IndexError as e:
                        print(f"{e}: There's no {code} committee in term {term}")
                        urls_tried.append(url) # I still log the url
                except MissingSchema as e:
                    print(e)
                time.sleep(random.random() * 2) # just in case
                urls_tried.append(url)

    # Write urls_tried to a csv file:
    with open("data/urls_tried.csv", "w") as f:
        for url in urls_tried:
            f.write(url + "\n")

    # Save sittings_info to a json file
    return write_json_to_file(path="data/sittings_info.json")
