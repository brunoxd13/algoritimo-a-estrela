#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
from pybot import *

# Configuração de caracteres do mapa
parede     = '#'
corredor   = '.'
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
        self.mapaInicial    = None
        self.entrada        = None
        self.saida          = None
        self.custoTot       = 0
        self.queijo         = 0
        self.historico      = None
        self.listaPercorica = {}
        self.listaAcaminhar = []
        self.passos         = []
        self.altura         = 0 
        self.largura        = 0 
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
        self.mapaInicial = texto.split( '\n' )

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

            self.mapaInicial[ i ] = list( l )
        if not self.entrada:
            raise ValueError( "O mapa não possui uma entrada!" )
        if not self.saida:
            raise ValueError( "O mapa não possui uma saída!" )

        self.altura = len(self.mapa)
        self.largura = len(self.mapa[0])
    # le_mapa()


    def le_mapa_arquivo( self, arquivo ):
        """Lê um mapa de um arquivo"""
        f = open( arquivo )
        self.le_mapa( f.read() )
        f.close()
    # le_mapa_arquivo()


    def posicao_valida(self, linha, coluna ):
        # Função utilizada para conferir se a posição está dentro do mapa
        if linha > len( self.mapa ) or \
               coluna >= len( self.mapa[ linha ] ):
            # Posição inválida, sai fora do mapa
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
                    self.queijo = self.queijo + 1 
                caminho = caminho['pai']

            lista.reverse()

            for item in (lista):
                self.passos.append((item['y'], item['x']))

            return True
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
    
        if (len(self.listaAcaminhar)>0):
            # achar o menor a caminha para saber onde tem que ir agora
            itemMenor = reduce(self.calcularMenorCusto, self.listaAcaminhar, self.listaAcaminhar[0])
            
            # remove o item menor pois é por ele que vamos seguir e não devemos ir por onde já fomos
            self.listaAcaminhar.remove(itemMenor)
  
            return self.encontra_saida(itemMenor)
        else:
            return False
    # encontra_saida()
# Labirinto


# Exemplo de uso:
import sys

l = Labirinto()

l.le_mapa_arquivo(sys.argv[1])
resultado = l.encontra_saida(l.entrada)

if(resultado):
    resultadoString = ''
    
    resultadoString += "@ representa o caminho percorrido\n"
    resultadoString += "Resultado:\n"
    resultadoString += str(l )
    resultadoString += "\n\nQueijos encontrados:\n"
    resultadoString += str(l.queijo)
    resultadoString += "\n\nPassos executados:"
    for item in l.passos: 
        resultadoString += "\n"
        resultadoString += str(item)

    arq = open("resultado.txt", "w")
    arq.write( resultadoString)
    arq.close()

    mundo = Mundo(altura=l.altura, largura=l.largura, espera=True)

    mundo.mostra_msg(0,0,'Clique para comecar')

    for i, n in enumerate( l.mapaInicial ): 
        for u, j in enumerate( n ):
            if j == parede:
                ParedeFloyd(u+1, i+1)
            if j == queijo:
                Sabre(u+1, i+1)
            if j == entrada:
                vader = Vader(u+1, i+1)
            if j == saida:
                portal = Portal(u+1, i+1)
    
    for passo in l.passos:
        vader.move_para(passo[1]+1, passo[0]+1)
        # meuSleep(0.5)
        espera()

    # espera()
    portal.remove()
    # vader.remove()
    # mundo.mostra_msg(0,0,'O resultado se encontra em um txt')
    
    for i, n in enumerate( l.mapa ): 
        for u, j in enumerate( n ):
            if j == solucao:
                Rastro(u+1, i+1)

    vader.explodir('Fim de jogo')