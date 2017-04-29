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
#include <math.h>
#include <omp.h>

void Usage(char* prog_name);

#define MAXIMO 20

int num_aleatorio() {
   double numero = random() % MAXIMO;
   if((double) random() / (double) RAND_MAX < 0.5) {
      numero *= -1;
   }
   return numero;
}

void geraMatriz(double * a, int m, int n) {
   int i, j;
   for (i = 0; i < m; i++) {
      for (j = 0; j < n; j++) {
         a[i*n + j] = num_aleatorio();
      }
   }
}

void geraMatrizTriangular(double * a, int m) {
   int i, j;
   for (i = 0; i < m; i++) {
      for (j = 0; j < m; j++) {
         if (j >= i) {
            a[i * m + j] = num_aleatorio();
         } else {
            a[i *m +j] = 0;
         }
      }
   }
}

void imprimeMatriz(double * a, int m, int n) {

   int i, j;
   for (i = 0; i < m; i++) {
      for (j = 0; j < n; j++) {
         printf("%f ", a[i*n + j]);
      }
      printf("\n");
   }
}

int main(int argc, char* argv[]) {
   int thread_count, n;

   if (argc != 3) Usage(argv[0]);
   thread_count = strtol(argv[1], NULL, 10);
   n = strtoll(argv[2], NULL, 10);
   if (thread_count < 1 || n < 1) Usage(argv[0]);

   srandom(0);

   double * a = malloc(n*n* sizeof(double));
   double * b = malloc(n* sizeof(double));
   double * x = malloc(n* sizeof(double));
   geraMatrizTriangular(a, n);
   geraMatriz(b, n, 1);
   imprimeMatriz(a, n, n);
   imprimeMatriz(b, n, 1);

   int row, col;
   double start = omp_get_wtime();

   #pragma omp parallel for num_threads(thread_count) default(none) \
         private(row) shared(x, b, n)
   for (row = 0; row < n; row++) {
      x[row] = b[row];
   }


   for (col = n -1; col >= 0; col--) {
      x[col] /= a[col*n + col];

      #pragma omp parallel for num_threads(thread_count) default(none) \
         private(row) shared(x, b, a, n, col)
      for (row = 0; row < col; row++) {
         x[row] -= a[row*n + col]*x[col];
      }
   }

   double finish = omp_get_wtime();

   //imprimeMatriz(x, n, 1);
   free(a);
   free(b);
   free(x);
   printf("Tempo estimado %e segundos\n", finish - start);
   return 0;
}  /* main */

void Usage(char* prog_name) {
   fprintf(stderr, "usage: %s <thread_count> <n>\n", prog_name);  /* Change */
   exit(0);
}  /* Usage */
