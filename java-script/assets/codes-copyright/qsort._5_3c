#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <string.h>
#define MAXIMO 100

int num_aleatorio() {
   int numero = random() % MAXIMO;
   return numero;
}

void geraMatriz(int * a, int n) {
   int i;
   for (i = 0; i < n; ++i) {
      a[i] = num_aleatorio();
   }
}

void imprimeMatriz(int * a, int n) {
   int i;
   for (i = 0; i < n; ++i) {
      printf("%d ", a[i]);
   }
   printf("\n");
}

int cmpfunc (const void * a, const void * b)
{
   return ( *(int*)a - *(int*)b );
}

int main(int argc, char* argv[]) {
   long int number_tosses, number_in_circle;
   int thread_count, i, j, n, count;
   srandom(0);
   thread_count = strtol(argv[1], NULL, 10);
   n = strtol(argv[2], NULL, 10);
   int * a = malloc(n* sizeof(int));
   geraMatriz(a, n);
   //imprimeMatriz(a, n);
   double start = omp_get_wtime();
   qsort(a, n, sizeof(int), cmpfunc);
   double finish = omp_get_wtime();
   printf("Tempo estimado %e segundos\n", finish - start);
   //imprimeMatriz(a, n);
   return 0;
}  /* main */

