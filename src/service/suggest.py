#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import regex
import math
import json
from unidecode import unidecode
default_uri = 'http://127.0.0.1:9411/'
from elasticsearch import Elasticsearch

esclient = Elasticsearch([os.environ.get('elastic_url',default_uri)])

def query_suggestion (original, size=5):

	def format (el, add=None):
		vec = {"text": el["text"], "_score": el["_score"]}
		return vec


	hits, ids = [], []
	body = {
    "suggest": {
        "test-suggest" : {
            "prefix" : original,
            "completion" : {
                "field" : "suggest", 
                "size" : 5 
            }
        }
    }
}



	res = esclient.search(index="suggestions", body=body)["suggest"]["test-suggest"]
	res = res[0]["options"]

	for el in sorted([el for el in res], key=(lambda el: (-el['_score'])))[:size]:
		hits.append(format(el))
	return hits

if __name__ == "__main__":
	arg = str(' '.join(sys.argv[1:]))
	print(query_suggestion(str(arg)))



