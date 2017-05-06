# coding=UTF-8

import os
import sys
import pygame
from pygame.locals import *
import random
import atexit

if not pygame.font:
    raise SystemExit('Não conseguiu carregar fontes')

# constantes gerais
MAIN_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
DATA_DIR = os.path.join(MAIN_DIR, 'dados')
FONT_DIR = os.path.join(MAIN_DIR, 'fonts')

#TODO pegar o diretório automaticamente (não FIXED_FONT certo quando é debug)

# direções sao tuplas das coordenadas "X" e "Y"
ACIMA = (0, -1)
ABAIXO = (0, 1)
DIREITA = (1, 0)
ESQUERDA = (-1, 0)
AQUI = (0, 0)

# direções alternativas
acima = ACIMA
abaixo = ABAIXO
direita = DIREITA
esquerda = ESQUERDA
aqui = AQUI

norte = acima
sul = abaixo
leste = esquerda
oeste = direita

nordeste = (1, -1)
sudeste = (1, 1)
sudoeste = (-1, -1)
noroeste = (-1, -1)

#constantes do ambiente
VELOCIDADE = 250  # em milesimos de segundo

# variáveis do sistema
_nome = []
_continua = True

#nomes para os objetos
try:
    arq_nomes = open(os.path.join(DATA_DIR, "nomes.txt"), "r")
    linhas = arq_nomes.readlines()
    _nomes = [str(random.randint(101, 999)) + texto.rstrip("\n") for texto in linhas]
    _nomes.sort()
    _nomes = [nome[3:].decode("utf-8") for nome in _nomes]
except IOError:
    print "Erro (pybot): não consegui ler os nomes"
finally:
    arq_nomes.close()


def acabou():
    global _continua
    _continua = False
    pygame.quit()
    sys.exit()


# aguarda teclar algo
def espera(tempo=0):
    #TODO: implementar tempo
    global _continua
    pronto = False
    while _continua and not pronto:

        #Handle Input Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _continua = False
                acabou()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                _continua = False
                acabou()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                pronto = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pronto = True
            elif event.type == pygame.MOUSEBUTTONUP:
                pronto = True


def inicio(tempo=0):
    espera(tempo)


def espera_fim():
    global _continua
    espera()
    acabou()

#registra a função de espera ao final
atexit.register(espera_fim)


#classe de exceções para os erros causados pelo pybot
class Erro(StandardError):
    def __init__(self, str):
        StandardError.__init__(self, str)


#funções
def load_image(file, path=None):
    "loads an image, prepares it for play"
    if path == None:
        path = DATA_DIR
    file = os.path.join(MAIN_DIR, path, file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' %
                         (file, pygame.get_error()))
    return surface.convert_alpha()


def resize_image(image, max_side):
    img_rect = image.get_rect()
    width = img_rect.width
    height = img_rect.height

    if width > max_side or height > max_side:
        if width > height:
            height = int(round((max_side * 1.0) / width * height, 0))
            width = max_side
        else:
            width = int(round((max_side * 1.0) / width * height, 0))
            height = max_side
        return pygame.transform.smoothscale(image, (width, height))
    else:
        return image


