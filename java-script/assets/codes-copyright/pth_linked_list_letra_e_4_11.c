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

struct list_node_s {
   int    data;
   struct list_node_s* next;
};

int thread_count;
pthread_barrier_t barrier_p;
struct list_node_s* head_p = NULL;  /* start with empty list */

int  Insert(int value, struct list_node_s** head_p);
void Print(struct list_node_s* head_p);
int  Member(int value, struct list_node_s* head_p);
int  Delete(int value, struct list_node_s** head_p);
void Free_list(struct list_node_s** head_p);
int  Is_empty(struct list_node_s* head_p);
char Get_command(void);
int  Get_value(void);
void *Thread_work(void* rank);

/*-----------------------------------------------------------------*/
int main(void) {
   long thread;
   pthread_t* thread_handles; 
   
   thread_count = 2;
    
   thread_handles = malloc (thread_count*sizeof(pthread_t));

   pthread_barrier_init(&barrier_p,NULL,thread_count);
   
   for (thread = 0; thread < thread_count; thread++)
      pthread_create(&thread_handles[thread], NULL,
          Thread_work, (void*) thread);

   for (thread = 0; thread < thread_count; thread++) {
      pthread_join(thread_handles[thread], NULL);
   }	   
   
   pthread_barrier_destroy(&barrier_p);
   Free_list(&head_p);
   free(thread_handles);
   return 0;
}  /* main */


/*-----------------------------------------------------------------*/
/* Function:   Insert
 * Purpose:    Insert value in correct numerical location 
 *             into list.  If value is already in the list, 
 *             print a message and return 
 * In arg:     value, the value to be inserted            
 * In/out arg: head_pp, a pointer to the head of the list pointer
 * Return val: 1 if value was inserted, 0 otherwise
 */            
int Insert(int value, struct list_node_s** head_pp) {
   struct list_node_s* curr_p = *head_pp;
   struct list_node_s* pred_p = NULL;
   struct list_node_s* temp_p;
   
   while (curr_p != NULL && curr_p->data < value) {
      pred_p = curr_p;
      curr_p = curr_p->next;
   }

   if (curr_p == NULL || curr_p->data > value) {
      temp_p = malloc(sizeof(struct list_node_s));
      temp_p->data = value;
      temp_p->next = curr_p;
      if (pred_p == NULL)
         *head_pp = temp_p;
      else
         pred_p->next = temp_p;
      return 1;
   } else { /* value in list */
      printf("%d is already in the list\n", value);
      return 0;
   }
}  /* Insert */

/*-----------------------------------------------------------------*/
/* Function:  Print
 * Purpose:   Print the contents of the list
 * In arg:    head_p, pointer to the head of the list
 */
void Print(struct list_node_s* head_p) {
   struct list_node_s* curr_p;

   printf("list = ");

   curr_p = head_p;
   while (curr_p != (struct list_node_s*) NULL) {
      printf("%d ", curr_p->data);
      curr_p = curr_p->next;
   }
   printf("\n");
}  /* Print */


/*-----------------------------------------------------------------*/
/* Function:    Member
 * Purpose:     Search list for value
 * In args:     value, the value to be searched for
 *              head_p, pointer to the head of the list  
 * Return val:  true, if value is in the list, false otherwise
 */
int  Member(int value, struct list_node_s* head_p) {
   struct list_node_s* curr_p;

   curr_p = head_p;
   while (curr_p != NULL && curr_p->data < value)
      curr_p = curr_p->next;

   if (curr_p == NULL || curr_p->data > value) {
      printf("%d is not in the list\n", value);
      return 0;
   } else {
      printf("%d is in the list\n", value);
      return 1;
   }
}  /* Member */

/*-----------------------------------------------------------------*/
/* Function:    Delete
 * Purpose:     If value is in the list, delete it.  Otherwise, just
 *              return.
 * In arg:      value, the value to be deleted
 * In/out arg:  head_pp, pointer to the head of the list pointer
 * Return val:  1 if value is deleted, 0 otherwise
 */
int Delete(int value, struct list_node_s** head_pp) {
   struct list_node_s* curr_p = *head_pp;
   struct list_node_s* pred_p = NULL;

   /* Find value */
   while (curr_p != NULL && curr_p->data < value) {
      pred_p = curr_p;
      curr_p = curr_p->next;
   }
   
   if (curr_p != NULL && curr_p->data == value) {
      if (pred_p == NULL) { /* first element in list */
         *head_pp = curr_p->next;
#        ifdef DEBUG
         printf("Freeing %d\n", value);
#        endif
         free(curr_p);
      } else { 
         pred_p->next = curr_p->next;
#        ifdef DEBUG
         printf("Freeing %d\n", value);
#        endif
         free(curr_p);
      }
      return 1;
   } else {
   printf("%d is not in the list\n", value);
      return 0;
   }
}  /* Delete */

/*-----------------------------------------------------------------*/
/* Function:   Free_list
 * Purpose:    Free the storage used by the list
 * In/out arg: head_pp, pointer to the head of the list pointer
 *               on input, NULL on return
 */
void Free_list(struct list_node_s** head_pp) {
   struct list_node_s* curr_p;
   struct list_node_s* succ_p;

   if (Is_empty(*head_pp)) return;
   curr_p = *head_pp; 
   succ_p = curr_p->next;
   while (succ_p != NULL) {
#     ifdef DEBUG
      printf("Freeing %d\n", curr_p->data);
#     endif
      free(curr_p);
      curr_p = succ_p;
      succ_p = curr_p->next;
   }
#  ifdef DEBUG
   printf("Freeing %d\n", curr_p->data);
#  endif
   free(curr_p);
   *head_pp = NULL;
}  /* Free_list */

/*-----------------------------------------------------------------*/
/* Function:    Is_empty
 * Purpose:     Determine whether the list is empty
 * In arg:      head_p:  head of list pointer
 * Return val:  true, if head_p is NULL, false otherwise
 */
int  Is_empty(struct list_node_s* head_p) {
   if (head_p == NULL)
      return 1;
   else
      return 0;
}  /* Is_empty */

/*-----------------------------------------------------------------*/
/* Function:    Get_command
 * Purpose:     Get the next command (a single char) from stdin
 * Return val:  The next nonwhite char in stdin
 */
char Get_command(void) {
   char c;

   printf("Please enter a command:  ");
   /* Put the space before the %c so scanf will skip white space */
   scanf(" %c", &c);
   return c;
}  /* Get_command */

/*-----------------------------------------------------------------*/
/* Function;      Get_value
 * Purpose:       Get an int from stdin
 * Return value:  The int
 */
int  Get_value(void) {
   int val;

   printf("Please enter a value:  ");
   scanf("%d", &val);
   return val;
}  /* Get_value */

void *Thread_work(void* rank) {
   long my_rank = (long) my_rank;
   
   pthread_barrier_wait(&barrier_p);
   if(my_rank == 0){
   	Insert(8,&head_p);
   }else{
	Member(8,head_p);
   }

   return NULL;
}  /* Thread_work */
