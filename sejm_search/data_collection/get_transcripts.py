import requests
from requests.exceptions import MissingSchema
import json
import time
import random

from data_collection.get_info import read_json_from_file, write_json_to_file


def get_html_data(url):
    response = requests.get(url)
    return response.text


# Let's get the transcripts
def get_transcripts(sittings_info):

    transcripts = {}

    for term in sittings_info:
        transcripts[term] = transcripts.get(term, {})
        print(term)

        for committee in sittings_info[term]:
            print(committee)
            sittings_count = 1 #len(sittings_info[term][committee])
            transcripts[term][committee] = transcripts[term].get(committee, {})

            for sitting_num in range(1, sittings_count + 1):
                sitting_transcript_url = f"https://api.sejm.gov.pl/sejm/term{term}/committees/{committee}/sittings/{sitting_num}/html"
                # some form of checking if transcript already present in the data probably needed here
                try: # being extra safe
                    transcript_text = get_html_data(sitting_transcript_url)
                    transcripts[term][committee][sitting_num] = transcripts[term][committee].get(sitting_num, transcript_text)
                    time.sleep(random.random() * 2) # random delay
                except MissingSchema as e:
                    print(e)
    
    return transcripts
