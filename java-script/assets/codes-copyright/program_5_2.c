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

double num_aleatorio() {
   double numero = (double) random() / (double) RAND_MAX;
   if((double) random() / (double) RAND_MAX < 0.5) {
      numero *= -1;
   }
   return numero;
}

int main(int argc, char* argv[]) {
   long int number_tosses, number_in_circle;
   int thread_count, i;
   double x, y, distancia;

   if (argc != 3) Usage(argv[0]);
   thread_count = strtol(argv[1], NULL, 10);
   number_tosses = strtoll(argv[2], NULL, 10);
   if (thread_count < 1 || number_tosses < 1) Usage(argv[0]);

   number_in_circle =0;
   srandom(0);
#  pragma omp parallel for num_threads(thread_count) \
      reduction(+: number_in_circle) private(x, y, distancia)
   for (i = 0; i < number_tosses; i++) {
      x = num_aleatorio(); // Gera nnumero entre -1 e 1
      y = num_aleatorio();
      distancia = x*x + y*y;

      if (distancia <= 1) {
         number_in_circle += 1;
      }
   }
   double pi = 4*number_in_circle/((double) number_tosses);
   printf("Estimacao de pi = %.14f\n", pi);
   return 0;
}  /* main */

void Usage(char* prog_name) {
   fprintf(stderr, "usage: %s <thread_count> <number_tosses>\n", prog_name);  /* Change */
   exit(0);
}  /* Usage */
