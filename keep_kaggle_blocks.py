import urllib
import json
import csv
import os
import ssl


def main():

    # get HuBMAP IDs from CSV file
    hubmap_ids = []
    with open('kaggle_hubmap_ids.csv', newline='') as csv_file:
        for line in csv_file:
            if 'HBM' in line:
                start = line.find('HBM')
                end = len(line)
                hubmap_ids.append(line[start:end].strip())
    
    # get uuids for all hubmap hubmap_ids
    uuids = []
    counter = 0
    for item in hubmap_ids:
        with urllib.request.urlopen("https://entity.api.hubmapconsortium.org/entities/" + item) as url:
            response = json.loads(url.read().decode())
            if response:
                # print('received')
                counter = counter + 1
                uuids.append(response['uuid'])

    # create mapping from hubmap_ids to uuids
    look_up_dict = {}
    for i in range(0,len(hubmap_ids)):
        look_up_dict[hubmap_ids[i]] = uuids[i]

# go through JSON-LD and find uuids
    with urllib.request.urlopen("https://hubmap-link-api.herokuapp.com/hubmap-datasets?format=jsonld") as url:
        data = json.loads(url.read().decode())

        sample_ids = []
        for item in data['@graph']:
            for sample in item['samples']:
                for dataset in sample['datasets']:
                    for key in look_up_dict:
                        if look_up_dict[key] in dataset['@id']:
                            sample_ids.append(sample['@id'])





# remove samples without rui_location from JSON-LD
        for item in data['@graph']:

            for sample in item['samples']:
                if sample['@id'] not in sample_ids:
                    pass
                    # del

            print(len(item['samples']))


# save/overwrite JSON-LD file

def make_ssl_work():
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

make_ssl_work()
main()





# with open('kaggle_hubmap_ids.csv', mode='r') as infile:
#     reader = csv.reader(infile)
#     with open('coors_new.csv', mode='w') as outfile:
#         writer = csv.writer(outfile)
#         mydict = {rows[0]: rows[1] for rows in reader}
        # print(mydict)
        # print(mydict.keys)
    # for line in csvfile:
    #     print(line)
    # print(csvfile)

