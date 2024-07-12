
import json
import requests
import pandas as pd

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Get info on MPs and save to files"

    def handle(self, *args, **options):

        all_mps = []
        current_term = 10
        # Getting a list of MPs for every term
        for  term in range(1, current_term + 1):
            url = f"https://api.sejm.gov.pl/sejm/term{term}/MP"
            response = requests.get(url)
            all_mps.append(response.json())
        
        # Adding term to every MP dict
        for term in range(1, len(all_mps)+1):
            for mp in all_mps[term-1]:
                mp["term"] = term
        
        # Getting a flast list of all MP dicts
        mps_flat = [mp for term in all_mps for mp in term]
        df = pd.DataFrame.from_dict(mps_flat)
        unique_mps = df[["firstName", "secondName", "lastName", "birthDate"]].drop_duplicates() # firstName + secondName + lastName + birthDate
        
        duplicates = unique_mps[unique_mps.duplicated(['firstName', 'secondName', 'birthDate'], keep=False)]       
                
        print(duplicates)

        # Remove duplicates from unique_mps
        c1 = (unique_mps['lastName'] == "Nowina Konopka") & (unique_mps['birthDate'] == '1938-05-27')
        c2 = (unique_mps['lastName'] == "Schmidt-Rodziewicz") & (unique_mps['birthDate'] == '1978-11-11')
        c3 = (unique_mps['lastName'] == "Gąsior-Marek") & (unique_mps['birthDate'] == '1983-12-17')

        unique_mps = unique_mps[~(c1 | c2 | c3)]
        
        unique_mps = unique_mps.to_dict('records')
        ###

        # Recode flat_mps
        def recode_mps_flat(mp):
            if mp.get("lastName") == "Nowina Konopka":
                mp["lastName"] = "Nowina-Konopka"
            if mp.get("lastName") == "Schmidt-Rodziewicz":
                mp["lastName"] = "Schmidt"
            if mp.get("lastName") == "Gąsior-Marek":
                mp["lastName"] = "Marek"
            return mp
        
        mps_flat = [recode_mps_flat(mp) for mp in mps_flat]
        ###

        with open("data_collection/data/mps_flat.json", "w") as f:
            json.dump(mps_flat, f, indent=4)

        with open("data_collection/data/unique_mps.json", "w") as f:
            json.dump(unique_mps, f, indent=4)
                    
        self.stdout.write(
            self.style.SUCCESS('MPs data saved to JSON files!')
        )
