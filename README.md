# How do I use this ?

## Example elasticsearch deployment including icu

```shell
docker build -t elastic-icu:0.0.1 src/mappings
docker run -d -p 127.0.0.1:9411:9200 elastic-icu:0.0.1
```

## Building and Using docker image for scenarios-poseidon API

### variables

elastic_url= #set elasticsearch adress (defaults to http://127.0.0.1:9411/)

### script

run.sh and test.sh both reload the data inside elastic_search, and create the index if it does not exist.

The data used for scenario is scenario.csv. It can have many columns, but these are necessary :

```csv
code	sousthème_1	sousthème_2	sousthème_3	sousthème_4	sousthème_5	sousthème_6	Probabilité (/10)
6600	Contrat de travail	Conseil de prud'hommes	Attributions	Compétence en raison de la matière			8
```

The data used for suggestion is expression.json. It contains this format :

```json
[
  {
    
      "input": "Rapports accords ou convention et lois",
      "weight": 5
    
  },
  {
    
      "input": "Détermination du salaire",
      "weight": 2
    
  },
  ...
]
```

!!! When re-running the upload of expression.json, do not use a file with fewer documents : old documents will remain in the index, because the bulk import won't erase some older documents.

This script starts the API as a daemon : 
```shell
docker build -t scenarios-poseidon:0.0.1 src
docker run --rm --network=host -v $PWD/data:/data -d scenarios-poseidon:0.0.1 sh run.sh
```

OR 

Testing the api whith an interactive interface whithin Command Line :
```shell
docker run --rm -ti --network=host -v $PWD/data:/data scenarios-poseidon:0.0.1 sh test.sh
```

### usage : scenarios

One route on POST, on :8888/scenario/
Body must be a JSON, including :
- search : string
- suggestions (optional) : [[string]], the history of suggestions that have been selected by a user (ex: [[
        "Santé Sécurité",
        "Lieux de travail"
      ],[
        "Santé Sécurité",
        "Opérations particulières"
      ]])
- count (optional) : int, defaults to 10, how many maximum suggestions are returned by the API
- max_size (optional) : int, defaults to 2, number of branches (gate that blocks the look for smaller clusters)

elastic_url= #set elasticsearch adress (defaults to http://127.0.0.1:9411/)

```shell
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"search":"rupture"}' \
  http://localhost:8888/scenario/
```

### usage : autocomplete

One route on POST, on :8888/suggest/

Body must be a JSON, including :
- search : string
- count (optional) : int, defaults to 5, how many maximum suggestions are returned by the API

```shell
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"search":"rupt", "count":5}' \
  http://localhost:8888/suggest/
```

Reply : {"results": [{"text": "Rupture abusive", "_score": 5.0}, {"text": "Rupture anticip\u00e9e", "_score": 5.0}, {"text": "Rupture contrat", "_score": 5.0}, {"text": "Rupture conventionnelle", "_score": 5.0}, {"text": "Rupture conventionnelle collective", "_score": 5.0}]}

# Examples ?

## One selected choice possible

The user looks for suggestions corresponding to a search for any word or sentence.

The API returns suggestions, inside "suggestions". "suggestions" is a dict, its keys are different suggestions. One suggestion is made of a "vec" (Sous-theme0, Sous-theme1, ... )  and a score.

The API also returns branches, inside "branches". "branches" is a dict, its keys are different branches. One branch is made of a full-length vec (Sous-theme0, Sous-theme1, ... ).

A user can select multiple suggestions by including their vec inside "suggestions" (a list of suggestions, so typed [[str]])

```shell
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"search":"rupture"}' \
  http://localhost:8888/scenario/
```

or (with options)

```shell
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"search":"rupture", "suggestions":[[]], "count": 10, "max_size": 2}' \
  http://localhost:8888/scenario/
```

returns :

