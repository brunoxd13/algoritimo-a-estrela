 /* File:  
 *    pth_hello.c
 *
 * Purpose:
 *    Illustrate basic use of pthreads:  create some threads,
 *    each of which prints a message.
 *
 * Input:
 *    none
 * Output:
 *    message from each thread
 *
 * Compile:  gcc -g -Wall -o pth_hello pth_hello.c -lpthread
 * Usage:    ./pth_hello <thread_count>
 *
 * IPP:   Section 4.2 (p. 153 and ff.)
 */
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h> 

const int MAX_THREADS = 64;

/* Global variable:  accessible to all threads */
int thread_count, message_avaliable, consumer;  
pthread_mutex_t mutex;

void Usage(char* prog_name);
void *Hello(void* rank);  /* Thread function */

/*--------------------------------------------------------------------*/
int main(int argc, char* argv[]) {
   long       thread;  /* Use long in case of a 64-bit system */
   pthread_t* thread_handles; 

   /* Vão ser usadas apenas duas threads */
   thread_count = 2;
   
   //Inicializa a flag para falso, a fim de dizer ao consumidor que ele tem que esperar pelo produtor
   message_avaliable = 0;

   //A thread com my_rank igual a 0 é a consumidora
   consumer = 0;

   thread_handles = malloc (thread_count*sizeof(pthread_t));

   //Inicializa o mutex para proteger a seção crítica de produção e consumo
   pthread_mutex_init(&mutex, NULL); 

   for (thread = 0; thread < thread_count; thread++)  
      pthread_create(&thread_handles[thread], NULL,
          Hello, (void*) thread);  

   for (thread = 0; thread < thread_count; thread++) 
      pthread_join(thread_handles[thread], NULL); 

   free(thread_handles);
   return 0;
}  /* main */

/*-------------------------------------------------------------------*/
void *Hello(void* rank) {
   long my_rank = (long) rank;  /* Use long in case of 64-bit system */ 

   while (1) {
	pthread_mutex_lock(&mutex);
	if (my_rank == consumer) {
		if (message_avaliable) {
			printf("Consumidor imprimiu mensagem\n");
			pthread_mutex_unlock(&mutex);
			break;
		}
	} else { /* my rank == producer */
		printf("Produtor criou mensagem\n");
		message_avaliable = 1;
		pthread_mutex_unlock(&mutex);
		break;
	}
	pthread_mutex_unlock(&mutex);
   }

   return NULL;
}  /* Hello */

/*-------------------------------------------------------------------*/
void Usage(char* prog_name) {
   fprintf(stderr, "usage: %s <number of threads>\n", prog_name);
   fprintf(stderr, "0 < number of threads <= %d\n", MAX_THREADS);
   exit(0);
}  /* Usage */
