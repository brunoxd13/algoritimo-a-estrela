#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

int geraSendCounts(int p, int n, int sendCounts[], int displs[]);

void Print_list(int a[], int n) {
    int i;

    for (i = 0; i < n; i++)
        printf("%d ", a[i]);
    printf("\n\n");
}  /* Print_list */

int main(void) {
    int n; //Tamanho dos vetores
    int local_n; //Tamanho do vetor dividido
    int i; //variavel auxiliar
    int escalar; //Escalar
    int* vetor1 = NULL; //Primeiro vetor
    int* vetor2 = NULL; //Segundo vetor
    int* local_vetor1; //Parte do vetor 1 em um processo
    int* local_vetor2; //Parte do vetor 2 em um processo
    int local_soma = 0; // Soma local
    int resultado = 0; //Resultado final
    int        comm_sz;               /* Numero de processos    */
    int        my_rank;               /* Rank do meu processo       */

    /* Inicia o MPI */
    MPI_Init(NULL, NULL);

    /* Pega o numero de processos */
    MPI_Comm_size(MPI_COMM_WORLD, &comm_sz);

    /* Pega meu rank diante de todos os processos */
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

    //Calcula o local_n
    if (my_rank == 0) {
        printf("Entre com o tamanho dos vetores\n");
        scanf("%d", &n);
        printf("Entre com o escalar\n");
        scanf("%d", &escalar);
    }

    MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast(&escalar, 1, MPI_INT, 0, MPI_COMM_WORLD);

    if(my_rank < (n % comm_sz))
    {
        local_n = n / comm_sz + 1;
    }
    else
    {
        local_n = n / comm_sz;
    }

    //Aloca os vetores
    vetor1 = (int*)malloc(n*sizeof(int));
    vetor2 = (int*)malloc(n*sizeof(int));
    local_vetor1 = (int*)malloc(local_n*sizeof(int));
    local_vetor2 = (int*)malloc(local_n*sizeof(int));

    int * sendCounts = (int*)malloc(comm_sz*sizeof(int));
    int * displs = (int*)malloc(comm_sz*sizeof(int));
    geraSendCounts(comm_sz, n, sendCounts, displs);

    //Preenche os vetores e os distribui
    if(my_rank == 0){
        printf("Digite o primeiro vetor\n");
        for(i=0;i<n;i++)
            scanf("%d",&vetor1[i]);
        printf("Digite o segundo vetor\n");
        for(i=0;i<n;i++)
            scanf("%d",&vetor2[i]);

    }
    MPI_Scatterv(vetor1, sendCounts, displs, MPI_INT,
                 local_vetor1, local_n, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Scatterv(vetor2, sendCounts, displs, MPI_INT,
                 local_vetor2, local_n, MPI_INT, 0, MPI_COMM_WORLD);
    free(vetor1);
    free(vetor2);

    //Calcula as somas locais
    for(i=0;i<local_n;i++){
        local_vetor1[i] *= escalar;
        local_vetor1[i] *= local_vetor2[i];
        local_soma += local_vetor1[i];
    }

    //Adiciona as somas locais no resultado
    MPI_Reduce(&local_soma, &resultado, 1, MPI_INT, MPI_SUM, 0,
               MPI_COMM_WORLD);

    if(my_rank == 0){
        printf("O resultado final: %d\n",resultado);
        free(local_vetor1);
        free(local_vetor2);
    }

    /* Finaliza o MPI */
    MPI_Finalize();

    return 0;
}  /* main */

int geraSendCounts(int p, int n, int sendCounts[], int displs[]) {

    int local_n = n / p;
    int i;
    for (i = 0; i < p; i++) {
        if(i < (n % p))
        {
            sendCounts[i] = local_n +1;
            displs[i] = i*(local_n + 1);
        }
        else
        {
            sendCounts[i] = local_n;
            displs[i] = i*(local_n) + n % p;
        }
    }
}
