#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universidade Federal do Cariri - UFCA
Disciplina: Paradigmas de Programação
Professor: Rafael Will M. de Araujo

Analisador Sintático da linguagem Will (sem geração da árvore sintática)
"""


from ClassesAuxiliares import SyntaxException


class AnalisadorSintatico:

	def __init__(self, listaTokens):
		self.tokens = listaTokens
		self.tokenCorrente = None
		self.posicao = -1
		self.proximoToken()
	

	def proximoToken(self):
		if self.posicao <= len(self.tokens)-2:
			self.posicao += 1
			self.tokenCorrente = self.tokens[self.posicao]
	

	def lancarErro(self, tipoEsperado=None):
		if tipoEsperado:
			raise SyntaxException(f"Token inesperado: \"{self.tokenCorrente.tipo}\" ({self.tokenCorrente.valor}), tipo esperado: \"{tipoEsperado}\", na linha {self.tokenCorrente.linha}")
		else:
			raise SyntaxException(f"Token inesperado: \"{self.tokenCorrente.tipo}\" ({self.tokenCorrente.valor}) na linha {self.tokenCorrente.linha}")
	

	def comparar(self, tipoEsperado):
		print(f'  comparar: {self.tokenCorrente.tipo} {self.tokenCorrente.valor} {tipoEsperado}')
		tokenRetorno = self.tokenCorrente
		if self.tokenCorrente.tipo == tipoEsperado.upper():
			self.proximoToken()
		else:
			self.lancarErro(tipoEsperado)
		return tokenRetorno
	

	def analisar(self):
		self.alg()


	# <alg> ::= 'alg' <identifier> <declarations> <block>
	def alg(self):
		self.comparar('ALG')
		self.comparar('ID')
		self.declarations()
		self.block()
	

	def declarations(self):
		if self.tokenCorrente.tipo == 'IMPLICIT':
			self.comparar('IMPLICIT')
			self.comparar('MOD')
			self.comparar('LPAR')
			self.comparar('NUMBER')
			self.comparar('RPAR')
		self.comparar('VAR')
		self.varDeclarationList()
	

	def varDeclarationList(self):
		self.varDeclaration()
		while self.tokenCorrente.tipo != 'LBLOCK':
			self.varDeclaration()


	def varDeclaration(self):
		self.comparar('TYPE')
		self.identifierList()
		self.comparar('SEMICOLON')


	def identifierList(self):
		self.comparar('ID')
		while self.tokenCorrente.tipo == 'COMMA':
			self.comparar('COMMA')
			self.comparar('ID')


	def block(self):
		self.comparar('LBLOCK')
		self.statementList()
		self.comparar('RBLOCK')
	

	def statementList(self):
		while self.tokenCorrente.tipo != 'RBLOCK':
			self.statement()
	

	def statement(self):
		if self.tokenCorrente.tipo == 'OUT':
			self.outStatement()
		elif self.tokenCorrente.tipo == 'IF':
			self.ifStatement()
		else:
			self.assignStatement()
	

	def assignStatement(self):
		self.comparar('ID')
		self.comparar('ASSIGN')
		if self.tokenCorrente.tipo == 'IN':
			self.comparar('IN')
			self.comparar('LPAR')
			self.comparar('RPAR')
		else:
			self.expression()
		self.comparar('SEMICOLON')
		
	
	def outStatement(self):
		self.comparar('OUT')
		self.comparar('LPAR')
		if self.tokenCorrente.tipo == 'NUMBER':
			self.comparar('NUMBER')
		elif self.tokenCorrente.tipo == 'BOOLEAN':
			self.comparar('BOOLEAN')
		else:
			self.comparar('ID')
		self.comparar('RPAR')
		self.comparar('SEMICOLON')
	

	def ifStatement(self):
		self.comparar('IF')
		self.expression()
		self.block()
		if self.tokenCorrente.tipo == 'ELSE':
			self.comparar('ELSE')
			self.block()
	

	def expression(self):
		self.sumExpression()
		if self.tokenCorrente.tipo == 'OPREL':
			self.comparar('OPREL')
			self.sumExpression()

	
	def sumExpression(self):
		if self.tokenCorrente.tipo == 'OPSUM':
			self.comparar('OPSUM')
		self.multiplicativeTerm()
		self.sumExpression2()
	

	def sumExpression2(self):
		if self.tokenCorrente.tipo == 'OPSUM':
			self.comparar('OPSUM')
			self.multiplicativeTerm()
			self.sumExpression2()
	

	def multiplicativeTerm(self):
		self.powerTerm()
		while self.tokenCorrente.tipo == 'OPMUL':
			self.comparar('OPMUL')
			self.multiplicativeTerm()


	def powerTerm(self):
		self.factor()
		while self.tokenCorrente.tipo == 'OPPOW':
			self.comparar('OPPOW')
			self.powerTerm()


	def factor(self):
		if self.tokenCorrente.tipo == 'OPSUM':
			self.comparar('OPSUM')
		if self.tokenCorrente.tipo == 'ID':
			self.comparar('ID')
		elif self.tokenCorrente.tipo == 'NUMBER':
			self.comparar('NUMBER')
		elif self.tokenCorrente.tipo == 'BOOLEAN':
			self.comparar('BOOLEAN')
		else:
			self.comparar('LPAR')
			self.expression()
			self.comparar('RPAR')



if __name__ == '__main__':
	from AnalisadorLexico import AnalisadorLexico  # necessário para os testes abaixo

	codigo = ''
	with open('exemplo.w', 'r') as f:
		codigo = f.read()

	lex = AnalisadorLexico(codigo)
	tokens = lex.getTokens()

	parser = AnalisadorSintatico(tokens)
	parser.analisar()
	
