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
#include <pthread.h>
#include "timer.h"

const int MAX_THREADS = 1024;


/* Thread function */
void *Thread_function(void* ignore);

/* No use of shared variables */
void Usage(char* prog_name);

double elapsed = 0.0;

pthread_mutex_t mutex;
pthread_barrier_t barrier_p;

int main(int argc, char* argv[]) {
   int        thread_count;
   long       thread;  /* Use long in case of a 64-bit system */
   pthread_t* thread_handles;

   /* Get number of threads from command line */
   if (argc != 2) Usage(argv[0]);
   thread_count = strtol(argv[1], NULL, 10);  
   if (thread_count <= 0 || thread_count > MAX_THREADS) Usage(argv[0]);

   thread_handles = (pthread_t*) malloc (thread_count*sizeof(pthread_t));
   pthread_mutex_init(&mutex, NULL);
   pthread_barrier_init(&barrier_p,NULL,thread_count);

   for (thread = 0; thread < thread_count; thread++)  
      pthread_create(&thread_handles[thread], NULL,
          Thread_function, (void *) thread);  

   for (thread = 0; thread < thread_count; thread++) 
      pthread_join(thread_handles[thread], NULL); 

   printf("O tempo gasto pela thread mais lenta foi %e segundos\n", elapsed);
   
   pthread_barrier_destroy(&barrier_p);
   free(thread_handles);
   pthread_mutex_destroy(&mutex);
   return 0;
}  /* main */

/*-------------------------------------------------------------------*/
void Usage(char* prog_name) {
   fprintf(stderr, "usage: %s <number of threads>\n", prog_name);
   fprintf(stderr, "0 < number of threads <= %d\n", MAX_THREADS);
   exit(0);
}  /* Usage */

/*-------------------------------------------------------------------*/
void* Thread_function(void* rank) {
   long my_rank = (long) rank;
   double my_start, my_finish, my_elapsed;
   pthread_barrier_wait(&barrier_p);
   int i;
   GET_TIME(my_start);
   for (i = 0; i < 100000; i++);
   GET_TIME(my_finish);
   
   my_elapsed = my_finish - my_start;

   pthread_mutex_lock(&mutex);
   if(my_elapsed > elapsed){
	elapsed = my_elapsed;

   }
   pthread_mutex_unlock(&mutex);

   return NULL;
}  /* Thread_function */
