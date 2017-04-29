#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-

import sys
import pygame
from pygame.locals import *
from pygame.sprite import Sprite, RenderUpdates
from math import floor



def desenha_quadrado( tamanho, cor ):
    img = pygame.Surface( tamanho )

    cinza = Color( "#808080" )
    cor1 = pygame.color.add( cor, cinza )
    cor2 = pygame.color.subtract( cor, cinza )

    r = Rect( ( 0, 0 ), tamanho )
    r.inflate_ip( -2, -2 )
    r.topleft = ( 1, 1 )

    img.fill( cor )

    line = pygame.draw.line
    line( img, cor1, r.topleft, r.topright )
    line( img, cor1, r.topleft, r.bottomleft )
    line( img, cor2, r.bottomleft, r.bottomright )
    line( img, cor2, r.bottomright, r.topright )

    return img
# desenha_quadrado()




class Quadrado( Sprite ):
    grupos = None # Grupos ao qual este sprite pertence
                  # depois esta variavel de classe sera atribuida
                  # para lembrar dos objetos nao desenhados
    tamanho = ( 50, 50 )
    def __init__( self, pos=( 0, 0 ) ):
        Sprite.__init__( self, self.grupos )
        self.rect = Rect( pos, self.tamanho )
    # __init__()
# Quadrado


class Parede( Quadrado ):
    pass
# Parede

class Vazio( Quadrado ):
    pass
# Vazio

class Caminho( Quadrado ):
    pass
# Caminho

class Entrada( Quadrado ):
    pass
# Entrada

class Saida( Quadrado ):
    pass
# Saida

class CaminhoErrado( Caminho ):
    pass
# CaminhoErrado

class CaminhoCerto( Caminho ):
    pass
# CaminhoCerto

class CaminhoPercorrido( Caminho ):
    pass
# CaminhoPercorrido


CHR_CAMINHO = "."
CHR_PAREDE = "#"
CHR_ENTRADA = "E"
CHR_SAIDA = "S"
CHR_CAMINHO_ERRADO = "!"
CHR_CAMINHO_PERCORRIDO = "-"
CHR_CAMINHO_CERTO = "@"
CHR_VAZIO = " "

