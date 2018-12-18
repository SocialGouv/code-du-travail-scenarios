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

def query_scenario (original, vec=None, size=100):

	if vec is None: vec = []

	def filtered (res):

		return True

	def format (el, add=None):
		res = {
			"code": el["_source"]["code"],
			"vec": el["_source"]["vec"],
			"proba": el["_source"]["proba"],
			"_score": el["_score"]
		}
		return res


	hits, ids = [], []
	query = {
		"bool": {"should":[{"multi_match":{
			"fields" : ["vec"],
			"analyzer": "scenario_analyzer",
			"query": original, #test,  #val  + "~"
			#"phrase_slop": 10,
			"fuzziness": "AUTO"
	}}]}}

	body={"query": query, "size": max(size, 20)}
	res = esclient.search(index="scenarios", doc_type="scenarios", body=body)['hits']
	for el in sorted([el for el in res['hits'] if filter], key=(lambda el: (-el['_score']))):
		if filtered(el) and el["_source"]['code'] not in ids:
			ids.append(el["_source"]['code'])
			hits.append(format(el))

	return hits

if __name__ == "__main__":
	arg = str(' '.join(sys.argv[1:]))
	print(query_scenario(str(arg)))



