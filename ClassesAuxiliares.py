#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universidade Federal do Cariri - UFCA
Disciplina: Paradigmas de Programação
Professor: Rafael Will M. de Araujo

Classes auxiliares usados pelo compilador da linguagem Will
"""


class LexicalException(Exception):
	pass


class SyntaxException(Exception):
	pass


class SemanticException(Exception):
	pass


class Token:

	def __init__(self, tipo, valor, linha):
		self.tipo = tipo
		self.valor = valor
		self.linha = linha
	
	def __repr__(self):
		return f'({self.tipo} {self.valor} {self.linha})'


class NoTabela:

	def __init__(self, valor, tipo):
		self.valor = valor
		self.tipo = tipo

	def __repr__(self):
		return f'({self.valor} {self.tipo})'

class NoInterno:
	def __init__(self, op, **nos):
		self.op = op
		self.d = {}
		for k, v in nos.items():
			self.d[k] = v

	def get(self, k):
		return self.d.get(k)

	def __repr__(self):
		return f"NoInterno(op: {self.op}; d: {self.d})"
	
	def toString(self, nivel=0):
		s = f'NoInterno(op="{self.op}", \n'
		for i, k in enumerate(self.d.keys()):
			valor = self.d[k]
			if type(valor) == str:
				valor = f'"{valor}"'
			elif type(valor) == NoInterno:
				valor = valor.toString(nivel+1)
			#s += "    "*nivel + f"{k}={valor},\n"
			s += "    "*nivel + f"{k}=\n{'    '*(nivel+1)}{valor}"
			if i < len(self.d.keys())-1:
				s += ",\n"
			else:
				s += "\n"
		s += "    "*nivel + ")"
		return s


class NoFolha:
	def __init__(self, op, valor, linha):
		self.op = op
		self.valor = valor
		self.linha = linha
	
	def __repr__(self):
		return f"NoFolha(op: {self.op}; val: {self.valor}; linha: {self.linha})"


