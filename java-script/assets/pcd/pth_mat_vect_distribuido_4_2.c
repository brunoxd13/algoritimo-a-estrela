/* File:     
 *     pth_mat_vect.c 
 *
 * Purpose:  
 *     Computes a parallel matrix-vector product.  Matrix
 *     is distributed by block rows.  Vectors are distributed by 
 *     blocks.
 *
 * Input:
 *     m, n: order of matrix
 *     A, x: the matrix and the vector to be multiplied
 *
 * Output:
 *     y: the product vector
 *
 * Compile:  gcc -g -Wall -o pth_mat_vect pth_mat_vect.c -lpthread
 * Usage:
 *     pth_mat_vect <thread_count>
 *
 * Notes:  
 *     1.  Local storage for A, x, y is dynamically allocated.
 *     2.  Number of threads (thread_count) should evenly divide both 
 *         m and n.  The program doesn't check for this.
 *     3.  We use a 1-dimensional array for A and compute subscripts
 *         using the formula A[i][j] = A[i*n + j]
 *     4.  Distribution of A, x, and y is logical:  all three are 
 *         globally shared.
 *
 * IPP:    Section 4.3 (pp. 159 and ff.).  Also Section 4.10 (pp. 191 and 
 *         ff.)
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "timer.h"

/* Global variables */
int     thread_count;
int     m, n;
double* A;
double* x;
double* y;

/* Serial functions */
void Usage(char* prog_name);
void Read_matrix(char* prompt, double A[], int m, int n);
void Read_vector(char* prompt, double x[], int n);
void Print_matrix(char* title, double A[], int m, int n);
void Print_vector(char* title, double y[], double m);

#define MAXIMO 100

int num_aleatorio() {
   int numero = random() % MAXIMO;
   return numero;
}

void geraMatriz(double * a, int n, int m) {
   int i, j;
   for (i = 0; i < n; ++i) {
      for (j = 0; j < m; j++) {
         a[i*m + j] = num_aleatorio();
      }
   }
}

void geraVetor(double * a, int m) {
   int i, j;
   for (i = 0; i < m; ++i) {
         a[i] = num_aleatorio();
   }
}

/* Parallel function */
void *Pth_mat_vect(void* rank);

/*------------------------------------------------------------------*/
int main(int argc, char* argv[]) {
   long       thread;
   pthread_t* thread_handles;
   double start, finish, elapsed;

   if (argc != 2) Usage(argv[0]);
   thread_count = atoi(argv[1]);
   thread_handles = malloc(thread_count*sizeof(pthread_t));

   printf("Enter m and n\n");
   scanf("%d%d", &m, &n);

   A = malloc(m*n*sizeof(double));
   x = malloc(n*sizeof(double));
   y = malloc(m*sizeof(double));
   
   geraMatriz(A, m, n);

   geraVetor(x, n);

   GET_TIME(start);

   for (thread = 0; thread < thread_count; thread++)
      pthread_create(&thread_handles[thread], NULL,
         Pth_mat_vect, (void*) thread);

   for (thread = 0; thread < thread_count; thread++)
      pthread_join(thread_handles[thread], NULL);

   GET_TIME(finish);
   elapsed = finish - start;

   printf("Tempo decorrido = %e segundos\n", elapsed);

   free(A);
   free(x);
   free(y);

   return 0;
}  /* main */


/*------------------------------------------------------------------
 * Function:  Usage
 * Purpose:   print a message showing what the command line should
 *            be, and terminate
 * In arg :   prog_name
 */
void Usage (char* prog_name) {
   fprintf(stderr, "usage: %s <thread_count>\n", prog_name);
   exit(0);
}  /* Usage */

/*------------------------------------------------------------------
 * Function:    Read_matrix
 * Purpose:     Read in the matrix
 * In args:     prompt, m, n
 * Out arg:     A
 */
void Read_matrix(char* prompt, double A[], int m, int n) {
   int             i, j;

   printf("%s\n", prompt);
   for (i = 0; i < m; i++) 
      for (j = 0; j < n; j++)
         scanf("%lf", &A[i*n+j]);
}  /* Read_matrix */


