#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
from pybot import *

# Configuração de caracteres do mapa
parede     = '#'
corredor   = '.'
percorrido = '='
errado     = 'x'
solucao    = '@'
entrada    = 'R'
saida      = 'S'
queijo     = 'Q'

direcoes = [ 
             [1,0],
             [-1,0],
             [0,1],
             [0,-1]
            ]

class Labirinto( object ):
    def __init__( self ):
        self.mapa           = None
        self.entrada        = None
        self.saida          = None
        self.quijos         = 0
        self.listaPercorica = {}
        self.listaAcaminhar = []
        self.passos			= []
    # __init__()

    def __str__( self ):
        m = []
        for l in self.mapa:
            m.append( ''.join( l ) )
        return '\n'.join( m )
    # __str__()

    def le_mapa( self, texto ):
        """Lê um mapa, este deve ter uma entrada e uma saída."""
        self.mapa = texto.split( '\n' )

        for i, l in enumerate( self.mapa ):
            # encontra entrada:
            p = l.find( entrada )
            if p >= 0:
                self.entrada = {'x':p, 'y':i, 'custo':0, 'pai':None, 'tipo':'R'}
            # encontra saida:
            p = l.find( saida )
            if p >= 0:
                self.saida = {'x':p, 'y':i}

            # converte string para lista
            self.mapa[ i ] = list( l )

        if not self.entrada:
            raise ValueError( "O mapa não possui uma entrada!" )
        if not self.saida:
            raise ValueError( "O mapa não possui uma saída!" )
    # le_mapa()


    def le_mapa_arquivo( self, arquivo ):
        """Lê um mapa de um arquivo"""
        f = open( arquivo )
        self.le_mapa( f.read() )
        f.close()
    # le_mapa_arquivo()

    # def resolve( self ):
        """Resolve o labirinto, tenta encontrar a saída.

        Se a saída foi encontrada, retorna True, caso contrário False.
        """

    def posicao_valida(self, linha, coluna ):
        "Função utilizada para conferir se a posição está dentro do mapa"
        if linha > len( self.mapa ) or \
               coluna >= len( self.mapa[ linha ] ):
            "Posição inválida, sai fora do mapa"
            return False
        else:
            return True
    # posicao_valida()

    def calcularHeuristica(self, itemLista):
        itemLista['heuristica'] = abs((itemLista['y'] - self.saida['y'])) + abs((itemLista['x'] - self.saida['x']))
    # calcularHeuristica
       
    # calcula o menor custo total, se for igual pega pela heuristica
    def calcularMenorCusto(self, item1, item2):
        if(item1['total'] < item2['total']):
            return item1
        elif(item2['total'] < item1['total']):
            return item2
        else:
            if(item1['heuristica'] < item2['heuristica']):
                return item1
            else:
                return item2
    # calcularMenorCusto

    def encontra_saida( self, itemLista ):
        # Função recursiva para encontrar a saída.
        if itemLista['x'] == self.saida['x'] and itemLista['y'] == self.saida['y']:
            # Caso base da recursão, estamos em cima da saída
            # obtém uma lista de caminhos percorridos
            caminho = itemLista
            lista = []

            while (caminho!=None):
                lista.append({'x':caminho['x'], 'y':caminho['y'],'tipo':caminho['tipo']})
                self.mapa[caminho['y']][caminho['x']] = solucao
                if(caminho['tipo'] == queijo):
                    self.quijos = self.quijos + 1 
                caminho = caminho['pai']

            lista.reverse()

            self.passos = lista 

            return lista, self.quijos
        else:
            
            # adiciona na lisra que já foi passado por essa posição
            self.listaPercorica[str(itemLista['y'])+','+str(itemLista['x'])] = True
            
            # percore todas as direcoes e verifica se a posicao já foi visitada
            # verifica se a posiçao está dentro do mapa, verifica se é um cimnho que pode seguir
            for direcao in direcoes:
                if self.posicao_valida(direcao[0]+itemLista['y'], direcao[1]+itemLista['x']):
                    tipo = self.mapa[direcao[0]+itemLista['y']][direcao[1]+itemLista['x']]
                    if tipo in (corredor, saida, queijo) and \
                    not(self.listaPercorica.get(str(itemLista['y']+direcao[0])+','+str(itemLista['x']+direcao[1]))):
                        itemValido = {}
                        itemValido['y'] = itemLista['y'] + direcao[0]
                        itemValido['x'] = itemLista['x'] + direcao[1]
                        itemValido['custo'] = itemLista['custo'] + 1
                        self.calcularHeuristica(itemValido)
                        itemValido['total'] = itemValido['heuristica'] + itemValido['custo']
                        itemValido['pai'] = itemLista
                        itemValido['tipo'] = tipo
                        self.listaAcaminhar.append(itemValido)
        # encontra_saida()
        

        if (len(self.listaAcaminhar)>0):
            # achar o menor a caminho para saber onde tem que ir agora
            itemMenor = reduce(self.calcularMenorCusto, self.listaAcaminhar, self.listaAcaminhar[0])
            
            # remove o item menor pois é por ele que vamos seguir e não devemos ir por onde já fomos
            self.listaAcaminhar.remove(itemMenor)
  
            return self.encontra_saida(itemMenor)
        else:
            print ("Nenhuma solução")
            return False
    # resolve()
# Labirinto


# Exemplo de uso:
import sys
l = Labirinto()

l.le_mapa(
    """#########
#R..Q..Q#
#.#.#Q#.#
#...#.#.#
#####.#.#
#.Q.Q.#.#
#.#####.#
#..Q..Q.#
#####S###""" )

print (l)
print ("achou?",l.encontra_saida(l.entrada))
print (l)
print ("quijos encontrados:", l.quijos)
#print "Custo Total:", l.custoTot
#print historico[2]

mundo = Mundo(altura=10, largura=8, espera=True)