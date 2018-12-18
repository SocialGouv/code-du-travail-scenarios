#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created Dec 2018

@author: onogone
"""

import argparse
import logging
import tornado.ioloop
import tornado.web
import json
import sys

from service.search import query_scenario
from service.suggest import query_suggestion
from service.fold import loop_create, Branche, Bouquet

def get_scenarios (val, prevs=None, count=10, max_size=2):
    """
    count: displays the maximum number of suggested tags that the program suggests
    max_size: if number of branches inside a suggestion is smaller, stop there
    prevs: list of previously selected suggestion vecs used as a filter, ie : [['Contrat', 'Contrat de Travail'], ...]
    """

    def returnee ():
        """
        This function formats the output
        """
        if len(prevs) == 0: return Bouquet([], branches).export()
        return Bouquet(prevs[-1], branches).export()

    # adding previously selected suggestions
    if prevs is None or len(prevs) == 0:
        prevs = []
        min_level = 0
    else:
        min_level=len(prevs[-1])

    # run the elastic search query
    queried = query_scenario(val)
    if len(queried) == 0 : return {}
    max_score = max([el["_score"] for el in queried])

    # create all branches from search results
    branches = [Branche(el["code"], el["vec"], score=el["_score"]/max_score, proba=el["proba"]) for el in queried]
    # filter all branches to match the prevs
    branches = list(filter(lambda el : len([prev for prev in prevs if el.contains(prev)]) > 0, branches))
    logging.info(f'{[el.vec for el in branches]}')

    # create bouquets, loop to generate rated suggestions
    suggestions = loop_create(branches, max_size=max_size, min_level=min_level)
    # filter prevs out of suggestions 
    suggestions = list(filter(lambda el: len([prev for prev in prevs if el.vec == prev]) == 0, suggestions))

    # limit to count
    suggest = {}
    for el in suggestions[:count]:
        suggest[el.vec[-1]] = {"vec": el.vec, "score": el.weight_components}

    returned = returnee()

    return {"suggestions": suggest, "branches": returned}

class SuggestHandler(tornado.web.RequestHandler):

    def post(self):
        req = tornado.escape.json_decode(self.request.body)
        search = req.get("search", None)
        count = req.get("count", 5)

        if search is None:
            logging.error(f'Cannot parse search : {req}')
            self.set_status(400)

        try:
            res = query_suggestion(search, size=count)
            self.write({"results":res})
        except Exception as e:
            logging.error(f'No result found : {e}')
            self.write({"results":[]})

class ScenarioHandler(tornado.web.RequestHandler):

    def post(self):
        req = tornado.escape.json_decode(self.request.body)
        suggestions = req.get("suggestions", [[]])
        search = req.get("search", None)
        count = req.get("count", 10)
        max_size = req.get("max_size", 2)

        if search is None:
            logging.error(f'Cannot parse search : {req}')
            self.set_status(400)

        try:
            res = get_scenarios(search, prevs=suggestions, count=count, max_size=max_size)
            self.write(res)
        except Exception as e:
            logging.error(f'No result found : {e}')
            self.write({"suggestions": {}, "branches": {}})

def make_app(args):
    return tornado.web.Application([
        (r"/suggest/", SuggestHandler),
        (r"/scenario/", ScenarioHandler)
    ])

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8888)
    args = parser.parse_args()

    app = make_app(args)
    app.listen(args.port)
    logging.info(f'Server is up and running on port {args.port}')
    tornado.ioloop.IOLoop.current().start()
