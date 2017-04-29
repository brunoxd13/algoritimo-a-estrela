# algoritimo-a-estrela


O trabalho consiste na implementação de um agente capaz de guiar um rato através de um labirinto utilizando o Algoritmo busca heurística A* para planejar o caminho.
O rato percorre o labirinto em busca da saída, e no decorrer do caminho encontra e come alguns pedaços de queijo. O rato anda somente uma casa por vez, podendo se deslocar somente à direita, esquerda, para cima e para baixo, nunca na diagonal, desde que não tenha parede no caminho. O labirinto é codi cado como uma matriz bidimensional de caracteres, na qual, as casas (células da matriz) livres são marcadas com o caractere '.' (ponto  nal), as paredes, com o caractere '#' (cerquilha), a posição de saída com o caractere 'S' (maiúsculo), as posições com queijo com o caractere 'Q' (maiúsculo), a posição inicial do rato, é indicada pelo caractere 'R' (maiúsculo). O labirinto deve ser todo cercado por paredes (caractere '#'), exceto na saída ('S').
Os labirintos serão armazenados em arquivos de extensão .txt e podem ter tamanhos diferentes. Esses arquivos, quando lidos, devem ser armazenados em matrizes. Cada arquivo representa somente um labirinto e está estrutudado da seguinte forma: a primeira linha do arquivo é composta de dois números que contém a quantidade de colunas e de linhas da matriz, respectivamente; as linhas seguintes representam os elementos que de nem o labirinto. Observação: o caractere de terminação de linha '\n' deve ser ignorado.
A seguir são apresentados dois exemplos de arquivos de entrada:

	5 5 
	##### 
	#R.Q# 
	###.# 
	SQ.Q# 
	#####

	40 13
	########################################
	#R..............Q...........#...#......#
	#.#.#.#.#.##.#.#.######.#.#...#.#.#.##.#
	#.#.#####.##.#.#......#.#.#.#..........S
	#.#...#.#.####.#.####.......##.#.#.###.#
	#.######.....##.#......####.##.#.#.#.#.#
	#.############.#.##########.##.#.###.#.#
	#.#............Q..........#.....Q......#
	#.##.##.#.#.#.#.#.#.#.#.#.#.###.#.#.##.#
	#.#...#...#....#....#.....#.#.#...#.##.#
	#.#.#######################.#.###.####.#
	#.............#Q......#.....#..........#
	########################################


O presente trabalho tem valor de 20 pontos na média  nal. O que deve ser feito:
• Implementar um programa em uma linguagem de programação a escolha do grupo, capaz de fazer um rato percorrer um labirinto e encontrar a saída;
• O programa deve possibilitar o carregamento do arquivo de texto que de ne um labirinto, mesmo que seja por linha de comando;
• As seguintes informações devem ser apresentadas ao  nal da execução:   número de passos feitos durante a busca pela saída
  coordenadas percorridas até a saída (xi, yi)
  quantidade de queijos encontrados no percurso.
• Exemplo de saída após execução do primeiro exemplo de entrada:
7 passos no total 11
12
13
23
33
32
31
3 queijos encontrados
• Informações importantes:
  O agente obrigatoriamente deve utilizar o algoritmo de busca especi cado para encontrar o
caminho para chegar a saída;
  Deve existir uma maneira de visualizar os movimentos do agente, mesmo que a interface seja
bem simples. Podendo até mesmo ser uma matriz desenhada e atualizada no console;
  O trabalho pode ser desenvolvido individualmente, ou em grupos de até 3 pessoas;
  Se necessário, será feita a prova de autoria, na qual os membros do grupo serão questionados
individualmente acerca da implementação. Se for detectado que um aluno não contribuiu para
o desenvolvimento do trabalho, este sofrerá penalização na nota  nal.
  Juntamente com o trabalho, deverão ser entregues todos os arquivos necessários, tais como
bibliotecas não nativas, para que o projeto seja executado. Deverá ser especi cado em arquivo adicional (a ser entregue junto com os códigos-fonte) os requisitos para execução do trabalho: Sistema Operacional, versão de interpretador ou compilador utilizado, versões das bibliotecas, e quaisquer outros fatores que possam prejudicar na execução do trabalho, como ocorrido no ambiente de desenvolvimento.
Forma de avaliação
• O trabalho será avaliado a partir dos seguintes itens:
  O trabalho atendeu a todos os requisitos especi cados anteriormente;   O algoritmo de busca foi implementado de forma correta
  O código foi devidamente organizado e comentado;
• Bônus:
  A interface grá ca não é objetivo deste trabalho, porém os grupos que implementarem uma
 boa interface grá ca  seja ela 2D ou 3D para representar o ambiente e as movimentações do agente, receberão até 10 pontos extras na nota.


 Disposições Finais
• A entrega deverá ser realizada via Ambiente Moodle, até o dia 07/05/2017 às 23:59 em tarefa especí ca;
• Comece a fazer este trabalho logo, enquanto o prazo para terminá-lo está tão longe quanto jamais poderá estar.
• Clareza, indentação e comentários no programa tambám vão valer nota.
• Trabalhos copiados serão penalizados com a nota zero.
• As apresentações, quando necessárias, serão agendadas pelo professor individualmente com cada
aluno.
• Serão aceitos trabalhos atrasados, com penalização de 20% da nota  nal para cada dia de atraso, ou
seja, após cinco dias, o grupo terá nota ZERO atribuída.
