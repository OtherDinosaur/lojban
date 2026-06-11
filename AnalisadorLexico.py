#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universidade Federal do Cariri - UFCA
Disciplina: Paradigmas de Programação
Professor: Rafael Will M. de Araujo

Analisador Léxico da linguagem Will
"""


from ClassesAuxiliares import Token, LexicalException


class AnalisadorLexico:

	# Tabela de símbolos (atributo estático)
	simbolos = {
		'=': 'ASSIGN',
		'+': 'OPSUM',
		'-': 'OPSUM',
		'.': 'OPMUL',
		':': 'OPMUL',
		'%': 'OPMUL',
		'#': 'OPMUL',
		'^': 'OPPOW',
		'(': 'LPAR',
		')': 'RPAR',
		'{': 'LBLOCK',
		'}': 'RBLOCK',
		',': 'COMMA',
		';': 'SEMICOLON',
		'==': 'OPREL',
		'<>': 'OPREL',
		'<': 'OPREL',
		'>': 'OPREL',
		'<=': 'OPREL',
		'>=': 'OPREL',
		'|': 'OPREL',
		'log': 'TYPE',
		'num': 'TYPE',
		'true': 'BOOLEAN',
		'false': 'BOOLEAN'
	}

	def __init__(self, codigo):
		self.codigo = codigo
		self.removeComentarios()

	def removeComentarios(self):
		resultado = ''
		pos = 0
		while pos < len(self.codigo): # considerando que um // inicia um comentário
			if pos <= len(self.codigo)-2 and self.codigo[pos:pos+2] == '//':
				while pos < len(self.codigo) and self.codigo[pos] != '\n':
					pos += 1
			if pos <= len(self.codigo)-2 and self.codigo[pos:pos+2] == '/*':
				while pos <= len(self.codigo)-2 and self.codigo[pos:pos+2] != '*/':
					if self.codigo[pos] == '\n':
						resultado += '\n'
					pos += 1
				pos += 2 # compensa o '*/' ao final
			if pos < len(self.codigo):
				resultado += self.codigo[pos]
			pos += 1
		self.codigo = resultado

	def getTokens(self):
		simbolos = AnalisadorLexico.simbolos  # cria um alias para a tabela de símbolos
		tokens = []
		linha = 1
		pos = 0

		while pos < len(self.codigo):
			c = self.codigo[pos]

			if c == '\n':
				linha += 1

			# Pula espaços em branco
			#if current_char.isspace():
			if c in [' ', '\t', '\r', '\n']:
				pos += 1
				continue

			# Checa por tokens de um único caractere
			if c in '=+-.:%^|#(){},:;':
				temp = pos+1
				if temp < len(self.codigo) and c == '=' and self.codigo[temp] == '=':
					tokens.append(Token(simbolos['=='], '==', linha))
					pos = temp
				else:
					tokens.append(Token(simbolos[c], c, linha))
				pos += 1
				continue

			if c in '=<>':
				operador = ''
				while pos < len(self.codigo) and self.codigo[pos] in '=<>':
					operador += self.codigo[pos]
					pos += 1
				if operador in ['<>', '>', '<', '>=', '<=']:
					tokens.append(Token(simbolos[operador], operador, linha))
				continue

			# Checa por números inteiros
			if c.isdigit():
				num = ''
				while pos < len(self.codigo) and self.codigo[pos].isdigit():
					num += self.codigo[pos]
					pos += 1
				tokens.append(Token('NUMBER', num, linha))
				continue

			# Checa por palavras chave ou identificadores
			if c.isalpha() or c == '_':
				identificador = ''
				while pos < len(self.codigo) and (self.codigo[pos].isalnum() or self.codigo[pos] == '_'):
					identificador += self.codigo[pos]
					pos += 1
				if identificador in ['alg', 'var', 'implicit', 'mod', 'in', 'out', 'if', 'else']:
					tokens.append(Token(identificador.upper(), identificador, linha))
				elif identificador in ['log', 'num']:
					tokens.append(Token(simbolos[identificador], identificador, linha))
				elif identificador in ['true', 'false']:
					tokens.append(Token(simbolos[identificador], identificador, linha))
				else:
					tokens.append(Token('ID', identificador, linha))
				continue
			raise LexicalException(f"Caractere inválido '{c}' na linha {linha}")
		
		tokens.append(Token('EOF', 'EOF', linha))  # remova se necessário
		return tokens


if __name__ == '__main__':
	codigo = ''
	with open('exemplo.w', 'r') as f:
		codigo = f.read()

	# Instancie o analisador léxico abaixo. Em seguida, obtenha a lista de tokens
	l = AnalisadorLexico(codigo)
	print(l.getTokens())
