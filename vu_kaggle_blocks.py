import json

def empty_jsonld():
  return {
    "@context": {
      "@base": "http://purl.org/ccf/latest/ccf-entity.owl#",
      "@vocab": "http://purl.org/ccf/latest/ccf-entity.owl#",
      "ccf": "http://purl.org/ccf/latest/ccf.owl#",
      "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
      "label": "rdfs:label",
      "description": "rdfs:comment",
      "link": {
        "@id": "rdfs:seeAlso",
        "@type": "@id"
      },
      "samples": {
        "@reverse": "has_donor"
      },
      "sections": {
        "@id": "has_tissue_section",
        "@type": "@id"
      },
      "datasets": {
        "@id": "has_dataset",
        "@type": "@id"
      },
      "rui_location": {
        "@id": "has_spatial_entity",
        "@type": "@id"
      },
      "ontologyTerms": {
        "@id": "has_ontology_term",
        "@type": "@id"
      },
      "thumbnail": {
        "@id": "has_thumbnail"
      }
    },
    "@graph": []
  }

def create_donor(block):
  rui_location = json.load(open(block['rui_location']))
  creator = rui_location['creator']
  date = rui_location['creation_date']
  age, sex = block['age'], block['sex']
  id = f'https://portal.hubmapconsortium.org/browse/{block["hbm_id"]}'

  annotations = rui_location['ccf_annotations']
  ref_organ = rui_location['placement']['target'].split('#')[1]
  if ref_organ.endswith('RightKidney'):
    annotations.append('http://purl.obolibrary.org/obo/UBERON_0013702')
    annotations.append('http://purl.obolibrary.org/obo/UBERON_0002113')
    annotations.append('http://purl.obolibrary.org/obo/UBERON_0004539')
  elif ref_organ.endswith('LeftKidney'):
    annotations.append('http://purl.obolibrary.org/obo/UBERON_0013702')
    annotations.append('http://purl.obolibrary.org/obo/UBERON_0002113')
    annotations.append('http://purl.obolibrary.org/obo/UBERON_0004538')
  else:
    annotations.append('http://purl.obolibrary.org/obo/UBERON_0013702')

  return {
    '@id': id + '#Donor',
    '@type': 'Donor',
    'label': f'{sex}, Age {age}',
    'description': f'Entered {date}, {creator}, TMC-Vanderbilt',
    'link': id,
    'age': age,
    'sex': sex,
    'consortium_name': 'HuBMAP',
    'provider_name': 'TMC-Vanderbilt',
    'provider_uuid': '73bb26e4-ed43-11e8-8f19-0a7c1eab007a',
    'samples': [
      {
        '@id': id + '#Sample',
        '@type': 'Sample',
        'sample_type': 'Tissue Block',
        'link': id,
        'label': f'Registered {date}, {creator}, TMC-Vanderbilt',
        'description': 'No description', #
        'section_count': 1, #
        'section_size': 0, #
        'section_units': 'millimeter',
        'rui_location': rui_location,
        'sections': [],
        'datasets': [
          {
            '@id': id + '#Dataset',
            '@type': 'Dataset',
            'label': f'Registered {date}, {creator}, TMC-Vanderbilt',
            'description': 'Data/Assay Types: PAS',
            'link': id,
            'technology': 'PAS',
            'thumbnail': 'assets/icons/ico-unknown.svg'
          }
        ]
      }
    ]
  }

blocks = []
with open('extra/vu_tissue_blocks/metadata.txt') as in_f:
    block = False

    for line in in_f:
        if 'UUID: ' in line:
            if block:
                blocks.append(block)

            block = {}
            ids = line.split()[2].split('_')
            block['hbm_id'] = ids[1]
            block['rui_location'] = f'extra/vu_tissue_blocks/{ids[0]}_{ids[1]}.json'

        if block:
            if line.startswith('A/S/R:'):
                age, sex, ethnicity = line.split()[1].split('/')
                block['age'] = int(age)
                block['sex'] = 'Male' if sex == 'M' else 'Female'
            if line.startswith('A, S, R:'):
                age, sex, ethnicity = line.split(
                    ':')[1].replace(',', '').split()
                block['age'] = int(age)
                block['sex'] = 'Male' if sex == 'M' else 'Female'
        else:
            print(line)

jsonld = empty_jsonld()
jsonld['@graph'] = list(map(lambda x: create_donor(x), blocks))

open('rui_locations.vu.jsonld', 'w').write(json.dumps(jsonld, indent=2))
