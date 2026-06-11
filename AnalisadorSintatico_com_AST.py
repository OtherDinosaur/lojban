#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universidade Federal do Cariri - UFCA
Disciplina: Paradigmas de Programação
Professor: Rafael Will M. de Araujo

Analisador Sintático da linguagem Will (com geração da árvore sintática)
"""


from ClassesAuxiliares import NoInterno, NoFolha, SyntaxException


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
		return self.alg()


	def alg(self):
		self.comparar('ALG')
		tokenIdentifier = self.comparar('ID')
		objDeclarations = self.declarations()
		objBlock = self.block()
		return NoInterno('alg', id=NoFolha('id', tokenIdentifier.valor, tokenIdentifier.linha), declarations=objDeclarations, block=objBlock)
	

	def declarations(self):
		mod = 0
		linha = 0
		if self.tokenCorrente.tipo == 'IMPLICIT':
			self.comparar('IMPLICIT')
			self.comparar('MOD')
			self.comparar('LPAR')
			token = self.comparar('NUMBER')
			linha = token.linha
			mod = token.valor
			self.comparar('RPAR')
		self.comparar('VAR')
		L = self.varDeclarationList()
		return NoInterno('declarations', mod=NoFolha('number', mod, linha), varDeclarationList=L)
	

	def varDeclarationList(self):
		no = None
		if self.tokenCorrente.tipo != 'LBLOCK':
			objVarDeclaration = self.varDeclaration()
			proxNo = self.varDeclarationList()
			no = NoInterno('varDeclarationList', varDeclaration=objVarDeclaration, prox=proxNo)
		return no


	def varDeclaration(self):
		token = self.comparar('TYPE')
		L = self.identifierList()
		self.comparar('SEMICOLON')
		return NoInterno('varDeclaration', type=NoFolha('type', token.valor, token.linha), identifierList=L)


	def identifierList(self):
		token = self.comparar('ID')
		noId = NoFolha('id', token.valor, token.linha)
		proxNo = None
		if self.tokenCorrente.tipo == 'COMMA':
			self.comparar('COMMA')
			proxNo = self.identifierList()
		return NoInterno('identifierList', id=noId, prox=proxNo)


	def block(self):
		self.comparar('LBLOCK')
		L = self.statementList()
		self.comparar('RBLOCK')
		return NoInterno('block', statementList=L)
	

	def statementList(self):
		no = None
		if self.tokenCorrente.tipo != 'RBLOCK':
			objStatement = self.statement()
			proxNo = self.statementList()
			no = NoInterno('statementList', statement=objStatement, prox=proxNo)
		return no
	

	def statement(self):
		objStatement = None
		if self.tokenCorrente.tipo == 'OUT':
			objStatement = self.outStatement()
		elif self.tokenCorrente.tipo == 'IF':
			objStatement = self.ifStatement()
		else:
			objStatement = self.assignStatement()
		return objStatement


	def assignStatement(self):
		tokenIdentifier = self.comparar('ID')
		self.comparar('ASSIGN')
		if self.tokenCorrente.tipo == 'IN':
			objInStatement = self.inStatement()
			self.comparar('SEMICOLON')
			return NoInterno('assignStatement', id=NoFolha('id', tokenIdentifier.valor, tokenIdentifier.linha), inStatement=objInStatement)
		else:
			objExpression = self.expression()
			self.comparar('SEMICOLON')
			return NoInterno('assignStatement', id=NoFolha('id', tokenIdentifier.valor, tokenIdentifier.linha), expression=objExpression)
	

	def inStatement(self):
		token = self.comparar('IN')
		self.comparar('LPAR')
		self.comparar('RPAR')
		return NoFolha('in', token.valor, token.linha)
		
	
	def outStatement(self):
		self.comparar('OUT')
		self.comparar('LPAR')
		objExpression = self.expression()
		self.comparar('RPAR')
		self.comparar('SEMICOLON')
		return NoInterno('outStatement', expression=objExpression)
	

	def ifStatement(self):
		self.comparar('IF')
		objExpressionIf = self.expression()
		objBlockIf = self.block()
		objBlockElse = None
		if self.tokenCorrente.tipo == 'ELSE':
			self.comparar('ELSE')
			objBlockElse = self.block()
		return NoInterno('ifStatement', expression=objExpressionIf, blockIf=objBlockIf, blockElse=objBlockElse)


	def expression(self):
		esq = self.sumExpression()
		operador = None
		dir = None
		if self.tokenCorrente.tipo == 'OPREL':
			token = self.comparar('OPREL')
			operador = token.valor
			dir = self.sumExpression()
		return NoInterno('expression', esq=esq, oper=operador, dir=dir)
	

	def sumExpression(self):
		esq = self.multiplicativeTerm()
		return self.sumExpression2(esq)
	

	def sumExpression2(self, esq):
		if self.tokenCorrente.tipo == 'OPSUM':
			token = self.comparar('OPSUM')
			dir = self.multiplicativeTerm()
			no = NoInterno('sumExpression', oper=token.valor, esq=esq, dir=dir)
			return self.sumExpression2(no)
		else:
			return esq
	

	def multiplicativeTerm(self):
		esq = self.powerTerm()
		return self.multiplicativeTerm2(esq)
	

	def multiplicativeTerm2(self, esq):
		if self.tokenCorrente.tipo == 'OPMUL':
			token = self.comparar('OPMUL')
			dir = self.powerTerm()
			no = NoInterno('multiplicativeTerm', oper=token.valor, esq=esq, dir=dir)
			return self.multiplicativeTerm2(no)
		else:
			return esq


	def powerTerm(self):
		esq = self.factor()
		if self.tokenCorrente.tipo == 'OPPOW':
			token = self.comparar('OPPOW')
			dir = self.powerTerm()
			return NoInterno('powerTerm', oper=token.valor, esq=esq, dir=dir)
		else:
			return esq


	def factor(self):
		sinal = '+'
		if self.tokenCorrente.tipo == 'OPSUM':
			token = self.comparar('OPSUM')
			if token.valor == '-':
				sinal = '-'
		if self.tokenCorrente.tipo == 'ID':
			token = self.comparar('ID')
			return NoInterno('factor', sinal=sinal, factor=NoFolha('id', token.valor, token.linha), esq=None, dir=None)
		elif self.tokenCorrente.tipo == 'NUMBER':
			token = self.comparar('NUMBER')
			return NoInterno('factor', sinal=sinal, factor=NoFolha('num', token.valor, token.linha), esq=None, dir=None)
		elif self.tokenCorrente.tipo == 'BOOLEAN':
			token = self.comparar('BOOLEAN')
			return NoInterno('factor', sinal=sinal, factor=NoFolha('log', token.valor, token.linha), esq=None, dir=None)
		else:
			self.comparar('LPAR')
			objExpression = self.expression()
			self.comparar('RPAR')
			return NoInterno('factor', sinal=sinal, expression=objExpression, esq=None, dir=None)



if __name__ == '__main__':
	from AnalisadorLexico import AnalisadorLexico  # necessário para os testes abaixo

	codigo = ''
	with open('exemplo.w', 'r') as f:
		codigo = f.read()

	lex = AnalisadorLexico(codigo)
	tokens = lex.getTokens()

	parser = AnalisadorSintatico(tokens)
	ast = parser.analisar()  # AST: Abstract Syntax Tree
	print(ast.toString())  # imprime a árvore sintática indentada