/*------------------------------------------------------------------
 * Function:        Read_vector
 * Purpose:         Read in the vector x
 * In arg:          prompt, n
 * Out arg:         x
 */
void Read_vector(char* prompt, double x[], int n) {
   int   i;

   printf("%s\n", prompt);
   for (i = 0; i < n; i++) 
      scanf("%lf", &x[i]);
}  /* Read_vector */


/*------------------------------------------------------------------
 * Function:       Pth_mat_vect
 * Purpose:        Multiply an mxn matrix by an nx1 column vector
 * In arg:         rank
 * Global in vars: A, x, m, n, thread_count
 * Global out var: y
 */
void *Pth_mat_vect(void* rank) {
   long my_rank = (long) rank;
   int i, j;
   int local_m = m/thread_count; //Divisão das linhas de A
   int local_n = n/thread_count; //Divisão do vetor y
   int my_first_row;
   int my_last_row; 
   int my_first_column;
   int my_last_column;
   double* local_y; //Vetor produto local
   double* local_A; //Matriz A local
      
   //Distribuição das linhas da matriz A
   if(my_rank < (m % thread_count)){	//Se minha thread atual
      // tem um my_rank menor que o resto da divisao de m pelo thread_count,
      // então ela recebe o resto da divisão
	local_m++;
	my_first_row = my_rank*local_m;
        my_last_row = (my_rank+1)*local_m - 1;
   }else{
      //Para as outras threads, adicionar o resto para compensaros local_m+1 das outras threads
        my_first_row = my_rank*local_m + (m % thread_count);
        my_last_row = (my_rank+1)*local_m - 1 + (m % thread_count);
   }

   //Distribuição do vetor y
   if(my_rank < (n % thread_count)){
      //Se minha thread atual tem um my_rank menor que
      // o resto da divisao de n pelo thread_count, então ela recebe o resto da divisão
	local_n++;
	my_first_column = my_rank*local_n;
        my_last_column = (my_rank+1)*local_n - 1;
   }else{ //Para as outras threads, adicionar o resto para compensar os local_m+1 das outras threads
        my_first_column = my_rank*local_n + (n % thread_count);
        my_last_column = (my_rank+1)*local_n - 1 + (n % thread_count);
   }

   //Aloca memória
   local_A = malloc(local_m*n*sizeof(double));
   local_y = malloc(local_n*sizeof(double));

   //Realiza as atribuições do local_A
   for(i=0;i<local_m;i++){
      for (j = 0; j < n; j++){
	local_A[i*n + j] = A[my_first_row*n+j];
      }
      my_first_row++; 
   }

   //Realiza o cálculo local
   for (i = 0; i < local_m; i++) {
      local_y[i] = 0.0;
      for (j = 0; j < local_n; j++)
          local_y[i] += local_A[i*n+j]*x[j];
   }

   //Junta o resultado novamente
   for (i = 0; i < local_n; i++) {
	y[my_first_column] = local_y[i];
        my_first_column++;
   }

   return NULL;
}  /* Pth_mat_vect */


/*------------------------------------------------------------------
 * Function:    Print_matrix
 * Purpose:     Print the matrix
 * In args:     title, A, m, n
 */
void Print_matrix( char* title, double A[], int m, int n) {
   int   i, j;

   printf("%s\n", title);
   for (i = 0; i < m; i++) {
      for (j = 0; j < n; j++)
         printf("%4.1f ", A[i*n + j]);
      printf("\n");
   }
}  /* Print_matrix */


/*------------------------------------------------------------------
 * Function:    Print_vector
 * Purpose:     Print a vector
 * In args:     title, y, m
 */
void Print_vector(char* title, double y[], double m) {
   int   i;

   printf("%s\n", title);
   for (i = 0; i < m; i++)
      printf("%4.1f ", y[i]);
   printf("\n");
}  /* Print_vector */