# classe principal: tabuleiro do jogo
class Mundo():
    # Borg design pattern
    __shared_state = {}
    __instance = None

    def __init__(self, largura=1, altura=1, ladrilho=64, espera=False, explodir=True):
        self.__dict__ = self.__shared_state  # Borg design pattern
        if not Mundo.__instance:
            Mundo.__instance = self
            # inicializa as variáveis
            self._tam_y = altura
            self._tam_x = largura
            self.lado = ladrilho
            self.margem = 20
            self._mapa = []
            self.objetos = pygame.sprite.LayeredUpdates()
            self.principal = None
            self.explodir = explodir
            self.espera = espera
            self.redimensiona = True
            self.ladrilho = ladrilho
            self.titulo = "Algoritimo a estrela"

            self.calc_tamanhos()
            self.desenha_grid()

    @staticmethod
    def get_instance():
        return Mundo.__instance

    # propriedades do mundo
    def get_tam_x(self):
        return self._tam_x

    def get_tam_y(self):
        return self._tam_y

    tam_x = property(get_tam_x)
    tam_y = property(get_tam_y)

    # insere um objeto no mundo
    def adiciona(self, objeto):
        if self.redimensiona:
            objeto.redimensiona(self.ladrilho)

        self.objetos.add(objeto)
        x, y = objeto.get_pos()

        self._mapa[x - 1][y - 1] += [objeto]
        # o primeiro objeto adicionado é o principal
        if not self.principal:
            self.principal = objeto
            self.objetos.change_layer(objeto, 1)

    def move_objeto(self, objeto, x, y):
        if objeto in self._mapa[objeto.x - 1][objeto.y - 1]:
            self._mapa[objeto.x - 1][objeto.y - 1].remove(objeto)
        self._mapa[x - 1][y - 1] += [objeto]

    def remove_objeto(self, objeto):
        self.objetos.remove(objeto)
        self._mapa[objeto.x - 1][objeto.y - 1].remove(objeto)
        self.atualiza()

    # desenha o grid
    def desenha_grid(self):
        cor_linha = (0, 0, 0)
        cor_borda = (255, 255, 255)
        cor_casas = ((0xCC, 0xCC, 0xCC), (0x99, 0x99, 0x99))

        # inicializa
        self.screen_tudo = pygame.display.set_mode(self.rect_tudo.size, 0, 32)
        self.screen = self.screen_tudo.subsurface(self.rect_dentro)
        pygame.display.set_caption(self.titulo)

        pygame.init()

        # moldura
        pygame.draw.rect(self.screen_tudo, cor_borda, self.rect_tudo, 0)
        pygame.draw.rect(self.screen, cor_linha, self.rect, 0)

        # grid
        pos_x = 0
        for x in range(0, self.tam_x):
            cor = x
            pos_y = 0
            for y in range(0, self.tam_y):
                pygame.draw.rect(self.screen, cor_casas[cor % 2], pygame.Rect(pos_x, pos_y, self.lado, self.lado))
                pos_y += self.lado
                cor = cor + 1
            pos_x += self.lado

        self.screen_fundo = self.screen.copy()
        pygame.display.flip()

    # refaz a pintura
    def atualiza(self):
        global _continua
        self.objetos.clear(self.screen, self.screen_fundo)
        self.objetos.draw(self.screen)
        pygame.display.flip()

    # quando mudam as dimensões tem recalcular tudo
    def calc_tamanhos(self):
        # tamanho em pixels da área útil
        self.pixels_x = (self.tam_x * self.lado)
        self.pixels_y = (self.tam_y * self.lado)

        # rect externo da tela
        self.rect_tudo = pygame.Rect(0, 0, self.pixels_x + (self.margem * 2), self.pixels_y + (self.margem * 2))

        # rect interno do tabuleiro, coordenadas da tela
        self.rect_dentro = pygame.Rect(self.margem, self.margem, self.pixels_x, self.pixels_y)

        # rect interno do tabuleiro
        self.rect = pygame.Rect(0, 0, self.pixels_x, self.pixels_x)

        # _mapa interno de objetos
        for i in range(0, self.tam_x):
            self._mapa.append([])
            for j in range(0, self.tam_y):
                self._mapa[i].append([])

        return None

    # retorna o Rect relativo à 0,0 da posição (1,1)
    def get_rect(self, x, y):
        pos_x = (x - 1) * self.lado
        pos_y = (y - 1) * self.lado
        return pygame.Rect(pos_x, pos_y, self.lado, self.lado)

    # funções de teste

    def get_objetos(self, x, y):  # retorna uma cópia dos objetos na posição
        return self._mapa[x - 1][y - 1] + []

    def get_vazio(self, x, y, obj=None):  # retorna se a posição está vazia
        if x > self.tam_x or y > self.tam_y:
            return True
        objetos = self.get_objetos(x, y)
        if obj in objetos:
            objetos.remove(obj)
        return len(objetos) == 0

    def get_fim(self, x, y):  # retorna se a posição está fora do tabuleiro
        return x < 1 or y < 1 or x > self.tam_x or y > self.tam_y

    def get_valor(self, x, y, objeto=None):  # retorna o valor do objeto
        objetos = self.get_objetos(x, y)
        if objeto in objetos: objetos.remove(objeto)
        if len(objetos) == 0:
            raise Erro("Não dá pra saber o valor de uma casa vazia.")

        if len(objetos) == 1:
            return objetos[0].get_valor()
        else:
            return tuple([obj.get_valor() for obj in objetos])

    def get_nome(self, x, y):  # retorna o nome do objeto
        objetos = self.get_objetos(x, y)
        if len(objetos) == 0:
            return ""

        if len(objetos) == 1:
            return objetos[0].get_nome()
        else:
            return tuple([obj.get_nome() for obj in objetos])

    def colisao(self, objeto):  # retorna True se há colisão
        if self.explodir and objeto.solido:
            for outro in self.get_objetos(objeto.x, objeto.y):
                if outro != objeto and outro.solido:
                    return True
        return False

    def mostra_msg(self, x, y, mensagem):
        # prepara a mensagem
        font_name = os.path.join(FONT_DIR, 'DejaVuSans-Bold.ttf')
        font = pygame.font.Font(font_name, 10)
        #TODO: fonte proporcional
        text = font.render(mensagem, True, (204, 0, 0), (255, 255, 255))

        # posiciona a mensagem
        text_rect = text.get_rect()
        text_rect.center = self.rect_dentro.center
        borda_rect = text_rect.inflate(10, 10)

        # salva
        screen_old = self.screen.subsurface(borda_rect)
        screen_bkp = screen_old.copy()

        # mostra a mensagem
        pygame.draw.rect(self.screen, (255, 255, 255), borda_rect)
        pygame.draw.rect(self.screen, (204, 0, 0), borda_rect, 1)
        self.screen.blit(text, text_rect)

        pygame.display.flip()

        # aguarda
        espera()

        # restaura conteúdo anterior
        screen_old.blit(screen_bkp, (0, 0))
        pygame.display.flip()

    def mapa(self):
        saida = ""
        for y in range(self.tam_x):
            if saida <> "":
                saida += "\n"
            for x in range(self.tam_y):
                if self.principal in self._mapa[x][y]:
                    saida += "O"
                elif len(self._mapa[x][y]) > 0:
                    saida += "x"
                else:
                    saida += "."
        return saida