class Labirinto( object ):
    tipos_mapa = {
        CHR_CAMINHO: Caminho,
        CHR_PAREDE: Parede,
        CHR_ENTRADA: Entrada,
        CHR_SAIDA: Saida,
        CHR_CAMINHO_ERRADO: CaminhoErrado,
        CHR_CAMINHO_PERCORRIDO: CaminhoPercorrido,
        CHR_CAMINHO_CERTO: CaminhoCerto,
        CHR_VAZIO: Vazio,
        }

    def __init__( self, tela, descricao_mapa=None ):
        self.tela     = tela
        self.entrada  = None
        self.saida    = None
        self.tamanho  = None
        self.mapa     = None
        self.tam_peca = None

        # grupo que contem objetos nao desenhados
        self.nao_desenhados = RenderUpdates()

        if descricao_mapa:
            self.monta_labirinto( descricao_mapa )
    # __init__()


    def monta_labirinto( self, descricao_mapa ):
            self.__le_mapa( descricao_mapa )
            self.__arruma_posicoes()
            self.__le_imagens()
    # monta_labirinto()


    def __le_imagens( self ):
        """Lê as imagens para cada tipo de peça.

        Usa-se variavel de classe para evitar que cada objeto tenha uma copia
        da mesma imagem, economizando memoria.
        """
        t = self.tam_peca

        if t is None:
            raise Exception( "Você deve usar __arruma_posicoes() primeiro!" )

        Quadrado.tamanho = t

        # Lê imagens:
        Parede.image            = desenha_quadrado( t, Color( "gray35" ) )
        Caminho.image           = desenha_quadrado( t, Color( "wheat" ) )
        Entrada.image           = desenha_quadrado( t, Color( "magenta" ) )
        Saida.image             = desenha_quadrado( t, Color( "green" ) )
        CaminhoCerto.image      = desenha_quadrado( t, Color( "cyan" ) )
        CaminhoErrado.image     = desenha_quadrado( t, Color( "red" ) )
        CaminhoPercorrido.image = desenha_quadrado( t, Color( "yellow" ) )
        Vazio.image             = pygame.Surface( t )
        Vazio.image.set_colorkey( Color( "black" ) )
        Vazio.image.fill( Color( "black" ) )
    # __le_imagens()



    def __le_mapa( self, descricao ):
        mapa       = []
        max_x      = 0
        tipos_mapa = self.tipos_mapa

        # esvazia grupo de sprites nao desenhados
        self.nao_desenhados.empty()
        Quadrado.grupos = self.nao_desenhados

        for i, linha in enumerate( descricao.split( "\n" ) ):
            l = []
            for j, letra in enumerate( linha ):
                tipo = tipos_mapa.get( letra, Vazio )

                if   tipo == Entrada:
                    self.entrada = ( i, j )
                elif tipo == Saida:
                    self.saida   = ( i, j )


                l.append( tipo() )
                max_x = max( max_x, j )
            mapa.append( l )
        max_x += 1

        self.mapa    = mapa
        self.tamanho = ( max_x, i )
    # __le_mapa()


    def __arruma_posicoes( self ):
        if self.mapa is None:
            raise Exception( "Você deve usar __le_mapa() primeiro!" )

        tw, th = self.tela.get_size()
        mw, mh = self.tamanho
        w = int( floor( float( tw ) / mw ) )
        h = int( floor( float( th ) / mh ) )

        ## Para ter aspecto quadrado das peças, descomente a linha abaixo
        # w = h = min( w, h )

        tamanho = ( w, h )

        for i, l in enumerate( self.mapa ):
            for j, c in enumerate( l ):
                pos = ( j * w, i * h )
                c.rect = Rect( pos, tamanho )

        for tipo in self.tipos_mapa.itervalues():
            tipo.tamanho = tamanho

        self.tam_peca = tamanho
    # __arruma_posicoes()


    def desenhe( self, tudo=False ):
        tela = self.tela
        nao_desenhados = self.nao_desenhados
        if tudo:
            for l in self.mapa:
                for p in l:
                    tela.blit( p.image, p )
        else:
            nao_desenhados.draw( self.tela )

        nao_desenhados.empty()
    # desenhe()


    def resolve( self, callback=None ):
        """Resolve o labirinto.

        callback pode ser uma função que recebe o estágio do processo
        recursivo, são eles:
          0: entrou em um estagio da recursao
          1: passou da condicao base (continua recursao)
          2: termino da funcao (saiu da recursao)
        """
        mapa  = self.mapa
        w, h  = self.tamanho

        if not callback:
            callback = lambda x: x

        def resolve_recursivo( x, y ):
            callback( 0 )

            achou = False
            if 0 <= x < w and 0 <= y < h:
                callback( 1 )

                peca = mapa[ y ][ x ]
                tipo_peca = type( peca )

                if tipo_peca in ( Caminho, Entrada ):
                    pos = peca.rect.topleft
                    mapa[ y ][ x ] = CaminhoPercorrido( pos )
                    if resolve_recursivo( x + 1,     y ) or \
                       resolve_recursivo(     x, y - 1 ) or \
                       resolve_recursivo( x - 1,     y ) or \
                       resolve_recursivo(     x, y + 1 ):
                        mapa[ y ][ x ] = CaminhoCerto( pos )
                        achou = True
                    else:
                        mapa[ y ][ x ] = CaminhoErrado( pos )
                elif tipo_peca == Saida:
                    achou = True
            # fim do if
            callback( 2 )
            return achou
        # resolve_recursivo()

        ex, ey = self.entrada
        # resolve a partir da entrada
        achou = resolve_recursivo( ex, ey )
        # marque a entrada
        pos = mapa[ ex ][ ey ].rect.topleft
        mapa[ ex ][ ey ] = Entrada( pos )
        return achou
    # resolve()
# Labirinto



class Jogo( object ):
    FPS = 24
    RESOLVE_PASSOS_POR_SEG = 0

    def __init__( self, mapa, tamanho=( 800, 600 ) ):
        self.clock = pygame.time.Clock()
        self.tela  = pygame.display.set_mode( tamanho )
        self.mapa  = mapa
        self.le_labirinto()
    # __init__()


    def le_labirinto( self ):
        #self.labirinto = Labirinto( self.tela, self.mapa )
        self.labirinto = AStar( self.tela, self.mapa )
    # le_labirinto()


    def termine( self ):
        raise StopIteration
    # termine()


    def atualize( self, tudo=False ):
        if tudo:
            pygame.display.flip()
        else:
            pygame.display.update() # XXXXXX usar lista de retangulos!
    # atualize()


    def trata_eventos( self ):
        for e in pygame.event.get( [ KEYDOWN, QUIT, ACTIVEEVENT ] ):
            if   e.type == QUIT:
                self.termine()

            elif e.type == KEYDOWN:
                if   e.key == K_F2:
                    self.le_labirinto()

                elif e.key == K_F3:
                    def callback( estagio ):
                        self.trata_eventos()
                        if   estagio == 0:
                            self.labirinto.desenhe(True)
                            self.atualize()
                        elif estagio == 1:
                            self.clock.tick( self.RESOLVE_PASSOS_POR_SEG )
                        elif estagio == 2:
                            self.labirinto.desenhe(True)
                            self.atualize()
                    # callback()
                    self.labirinto.resolve( callback )
                    self.labirinto.desenhe(True)
                    self.atualize()

                elif e.key == K_ESCAPE:
                    self.termine()

            elif e.type == ACTIVEEVENT:
                self.labirinto.desenhe( True )
                self.atualize( True )
    # trata_eventos()


    def rode( self ):
        try:
            # ActiveEvent faz desenhar a tela de novo
            pygame.event.post( pygame.event.Event( ACTIVEEVENT ) )
            while True:
                self.clock.tick( self.FPS )
                self.trata_eventos()
                #self.labirinto.desenhe()
                self.atualize()
        except StopIteration:
            return
    # rode()
