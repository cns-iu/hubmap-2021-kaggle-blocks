import csv
import json
import os
import ssl
import sys
import urllib.request

TOKEN = sys.argv[1] if len(sys.argv) > 1 else None
HBM_LINK = 'https://hubmap-link-api.herokuapp.com/hubmap-datasets?format=jsonld'
if TOKEN:
    HBM_LINK += '&token=' + TOKEN

def make_ssl_work():
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

make_ssl_work()

# get HuBMAP IDs from CSV file
with open('kaggle_hubmap_ids.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    hubmap_ids = [ row['HuBMAP ID'] for row in reader ]

# get uuids for all hubmap hubmap_ids
iris = set()
for item in hubmap_ids:
    print(item)
    request = urllib.request.Request(
        'https://entity.api.hubmapconsortium.org/entities/' + item)
    if TOKEN:
        request.add_header('Authorization', 'Bearer ' + TOKEN)
    with urllib.request.urlopen(request) as url:
        response = json.loads(url.read().decode())
        if response:
            iris.add('https://entity.api.hubmapconsortium.org/entities/' + response['uuid'])

# go through JSON-LD and find uuids
with urllib.request.urlopen(HBM_LINK) as url:
    data = json.loads(url.read().decode())
    original_data = data['@graph']

    keep = set()
    found = set()
    for item in data['@graph']:
        for sample in item['samples']:
            if sample['@id'] in iris:
                keep.add(item['@id'])
                found.add(sample['@id'])    

            for dataset in sample['datasets']:
                if dataset['@id'] in iris:
                    keep.add(item['@id'])
                    found.add(dataset['@id'])

            for section in sample['sections']:
                if section['@id'] in iris:
                    keep.add(item['@id'])
                    found.add(section['@id'])

                for dataset in section['datasets']:
                    if dataset['@id'] in iris:
                        keep.add(item['@id'])
                        found.add(dataset['@id'])

                for subsample in section['samples']:
                    if subsample['@id'] in iris:
                        keep.add(item['@id'])
                        found.add(subsample['@id'])    

                    for dataset in subsample['datasets']:
                        if dataset['@id'] in iris:
                            keep.add(item['@id'])
                            found.add(dataset['@id'])

# remove samples without rui_location from JSON-LD
data['@graph'] = list(filter(lambda item: item['@id'] in keep, data['@graph']))

print(f'''
Original Donors: { len(original_data) }
Kaggle Donors: { len(data['@graph']) } { len(keep) }
Kaggle HBM IDs: { len(hubmap_ids) }
Kaggle UUIDs: { len(iris) }
Kaggle UUIDs Found: { len(found) }
''')

# save/overwrite JSON-LD file
open('rui_locations.jsonld', 'w').write(json.dumps(data, indent=2))