class Objeto(pygame.sprite.Sprite):
    #TODO construtor de cópia
    #TODO criar sem inserir no mundo

    def __init__(self, imagem, x=1, y=1, pasta=None, velocidade=VELOCIDADE):
        # inicializa
        """

        :rtype : object
        """
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = load_image(imagem, pasta)
        self.rect = self.image.get_rect()
        self.velocidade = velocidade
        self._posx = x
        self._posy = y
        self.solido = True
        self._nome = _nomes.pop()

        # insere no mundo
        self.layer = 0
        self.mundo = Mundo()
        self.screen = self.mundo.screen
        self.mundo.adiciona(self)

        # posiciona
        self.move_para(x, y)

    def get_x(self):
        return self._posx

    def get_y(self):
        return self._posy

    x = property(get_x)
    y = property(get_y)

    # redimensiona a imagem
    def redimensiona(self, tamanho):
        self.image = resize_image(self.image, tamanho)
        img_rect = self.image.get_rect()
        img_rect.center = self.rect.center
        self.rect = img_rect

    # retorna a posição (x,y)
    def get_pos(self):
        return (self.x, self.y)

    # testa se a casa apontada está vazia
    def vazio(self, direcao):
        x, y = direcao
        return self.mundo.get_vazio(self.x + x, self.y + y, self)

    def fim(self, direcao):
        x, y = direcao
        return self.mundo.get_fim(self.x + x, self.y + y)

    # move para a posição x,y no mundo
    def move_para(self, x, y):
        # atualiza o mundo
        self.mundo.move_objeto(self, x, y)
        # atualiza o objeto
        self._posx = x
        self._posy = y
        mundo_rect = self.mundo.get_rect(x, y)
        self.rect.center = mundo_rect.center
        # redesenha a tela
        self.mundo.atualiza()

    # faz o objeto explodir
    def explodir(self, mensagem):
        # salva a imagem antiga
        old_image = self.image

        # coloca a explosão e redimensiona
        self.image = load_image("explosion.png", DATA_DIR)

        # self.rect = self.image.get_rect()
        self.redimensiona(self.mundo.ladrilho)

        # cola a explosão sobre a antiga
        old_image.blit(self.image, (0, 0))

        # atualiza a imagem com a versao explodida
        self.image = old_image

        # atualiza a tela
        self.mundo.atualiza()

        # mostra a mensagem
        self.dizer(mensagem)

        # cai fora
        acabou()


    # anda na direção informada
    def andar(self, direcao):

        if self.mundo.espera:
            espera()

        x, y = direcao

        if ((self.x + x > self.mundo.tam_x) or (self.y + y > self.mundo.tam_y)
            or (self.x + x < 1) or (self.y + y < 1)):
            self.explodir(u"ERRO: Você caiu para fora do tabuleiro.")

        else:
            self.move_para(self.x + x, self.y + y)
            if self.mundo.colisao(self):
                self.explodir(u"ERRO: Você esbarrou em um obstáculo")

        pygame.time.wait(self.velocidade)


    def dizer(self, mensagem):
        self.mundo.mostra_msg(self.x, self.y, mensagem)

    def get_valor(self):
        return None

    def get_nome(self):
        return self._nome

    def valor(self, direcao):
        x, y = direcao
        return self.mundo.get_valor(self.x + x, self.y + y, self)

    def nome(self, direcao=None):
        x, y = direcao
        if direcao is None:
            return self.get_nome()
        else:
            return self.mundo.get_nome(self.x + x, self.y + y)

    def objeto(self, direcao):
        x, y = direcao
        obj = self.mundo.get_objetos(self.x + x, self.y + y) + []
        obj.remove(self)
        if len(obj) == 0:
            return None
        else:
            return obj[0]

    def remove(self):
        self.mundo.remove_objeto(self)

        #TODO função que adiciona objeto no mundo


