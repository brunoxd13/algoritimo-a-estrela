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
int thread_count, message_avaliable;  
pthread_mutex_t mutex;

void Usage(char* prog_name);
void *Hello(void* rank);  /* Thread function */

/*--------------------------------------------------------------------*/
int main(int argc, char* argv[]) {
   long       thread;  /* Use long in case of a 64-bit system */
   pthread_t* thread_handles;

   /* Pega o número de threads da linha de comando */
   if (argc != 2) Usage(argv[0]);
   thread_count = strtol(argv[1], NULL, 10);  
   if (thread_count <= 0 || thread_count > MAX_THREADS) Usage(argv[0]); 
   
   //Inicializa a flag para falso, a fim de dizer ao consumidor que ele tem que esperar pelo produtor
   message_avaliable = 0;

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
        if(message_avaliable == 0){
           printf("Produtor %li criou mensagem\n",my_rank);
           message_avaliable = 1;
           pthread_mutex_unlock(&mutex);
           break;
        }else{
           printf("Consumidor %li imprimiu mensagem\n",my_rank);
           message_avaliable = 0;
           pthread_mutex_unlock(&mutex);
           break;
	     }
   }

   return NULL;
}  /* Hello */

/*-------------------------------------------------------------------*/
void Usage(char* prog_name) {
   fprintf(stderr, "usage: %s <number of threads>\n", prog_name);
   fprintf(stderr, "0 < number of threads <= %d\n", MAX_THREADS);
   exit(0);
}  /* Usage */
