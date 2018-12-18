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


def init_suggestions():

	esclient = Elasticsearch([os.environ.get("elastic_url",default_uri)])
	indices = esclient.indices

	if not indices.exists(index="suggestions"):
		indices.create(index="suggestions")

	with open("mappings/suggestions.json", "r") as mapping:
		indices.put_mapping(index="suggestions", doc_type="suggestions", body=json.load(mapping))


def fill_suggestions():

	def build_json (i, el):

		full = {
			"_index": "suggestions",
			"_type": "suggestions",
			"_id": str(i),
			"_source": {"suggest":el}
		}

		suggestions.append(full)


	with open("../data/expression.json") as data_formatted:
	    data_formatted = json.load(data_formatted)

	suggestions = []
	for i, el in enumerate(data_formatted): build_json(i, el)

	with open("../data/expression_bulk.json", "w+") as new_file:
		json.dump(suggestions, new_file)

def upload_suggestions():

	with open("../data/expression_bulk.json") as data_formatted:
	    data_formatted = json.load(data_formatted)

	esclient = Elasticsearch([os.environ.get("elastic_url",default_uri)])

	helpers.bulk(esclient, data_formatted)

if __name__ == "__main__":

	init_suggestions()
	fill_suggestions()
	upload_suggestions()


