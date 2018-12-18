#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import pickle
import math
from unidecode import unidecode
import pandas as pd
from numpy import array
from json.decoder import JSONDecodeError
from elasticsearch import Elasticsearch
from elasticsearch import helpers

default_uri = "http://127.0.0.1:9411/"

"""

Ensure index, types and mappings creation 

"""


def init_scenarios():

	esclient = Elasticsearch([os.environ.get("elastic_url",default_uri)])
	indices = esclient.indices

	if not indices.exists(index="scenarios"):
		indices.create(index="scenarios")

	with open("mappings/synonyms.json", "r") as file:
		synonyms = json.load(file)

	if "analysis" not in indices.get(index="scenarios")["scenarios"]["settings"]["index"] or "scenario_analyzer" not in indices.get(index="scenarios")["scenarios"]["settings"]["index"]["analysis"]["analyzer"]:
		indices.close(index="scenarios")
		
		settings = {
		  "settings": {
		  "analysis": {
		    "filter": {
		    "synonym_filter": {
          "type": "synonym", 
          "synonyms": synonyms
        },
		      "french_elision": {
		        "type": "elision",
		        "articles_case": True,
		        "articles": [
		          "l",
		          "m",
		          "t",
		          "qu",
		          "n",
		          "s",
		          "j",
		          "d",
		          "c",
		          "jusqu",
		          "quoiqu",
		          "lorsqu",
		          "puisqu"
		        ]
		      },
		      "french_stop": {
		        "type": "stop",
		        "stopwords": "_french_"
		      },
		      "french_stemmer": {
		        "type": "stemmer",
		        "language": "light_french"
		      }
		    },
		    "analyzer": {
		      "scenario_analyzer": {
		        "tokenizer": "icu_tokenizer",
		        "filter": [
		          "french_elision",
		          "lowercase",
            	  "synonym_filter",
		          "french_stop",
		          "icu_folding"
		        ]
		      }
		    }
		  }
		}}
		indices.put_settings(index="scenarios", body=settings)
		indices.open(index="scenarios")

	with open("mappings/scenarios.json", "r") as mapping:
		indices.put_mapping(index="scenarios", doc_type="scenarios", body=json.load(mapping))


def fill_scenarios():

	def build_json (row):
		res = {
			"code": row["code"],
			"proba": row["Probabilité (/10)"]/10,
			"vec": []
		}
		res["proba"] = res["proba"] if not math.isnan(res['proba']) else 5
		for el in ["sousthème_1", "sousthème_2", "sousthème_3", "sousthème_4", "sousthème_5", "sousthème_6"]:
			if type(row[el]) == str and len(row[el]) > 0 :
				res["vec"].append(row[el])
		full = {
			"_index": "scenarios",
			"_type": "scenarios",
			"_id": row["code"],
			"_source": res
		}

		scenarios.append(full)


	df = pd.read_csv("../data/scenario.csv")
	tree = df[["code", "sousthème_1", "sousthème_2", "sousthème_3", "sousthème_4", "sousthème_5", "sousthème_6", "Probabilité (/10)"]]
	print(tree)

	scenarios = []

	df.apply(lambda row: build_json (row),axis=1)

	with open("../data/scenario_bulk.json", "w+") as new_file:
		json.dump(scenarios, new_file)

def upload_scenarios():

	with open("../data/scenario_bulk.json") as data_formatted:
	    data_formatted = json.load(data_formatted)

	esclient = Elasticsearch([os.environ.get("elastic_url",default_uri)])

	helpers.bulk(esclient, data_formatted)

if __name__ == "__main__":

	init_scenarios()
	fill_scenarios()
	upload_scenarios()


