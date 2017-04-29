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
   //imprimeMatriz(a, n, n);
   //imprimeMatriz(b, n, 1);

   int row, col;
   double start = omp_get_wtime();

   for (row = n - 1; row >= 0; row--) {
      x[row] = b[row];

      #pragma omp parallel for num_threads(thread_count) default(none) \
         private(col) shared(x, b, a, n, row)
      for (col = row + 1; col < n ; col++) {
         double valor = a[row*n + col]*x[col];
         #pragma omp critical
         x[row] -= valor;
      }

      x[row] /= a[row*n + row];
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
