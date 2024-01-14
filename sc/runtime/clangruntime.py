import subprocess, pathlib, tempfile, os

DEFAULT_CLANG_RUNTIME = '''
#include <stdio.h>
/* define all scheme constants */
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
/* all scheme values are of type ptrs */
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
        printf("#\\\%c", (char)(x >> char_shift));
    } else {
        printf("#<unknown 0x%08x>", x);
    }
    printf("\\n");
}
int main(int argc, char** argv){
    print_ptr(scheme_entry());
}
'''

def compile_c_to_asm(c_source:str=DEFAULT_CLANG_RUNTIME) -> str:
    output = subprocess.check_output(args=f'clang -O3 -fomit-frame-pointer -Wno-implicit-function-declaration -S -x c - -o -'.split(), input=c_source.encode('utf-8'), stderr=None)
    return output.decode('utf-8')


def compile_runtime(runtime_asm:str, scheme_entry_asm:str) -> bytes: 
    output = subprocess.check_output(args=f'clang -O3 -fomit-frame-pointer -Wno-unused-command-line-argument -Wno-implicit-function-declaration -x assembler - -o /dev/stdout'.split(), input=str(runtime_asm+scheme_entry_asm).encode('utf-8'), stderr=None)
    return output

# TODO: Write something to run directly from memory
def exec_runtime(compiled_runtime:bytes) -> bytes: 
    with tempfile.NamedTemporaryFile(delete=True) as execfile:
        execfile.write(compiled_runtime)
        subprocess.run(args=f'chmod +x {execfile.name}'.split())
        return bytes(subprocess.check_output(execfile.name, shell=True))
