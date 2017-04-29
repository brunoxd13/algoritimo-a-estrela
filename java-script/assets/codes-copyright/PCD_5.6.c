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
#include <omp.h>

int main(int argc, char *argv[]) {
	long thread_count;
	int i, iteracoes;

	thread_count = strtol(argv[1], NULL, 10);

	printf("Insira a quantidade de iterações: ");
	scanf("%d", &iteracoes);
	printf("\n");

	# pragma omp parallel num_threads(thread_count)

		# pragma omp for

			for (i = 0; i < iteracoes; ++i) {
				printf("Thread %d - Iteração %d\n", omp_get_thread_num(), i);
			}

	for (i = 0; i < n; i++)
		a[i] = i * (i + 1) / 2;

	#pragma omp parallel for num_threads(thread_count) \
 		default(none) private(i) shared(a, n)
	for (i = 0; i < n; i++)
		a[i] = i * (i + 1) / 2;

	return 0;
}