class Robot(Objeto):
    def __init__(self, x=1, y=1):
        Objeto.__init__(self, 'r2d2.png', x, y)
        self.nome = "Juca"


class Inimigo(Objeto):
    def __init__(self, x=1, y=1):
        icon = ("trooper", "vader", "clone-red", "clone-blue", "clone-yellow")[numAleatorio(0, 3)] + ".png"
        Objeto.__init__(self, icon, x, y)


class Vader(Objeto):
    def __init__(self, x=1, y=1):
        Objeto.__init__(self, 'vader.png', x, y)
        self.nome = "Anakin Skywalker"


class Domino(Objeto):
    def __init__(self, x=1, y=1, valor=None):
        # acha o valor
        self.face1 = random.randint(0, 6)
        if valor == None:
            self.face2 = random.randint(0, 6)
        elif valor <= 12:
            while self.face1 > valor:
                self.face1 = random.randint(0, 6)
            while (valor - self.face1) > 6:
                self.face1 = random.randint(0, 6)
            self.face2 = valor - self.face1
        else:
            Erro("Valor do dominó deve ser menor que 12 (%d)" % valor)

        if self.face1 > self.face2:
            self.face1, self.face2 = (self.face2, self.face1)

        self.nome = "%d%d" % (self.face1, self.face2)
        # acha a image
        Objeto.__init__(self, self.nome + ".jpg", x, y)

        # dominós não explodem
        self.solido = False

    def get_valor(self):
        return self.face1 + self.face2


class Parede(Objeto):
    def __init__(self, x, y):
        Objeto.__init__(self, "parede.png", x, y)

class EstrelaMorte(Objeto):
    def __init__(self, x, y):
        Objeto.__init__(self, "estrela-morte.png", x, y)

class Rastro(Objeto):
    def __init__(self, x, y):
        Objeto.__init__(self, "rastro.png", x, y)

class Sabre(Objeto):
    def __init__(self, x, y):
        Objeto.__init__(self, "sabre.png", x, y)

class Portal(Objeto):
    def __init__(self, x, y):
        Objeto.__init__(self, "portal.png", x, y)

class ParedeFloyd(Objeto):
    def __init__(self, x, y):
        Objeto.__init__(self, "brick-wall.png", x, y)