# Jogo


from heapq import heappush, heappop

# representação de cada nó do AStar
class No(object):
    def __init__(self, pos=None, pai=None, g=0, h=0):
        self.pos = pos
        self.pai = pai
        self.g = g
        self.h = h

    def __eq__(self, other):
        return self.pos == other.pos

    def __ne__(self, other):
        return self.pos != other.pos

    def __le__(self, other):
        return self.g+self.h <= other.g+other.h

    def __ge__(self, other):
        return self.g+self.h >= other.g+other.h

    def __str__(self):
        return 'pos = %s, g = %d, h = %d' % (self.pos, self.g, self.h)


class AStar(Labirinto):

    """ Algoritmo AStar.

    mapa deve ser um vetor de strings ou uma matriz de caracteres de
    tamanho NxM.
    """
    def __init__(self, tela, mapa):
        Labirinto.__init__(self, tela, mapa)
        # listas do algoritmo AStar
        mapa = mapa.split('\n')
        self.n = len(mapa)    #linhas
        self.m = len(mapa[0]) #colunas

        # procurar pela entrada e saída
        entrada = None
        saida = None
        print (mapa)
        for i, linha in enumerate(mapa):
            for j, char in enumerate(linha):
                if char == 'E':
                    entrada = [i, j]
                elif char == 'S':
                    saida = [i, j]
        self.entrada = entrada
        self.saida = saida
        
    # ajuda a calcular a distância
    def dist(self, orig, dest):
        return abs(orig[0] - dest[0]) + abs(orig[1] - dest[1])

    # retorna os vizinhos de um nó no mapa, caso possa caminhar por eles
    def vizinhos(self, no):
        mapa = self.mapa
        n, m = self.n, self.m
        pos = no.pos
        res = []
        listaPos = [(-1,0), (1,0), (0,-1), (0,1)]
        for p in listaPos:
            x, y = pos[0] + p[0], pos[1] + p[1]
            if 0 <= x < m and  0 <= y < n:
                if type(mapa[x][y]) in (Caminho, CaminhoPercorrido, Saida):
                    novo = No([x, y], no, no.g+1, self.dist([x, y], self.saida))
                    res.append(novo)
        return res


    def resolve(self, callback):
        aberta = []
        fechada = [] 

        entrada = self.entrada
        saida = self.saida
        mapa = self.mapa
        
        at = No()
        at.h = self.dist(entrada, saida)
        at.pos = entrada[:]
        at.pai = None
        heappush(aberta, at)
        achou = False
        callback(0)
        qSaida = mapa[saida[0]][saida[1]]
        qEntrada = mapa[entrada[0]][entrada[1]]
        while len(aberta) > 0:
            at = heappop(aberta)
            fechada.append(at)
            if at.pos == saida: # achou
                achou = True
                break
            viz = self.vizinhos(at)
            for no in viz:
                if not no in fechada:
                    if not no in aberta:
                        heappush(aberta, no)
                        topleft = mapa[no.pos[0]][no.pos[1]].rect.topleft
                        mapa[no.pos[0]][no.pos[1]] = CaminhoPercorrido(topleft)
                        callback(1)
        mapa[saida[0]][saida[1]] = qSaida
        # reconstrução do caminho
        if achou:
            caminho = [at.pos]
            while True:
                at = at.pai
                if at is None:
                    break
                caminho.insert(0, at.pos)
                topleft = mapa[at.pos[0]][at.pos[1]].rect.topleft
                mapa[at.pos[0]][at.pos[1]] = CaminhoCerto(topleft)
                callback(1)
#            print caminho
            mapa[entrada[0]][entrada[1]] = qEntrada
            callback(2)
        else:
            print ('Caminho não encontrado')



if __name__ == "__main__":
    def uso():
        print ("Uso:\n\t%s [arquivo.mapa]\n\n" % sys.argv[ 0 ])
        print ("Caracteres que compoe um mapa:")
        for k, v in globals().iteritems():
            if k.startswith( "CHR_" ):
                legenda = k[ 4: ].replace( "_", " " ).capitalize()
                print ("   '%s'   %s" % ( v, legenda ))
        print
    # uso()

    if len( sys.argv ) < 2:
        mapa = """\
############## ####################
#E.#..#..#...###.....#.#..........#
#................###.#............#
#................###.#............#
#................###.#............#
#................###.#............#
#................###.#............#
#................###.#............#
##..S##...######## #...#..........# 
##############     ################
"""
    else:
        if sys.argv[ 1 ] in ( "-h", "-help", "--help" ):
            uso()
            raise SystemExit
        else:
            f = open( sys.argv[ 1 ] )
            mapa = f.read()
            f.close()

    pygame.init()
    jogo = Jogo( mapa )
    jogo.rode()