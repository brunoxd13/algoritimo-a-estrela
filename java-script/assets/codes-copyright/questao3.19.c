/*
   Copyright 2016 -  José Victor Alves de Souza - https://github.com/dudevictor/

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
 */
#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

void lerMatriz(double* matriz, int n);
void imprimeMatrix(double* matriz, int tamanho);
void constroiTipoIndexado(double* matriz, int n, MPI_Datatype* novoTipoConstruido);
void recebeN(int * n, int my_rank, MPI_Comm mpi_comm);

int main(void) {
    int my_rank, comm_sz;
    int n;
    MPI_Comm mpi_comm = MPI_COMM_WORLD;
    MPI_Init(NULL, NULL);
    MPI_Comm_size(mpi_comm, &comm_sz);
    MPI_Comm_rank(mpi_comm, &my_rank);

    recebeN(&n, my_rank, mpi_comm);
    double matriz[n*n];
    MPI_Datatype novoTipo;
    constroiTipoIndexado(matriz, n, &novoTipo);
    if (my_rank == 0) {
        lerMatriz(matriz, n);
        MPI_Send(matriz, 1, novoTipo, 1, 0, mpi_comm);
    } else {
        MPI_Recv(matriz, 1, novoTipo, 0, 0, mpi_comm, MPI_STATUS_IGNORE);
        imprimeMatrix(matriz, n);
    }

    MPI_Type_free(&novoTipo);
    MPI_Finalize();
    return 0;
}

void lerMatriz(double* matriz, int tamanho) {
    printf("Digite a matriz n x n:\n");
    int i;
    for (i = 0; i < tamanho; i++) {
        int j;
        for (j = 0; j < tamanho; j++) {

            scanf("%lf", &matriz[i*tamanho+j]);
        }
    }
}


void imprimeMatrix(double* matriz, int tamanho) {
    printf("Matriz:\n");
    int i;
    for (i = 0; i < tamanho; i++) {
        int j;
        for (j = 0; j < tamanho; j++) {
            printf("%f ", matriz[i*tamanho + j]);
        }
        printf("\n");
    }
}

/**
 * Constroi um tipo indexado do triangulo superior da matriz informada
 * O tipo construído vem no seguinte formato:
 *
 * matriz = [ 0 1 2 ]
 *          [ 3 4 5 ]
 *          [ 6 7 8 ]
 *
 * novoTipoConstruido = ( [ 0 1 2 ],
 *                        [   4 5 ],
 *                        [     8 ] )
 *
 */
void constroiTipoIndexado(double* matriz, int n, MPI_Datatype* novoTipoConstruido) {
    int array_tamanhoDosBlocos[n];
    int array_distancias[n];
    array_distancias[0] = 0;
    int i;
    int j;
    for (i = 0, j = n; i < n; i++, j--) {
        // O tamanho dos arrays diminuem -1 a cada linha (triangulo superior)
        array_tamanhoDosBlocos[i] = j;
    }
    for (i = 1; i < n;  i++) {
        //O deslocamento dele é o delslocamento do elementoAtual - o do primeiroElemento
        array_distancias[i] = i*n + i;
    }
    MPI_Type_indexed(n, array_tamanhoDosBlocos, array_distancias, MPI_DOUBLE, novoTipoConstruido);
    MPI_Type_commit(novoTipoConstruido);
}

void recebeN(int * n, int my_rank, MPI_Comm mpi_comm) {
    if (my_rank == 0) {
        printf("Digite o tamanho de n:\n");
        scanf("%d", n);
        MPI_Send(n, 1, MPI_INT, 1, 0, mpi_comm);
    } else {
        MPI_Recv(n, 1, MPI_INT, 0, 0, mpi_comm, MPI_STATUS_IGNORE);
    }
}

