import csv
import json
import os
import ssl
import sys
import urllib.request

# TOKEN = sys.argv[1] if len(sys.argv) > 1 else None
TOKEN = 'Ag78dKQOgjdV7xwpBd3Q6G37P98mJKGWQ3Nk8v0DdmPyYmMG5dSWCXknQmgqXbB5eEwvX8WNGV0a1zszkEEobhadm3'
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
    hubmap_ids = [row['HuBMAP ID'] for row in reader]

# get uuids for all hubmap hubmap_ids
iris = set()
for donor in hubmap_ids:
    request = urllib.request.Request(
        'https://entity.api.hubmapconsortium.org/entities/' + donor)
    if TOKEN:
        request.add_header('Authorization', 'Bearer ' + TOKEN)
    with urllib.request.urlopen(request) as url:
        response = json.loads(url.read().decode())
        if response:
            iris.add(
                'https://entity.api.hubmapconsortium.org/entities/' + response['uuid'])

# go through JSON-LD and find uuids
with urllib.request.urlopen(HBM_LINK) as url:
    data = json.loads(url.read().decode())
    original_data = data['@graph']
    keep = set()
    found = set()
    for donor in data['@graph']:
        samples_to_keep = set()
        for sample in donor['samples']:
            if sample['@id'] in iris:
                keep.add(donor['@id'])
                found.add(sample['@id'])
                samples_to_keep.add(sample['@id'])

            for dataset in sample['datasets']:
                if dataset['@id'] in iris:
                    keep.add(donor['@id'])
                    found.add(dataset['@id'])
                    samples_to_keep.add(sample['@id'])

            for section in sample['sections']:
                if section['@id'] in iris:
                    keep.add(donor['@id'])
                    found.add(section['@id'])
                    samples_to_keep.add(sample['@id'])

                for dataset in section['datasets']:
                    if dataset['@id'] in iris:
                        keep.add(donor['@id'])
                        found.add(dataset['@id'])
                        samples_to_keep.add(sample['@id'])

                for subsample in section['samples']:
                    if subsample['@id'] in iris:
                        keep.add(donor['@id'])
                        found.add(subsample['@id'])
                        samples_to_keep.add(sample['@id'])

                    for dataset in subsample['datasets']:
                        if dataset['@id'] in iris:
                            keep.add(donor['@id'])
                            found.add(dataset['@id'])
                            samples_to_keep.add(sample['@id'])

        donor['samples'] = list(filter(lambda sample: sample['@id'] in samples_to_keep, donor['samples']))

# remove samples without rui_location from JSON-LD
data['@graph'] = list(filter(lambda donor: donor['@id'] in keep, data['@graph']))

print(f'''
Original Donors: { len(original_data) }
Kaggle Donors: { len(data['@graph']) } { len(keep) }
Kaggle HBM IDs: { len(hubmap_ids) }
Kaggle UUIDs: { len(iris) }
Kaggle IDs Kept: {len(keep) }
Kaggle UUIDs Found: { len(found)}
''')

# save/overwrite JSON-LD file
open('rui_locations.jsonld', 'w').write(json.dumps(data, indent=2))