```json
{
  "suggestions": {
    "Rupture de contrat à durée Indéterminée": {
      "vec": [
        "Contrat de travail",
        "Rupture de contrat à durée Indéterminée"
      ],
      "score": [
        0.16666666666666666,
        2.03876872195286,
        1.4158631586566761
      ]
    },
    "Contrat de travail": {...},
    ...
  },
  "branches": {
    "1700": [
      "Contrat de travail",
      "Rupture de contrat à durée Indéterminée",
      "Rupture conventionnelle individuelle"
    ],
    "2145": [
      "Contrat de travail",
      "Rupture de contrat à durée Indéterminée",
      "Rupture conventionnelle collective",
      "Principe"
    ],
    ...
  }
}
```

```shell
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"search":"rupture", "suggestions":[[
        "Contrat de travail",
        "Rupture de contrat à durée Indéterminée"
      ]]}' \
  http://localhost:8888/scenario/
```

```json
{
  "suggestions": {
    "Licenciement": {
      "vec": [
        "Contrat de travail",
        "Rupture de contrat à durée Indéterminée",
        "Licenciement"
      ],
      "score": [
        0.3333333333333333,
        1.6094379124341003,
        1.1845164180030645
      ]
    },
    "Rupture conventionnelle individuelle": {...},
    ...
  },
  "branches": {
    "1700": [
      "Contrat de travail",
      "Rupture de contrat à durée Indéterminée",
      "Rupture conventionnelle individuelle"
    ],
    "2145": [
      "Contrat de travail",
      "Rupture de contrat à durée Indéterminée",
      "Rupture conventionnelle collective",
      "Principe"
    ],
    ...
  }
}
```

## Severall selected choices

```shell
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"search":"entretien"}' \
  http://localhost:8888/scenario/
```

```json
{
  "suggestions": {
    "Santé Sécurité": {
      "vec": [
        "Santé Sécurité"
      ],
      "score": [
        0.0,
        0.8958797346140275,
        1.6295998320466483
      ]
    },
    "Lieux de travail": {
      "vec": [
        "Santé Sécurité",
        "Lieux de travail"
      ],
      "score": [
        0.16666666666666666,
        0.34657359027997264,
        1.891415644909568
      ]
    },
    "Equipement de travail": {
      "vec": [
        "Santé Sécurité",
        "Equipement de travail"
      ],
      "score": [
        0.16666666666666666,
        0.0,
        1.9674666593952281
      ]
    },
    "Contrat de travail": {
      "vec": [
        "Contrat de travail"
      ],
      "score": [
        0.0,
        0.6931471805599453,
        1.330288983245883
      ]
    },
    "Sécurité: Généralités": {
      "vec": [
        "Santé Sécurité",
        "Sécurité: Généralités"
      ],
      "score": [
        0.16666666666666666,
        0.34657359027997264,
        1.3711491252398829
      ]
    },
    "Emploi - Formation": {
      "vec": [
        "Emploi - Formation"
      ],
      "score": [
        0.0,
        0.34657359027997264,
        1.2949187597390752
      ]
    },
    "Opérations particulières": {
      "vec": [
        "Santé Sécurité",
        "Opérations particulières"
      ],
      "score": [
        0.16666666666666666,
        0.0,
        1.2850027925857592
      ]
    }
  },
  "branches": {
    "144600": [
      "Santé Sécurité",
      "Lieux de travail",
      "Lieux de Travail : Utilisation",
      "Sécurité des lieux de travail",
      "Dossier de maintenance"
    ],
    "130000": [
      "Santé Sécurité",
      "Equipement de travail",
      "Equipement de travail: Utilisation",
      "Utilisation, maintenance équipement de travail",
      "Utilisation, maintenance équipement de Travail"
    ],
    ...
  }
}
```

```shell
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"search":"entretien", "suggestions":[[
        "Santé Sécurité",
        "Lieux de travail"
      ],[
        "Santé Sécurité",
        "Opérations particulières"
      ]]}' \
  http://localhost:8888/scenario/
```