#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import copy
import math 

########## DEFINITIONS

class Branche:
	def __init__(self, code, vec, score=0, proba=0):
		self.code = code
		self.vec = vec
		self.score = score
		self.proba = proba

	def export (self):
		return self.vec

	@property
	def level(self):
		return len(self.vec) - 1

	@property
	def text(self):
		return ' - '.join(self.vec)

	def contains(self, vec):
		for ind in range(len(vec)):
			try:
				if vec[ind] != self.vec[ind]:
					return False
			except IndexError:
				return False
		return True


class Bouquet:

	def __init__(self, vec, branches=None):
		self.vec = vec
		self.branches = {}
		if branches is None: branches = []
		self._create_bouquets(branches)

	@property
	def level(self):
		return len(self.vec) - 1
	
	@property
	def size(self):
		return sum([1 + el.proba for el in self.branches.values()]) / 1.5

	def proximity(self, name):
		return 

	@property
	def weight_components(self):
		branches = list(self.branches.values())
		if len(branches) == 0: return (0,0,0)
		return (
			1 * (self.level)/6 # level is usefull in order to know whether we are closer to a theme or a precise suggestion
		), (
			1 * math.log(self.size)/2 # this measures the number of branches inside a suggestion
		), (
			2 * sum([
				el.score for el in branches  # This is the semantic proximity score of each branch
			])/len(branches)
		)

	@property
	def weight(self):
		return sum(self.weight_components)

	def _create_bouquets(self, branches):
		for branch in branches:
			if self.match_branch(branch):
				self.branches[branch.code] = branch

	def contains(self, vec):
		for ind in range(len(vec)):
			try:
				if vec[ind] != self.vec[ind]:
					return False
			except IndexError:
				return False
		return True

	def match_branch(self, branch):
		for ind in range(self.level + 1):
			try:
				if branch.vec[ind] != self.vec[ind]:
					return False
			except IndexError:
				return False
		return True

	def export (self):
		res = copy(self.branches)
		for el in res:
			res[el] = res[el].export()
		return res

def sort_bouquets(el):
	"""
	this function sorts bouquets of suggestions
	"""
	return (-el.weight, el.level)

########### METHODS

def _create_bouquets (branches, level=0):
	"""
	This function creates bouquets (suggestions) from branches
	"""
	root = branches[0].vec[0:level]
	bouquets = [Bouquet(el.vec, branches) for el in branches if el.level == level]
	for el in list(set([el.vec[level] for el in branches if el.level > level])):
		bouquets.append(Bouquet(root + [el], branches) )

	return sorted(bouquets, key=sort_bouquets)

def loop_create(branches, max_size=5, min_level=0):
	"""
	This function loops through bouquets in order to generate all possibles bouquets and rate them
	"""
	group = _create_bouquets(branches, min_level)
	bigs = []

	for el in group:
		if el.size > max_size or el.level == 5:
			bigs.append(el)
			group.remove(el)
			group+=_create_bouquets(list(el.branches.values()), el.level+1)

	# make them unique
	uniques = []
	unique_ids = []

	for el in group + bigs:
		if not ' >> '.join(el.vec) in unique_ids:
			uniques.append(el)
			unique_ids.append(' >> '.join(el.vec))

	return sorted(uniques, key=sort_bouquets)

