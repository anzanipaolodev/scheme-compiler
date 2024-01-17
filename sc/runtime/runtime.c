#include <stdio.h>
#include <sys/types.h>
#define _GNU_SOURCE
#include <sys/mman.h>
#include <unistd.h>

/* Scheme types tags and masks */
#define bool_f 0x2F
#define bool_t 0x6F
#define null_s 0x3F
#define fx_mask 0x03
#define fx_tag 0x00
#define fx_shift 2
#define char_mask 0x0F
#define char_shift 8
#define char_tag 0x0F
#define char_mask 0x0F

/* Type of Scheme values  */
typedef unsigned int ptr;

static void print_ptr(ptr x){
    if((x & fx_mask) == fx_tag){
        printf("%d", ((int)x) >> fx_shift);
    } else if(x == bool_f){
        printf("#f");
    } else if(x == bool_t){
        printf("#t");
    } else if(x == null_s){
        printf("()");   
    } else if((x & char_mask) == char_tag){
        printf("#\\%c", (char)(x >> char_shift));
    } else {
        printf("#<unknown 0x%08x>", x);
    }
    printf("\n");
}


/* Allocate a specified amount of bytes in memory.
 * This reserves two extra pages to act as guards.
 * Accidently writing or reading beyond the returned memory
 * will casue the program to fault.
 */
static char* allocate_protected_space(int size) {
    int page = getpagesize();
    int status;
    int aligned_size = ((size + page - 1) / page) * page;
    char* p = mmap(NULL, aligned_size + 2 * size, PROT_READ | PROT_WRITE, MAP_ANONYMOUS | MAP_PRIVATE, 0, 0);
    if (p == MAP_FAILED) {
        perror("mmap");
        exit(1);
    }
    status = mprotect(p, page, PROT_NONE);
    if (status != 0) {
        perror("mprotect"); exit(1);
    }
    status = mprotect(p + page + aligned_size, page, PROT_NONE);
    if (status != 0) {
        perror("mprotect"); exit(1);
    }
    return (p + page);
}


/* Free the allocated memory. */
static void deallocate_protected_space(char *p, int size) {
    int page = getpagesize();
    int status;
    int aligned_size = ((size + page - 1) / page) * page;
    status = munmap(p - page, aligned_size + 2 * page);
    if (status != 0) {
        perror("munmap"); exit(1);
    }
}

extern long __cdecl scheme_entry(char* stack_base);

int main(int argc, char** argv){
    int stack_size = (16 * 4096);
    char* stack_top = allocate_protected_space(stack_size);
    char* stack_base = stack_top + stack_size;
    print_ptr(scheme_entry(stack_base));
    deallocate_protected_space(stack_top, stack_size);
}
