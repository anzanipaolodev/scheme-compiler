import subprocess, pathlib, tempfile, os

file_path = os.path.join(__file__.replace(os.path.basename(__file__), ''), 'runtime.c')
with open(file_path, 'r') as f:
    DEFAULT_CLANG_RUNTIME = f.read()

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
