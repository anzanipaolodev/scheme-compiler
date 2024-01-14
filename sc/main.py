import sys, argparse
sys.path.append(".")
import sc.parser
import sc.code_generator
import sc.runtime.clangruntime


def stdin() -> str:
    return sys.stdin.read().strip()


def write_output(data:str|bytes, dest:str) -> None:
    if dest == '-':
        output = sys.stdout
        output.write(str(data)+'\n')
        return
    else:
        out_path = 'a.out' if not args.output else args.output
        with open(out_path, 'wb') as output:
            output.write(data)
        return


# Usefull as wrapping function to write tests
def generate_asm(input_str:str) -> str:
    parser = sc.parser.Parser()
    root_node = parser.run(input_str)
    asm_code = sc.code_generator.compile_to_asm(root_node)
    return asm_code


parser = argparse.ArgumentParser(prog='sc', description='Compiler for Scheme')
parser.add_argument('filename', type=str)
parser.add_argument('-o', '--output', type=str)
parser.add_argument('-d', '--debug', action='store_true')
parser.add_argument('-S', '--asm', action='store_true')

if  __name__ == "__main__":
    # ***** Read input  *****
    args = parser.parse_args() 
    debug = args.debug
    if args.filename == '-':
        input_str = stdin()
    else:
        with open(args.filename, 'r') as f:
            input_str = f.read() 
    # ***** Generate Code ***** 
    asm_code = generate_asm(input_str)
    if args.asm:
        write_output(asm_code, args.output)
        sys.exit(0)
    # ***** Create Executable *****
    runtime_asm = sc.runtime.clangruntime.compile_c_to_asm()
    executable = sc.runtime.clangruntime.compile_runtime(runtime_asm, asm_code)
    write_output(executable, args.output)
