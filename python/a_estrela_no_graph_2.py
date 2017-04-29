#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-


# Configuração de caracteres do mapa
parede     = '#'
corredor   = '.'
percorrido = '='
errado     = 'x'
solucao    = '@'
entrada    = 'E'
saida      = 'S'


class Labirinto( object ):
    def __init__( self ):
        self.mapa    = None
        self.entrada = None
        self.saida   = None
    # __init__()


    def le_mapa( self, texto ):
        """Lê um mapa, este deve ter uma entrada e uma saída."""
        self.mapa = texto.split( '\n' )

        for i, l in enumerate( self.mapa ):
            # encontra entrada:
            p = l.find( entrada )
            if p >= 0:
                self.entrada = ( i, p )
            # encontra saida:
            p = l.find( saida )
            if p >= 0:
                self.saida = ( i, p )

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



    def __str__( self ):
        m = []
        for l in self.mapa:
            m.append( ''.join( l ) )
        return '\n'.join( m )
    # __str__()


    def resolve( self ):
        """Resolve o labirinto, tenta encontrar a saída.

        Se a saída foi encontrada, retorna True, caso contrário False.
        """
        def posicao_valida( linha, coluna ):
            "Função utilizada para conferir se a posição está dentro do mapa"
            if linha > len( self.mapa ) or \
                   coluna > len( self.mapa[ linha ] ):
                "Posição inválida, sai fora do mapa"
                return False
            else:
                return True
        # posicao_valida()


        def encontra_saida( linha, coluna ):
            """Função recursiva para encontrar a saída."""

            if self.mapa[ linha ][ coluna ] == saida:
                "Caso base da recursão, estamos em cima da saída"
                return True
            else:
                """Marque como percorrido e entre em recursão

                No caso iremos pela direita, depois para cima, para esquerda e
                então para baixo.

                Lembrando que isto é uma recursão e que marcamos nosso caminho,
                temos magicamente a lembrança dos caminhos já testados.
                """
                self.mapa[ linha ][ coluna ] = percorrido
                achou = False

                if not achou and \
                       posicao_valida( linha, coluna + 1 ) and \
                       self.mapa[ linha ][ coluna + 1 ] in ( corredor, saida ):
                    """Ainda não encontrou e
                    a posição à direita é corredor ou é a saída.
                    Prossiga pela direita."""
                    achou = encontra_saida( linha, coluna + 1 )

                if not achou and \
                       posicao_valida( linha - 1, coluna ) and \
                       self.mapa[ linha - 1 ][ coluna ] in ( corredor, saida ):
                    """Ainda não encontrou e
                    a posição acima é corredor ou é a saída.
                    Prossiga para cima."""
                    achou = encontra_saida( linha - 1, coluna )

                if not achou and \
                       posicao_valida( linha, coluna - 1 ) and \
                       self.mapa[ linha ][ coluna - 1 ] in ( corredor, saida ):
                    """Ainda não encontrou e
                    a posição à esquerda é corredor ou é a saída.
                    Prossiga para esquerda."""
                    achou = encontra_saida( linha, coluna - 1 )

                if not achou and \
                       posicao_valida( linha + 1, coluna ) and \
                       self.mapa[ linha + 1 ][ coluna ] in ( corredor, saida ):
                    """Ainda não encontrou e
                    a posição abaixo é corredor ou é a saída.
                    Prossiga para baixo."""
                    achou = encontra_saida( linha + 1, coluna )

                # Caso o caminho adotado foi correto, marque como solução
                # senão marque como errado
                if achou:
                    self.mapa[ linha ][ coluna ] = solucao
                else:
                    self.mapa[ linha ][ coluna ] = errado
                    
                return achou
        # encontra_saida()
        
        return encontra_saida( self.entrada[ 0 ], self.entrada[ 1 ] )
    # resolve()
# Labirinto


# Exemplo de uso:
l = Labirinto()
l.le_mapa(
    """
############## ####################
#E.#.S#..#...###.....#.#..........#
#..#.............###.#............#
##...##...######## #...#..........# 
##############     ################
""" )
print l
print "achou?",l.resolve()
print l