class Moedas(Objeto):
    def __init__(self, x, y, valor=None):
        # cria o objeto
        Objeto.__init__(self, "moedas.png", x, y)
        # evita a explosão quando colide
        self.solido = False
        # chuta um valor
        if valor is None:
            valor = random.randint(1, 100)
        self._valor = valor
        # coloca o valor sobre a imagem
        font_name = os.path.join(FONT_DIR, 'DejaVuSansMono-Bold.ttf')
        font = pygame.font.Font(font_name, 11)
        #font.set_bold(True)
        txt_valor = ("000%d" % valor)[-3:]
        text = font.render(txt_valor, True, (255, 255, 0), (0, 0, 0))
        textpos = text.get_rect()
        textpos.center = self.image.get_rect().center
        textpos = textpos.move(0, 5)
        pygame.draw.rect(self.image, (0, 0, 0), textpos.inflate(2, 2))
        self.image.blit(text, textpos.move(0, 2))


    def get_valor(self):
        return self._valor


class Fantasma(Objeto):
    def __init__(self, x, y):
        num = random.randint(1, 4)
        imagem = "fantasma%d.png" % num
        Objeto.__init__(self, imagem, x, y)
        self.nome = ("", "Perna", "Boca", "Cabeção", "Batata")[num]
        self.mundo.objetos.change_layer(self, 9)
        self.solido = False


# funções
def fim(direcao):
    return Mundo.get_instance().principal.fim(direcao)


def vazio(direcao):
    return Mundo.get_instance().principal.vazio(direcao)


def andar(direcao):
    return Mundo.get_instance().principal.andar(direcao)


def dizer(fala):
    Mundo.get_instance().principal.dizer(fala)


def valor(direcao):
    return Mundo.get_instance().principal.valor(direcao)


def nome(direcao):
    return Mundo.get_instance().principal.nome(direcao)


def objeto(direcao):
    return Mundo.get_instance().principal.objeto(direcao)


def numAleatorio(min, max):
    return random.randint(min, max)


def boolAleatorio(chance=1, em_cada=2):
    return numAleatorio(1, em_cada) <= chance


# retorna a direção contrária
def contrario(direcao):
    return (-direcao[0], -direcao[1])

    #TODO objeto tipo carta, moeda e dado
    #TODO flag para criar objeto sem colocar no mundo
    #TODO mótodo copy para objeto e mundo
    #TODO criar cópia do mundo para reiniciar facilmente
    #TODO balãozinho
    #TODO função pra encher uma linha inteira
    #TODO função para encher uma linha esparsa
    #TODO função para um bloco de vários grudados em posição aleatória
    #TODO programa principal deve ter método inicializa()
    #TODO programa principal deve ter método programa()
    #TODO processar o evento QUIT no meio da execução
    #TODO passar um arquivo texto para gerar os nomes
    #TODO sprites de placar fora do campo
    #TODO animação do movimento
    #TODO tratador de exceções faz _continua=False
    #TODO Letras e números ao redor do tabuleiro
    #TODO colocar titulo na janela
    #TODO casas com texto
    #TODO peça de xadrez de qq cor (branco multiply cor)
    #TODO renomear Mundo para Tabuleiro
    #TODO objeto "digito"
    #TODO calendários e relógios
    #TODO Tooltip com nome e valor dos objetos
    #TODO erro ao redimensionar (olhar erro.py)
    #TODO tipo de objeto ALVO
    #TODO tipo de objeto INIMIGO
    #TODO explosão

    #OK esperar ao final que clique o mouse
    #OK centralizar o dominó
    #OK ERRO de pintura quando tabuleiro é impar
    #OK espera a cada movimento em Mundo()
    # 04 - nov - 09
    #OK permitir criar dominós com valor solicitado 04-nov-09
    #OK criado objeto moeda e parede 04-nov-09
    #OK redimensionar imagem quando é menor que o quadro 04-nov-09
    #OK ERRO de lógica na espera (quit começa o programa)
    #OK se tem ao menos um que tem "valor" retorna senão erro
    #OK objeto.X e objeto.Y são properties
    #OK mundo.tamX e mundoY são properties
    # 05 - nov - 09
    #OK colocar o robot no primeiro plano em inicio()
    #OK função pra inverter a direção
    #OK mostrar números nas moedas