# -*- coding: utf-8 -*-
"""
Created Dec 2018

@author: onogone
"""
import sys
from service.search import query_scenario
from service.fold import loop_create, Branche, Bouquet

def test (val, prevs=None, count=3, max_size=2):
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

    def print_question_information():

        question = ' >> '.join(prevs[-1]) if len(prevs) > 0 else ":"
        print("\n=====\n\n" + question + "\n")

        for i, el in enumerate(suggestions):
            print(i, '|', el.vec[-1], el.size, el.level, el.weight_components)

    def ask_question():
        print_question_information()

        answer = None
        while answer not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '=', 'q']:
            answer = input("\n||||| Quelle sélection ? ('+' pour davantage, '=' pour précédent, 'q' pour quitter) >> ")

        if answer == 'q': return []
        if answer == '+':
            return test(val, prevs, 10, max_size)
        if answer == '=':
            return test(val, prevs[:-1], 3, max_size)

        return prevs + [suggestions[int(answer)].vec]

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
    branches = list(filter(lambda el : len(prevs) == 0 or len([prev for prev in prevs if el.contains(prev)]) > 0, branches))

    print(branches)
    # create bouquets, loop to generate rated suggestions
    suggestions = loop_create(branches, max_size=max_size, min_level=min_level)
    # filter prevs out of suggestions 
    suggestions = list(filter(lambda el: len([prev for prev in prevs if el.vec == prev]) == 0, suggestions))

    # limit to count
    suggestions = suggestions[:count]

    if len(suggestions) == 0: return returnee()

    prevs = ask_question()
    if type(prevs) == dict: return prevs
    if len(prevs) == 0: return returnee()

    return test(val, prevs, max_size=max_size)

def many():
    while True:
        print('\n=============\n===== * =====\n=============\n')
        arg = input('Quelle recherche faites-vous ? >> ')
        res = test(str(arg))
        for el in res:
            print(el, res[el])


if __name__ == "__main__":
    many()
    #arg = str(' '.join(sys.argv[1:]))
    
