import unittest
from sc.runtime import clangruntime
import sc.helpers
import sc.main

class CompilerTestCase(unittest.TestCase): 
    def setUp(self):
        pass

    def test_fixnum(self): 
        print('Testing FIXNUMS')
        fixnums = [0, 1, -1, 10, -10, 2736, -2736, 536870911, -536870912]
        asm_runtime = clangruntime.compile_c_to_asm()
        for i in range(0, len(fixnums)):
            with self.subTest(i=fixnums[i]):
                program = str(fixnums[i])
                asm_code = sc.main.generate_asm(program)
                compiled_runtime = clangruntime.compile_runtime(asm_runtime, asm_code)
                self.assertEqual(clangruntime.exec_runtime(compiled_runtime).decode('ascii').strip('\n'), str(fixnums[i]))
    
    def test_immediate_constants(self):
        print('Testing IMMEDIATE VALUES') 
        values = list(map(lambda x: '#\\'+ x, sc.helpers.CHARSET))
        values.extend(['#f', '#t', '()'])
        asm_runtime = clangruntime.compile_c_to_asm()
        for i in range(0, len(values)):
            with self.subTest(i=values[i]):
                program = str(values[i])
                asm_code = sc.main.generate_asm(program)
                compiled_runtime = clangruntime.compile_runtime(asm_runtime, asm_code)
                self.assertEqual(clangruntime.exec_runtime(compiled_runtime).decode('ascii'), str(values[i])+'\n')

    def test_unary_primitives(self):
        print('Testing UNARY PRIMITIVES')
        tests_fxadd1 = [
            ('(fxadd1 0)', '1'),
            ('(fxadd1 -1)', '0'),
            ('(fxadd1 1)', '2'),
            ('(fxadd1 -100)', '-99'),
            ('(fxadd1 1000)', '1001'),
            ('(fxadd1 536870910)', '536870911'),
            ('(fxadd1 -536870912)', '-536870911'),
            ('(fxadd1 (fxadd1 0))', '2'),
            ('(fxadd1 (fxadd1 (fxadd1 (fxadd1 (fxadd1 (fxadd1 12))))))', '18'),
        ]
        tests_fixnum_char = [
            ('(fixnum->char 65)', '#\\A'),
            ('(fixnum->char 97)', '#\\a'),
            ('(fixnum->char 122)', '#\\z'),
            ('(fixnum->char 90)', '#\\Z'),
            ('(fixnum->char 48)', '#\\0'),
            ('(fixnum->char 57)', '#\\9'),
            ('(char->fixnum #\\A)', '65'),
            ('(char->fixnum #\\a)', '97'),
            ('(char->fixnum #\\z)', '122'),
            ('(char->fixnum #\\Z)', '90'),
            ('(char->fixnum #\\0)', '48'),
            ('(char->fixnum #\\9)', '57'),
            ('(char->fixnum (fixnum->char 12))', '12'),
            ('(fixnum->char (char->fixnum #\\x))', '#\\x'),
        ]
        tests_fixnum_check = [
            ('(fixnum? 0)', '#t'),
            ('(fixnum? 1)', '#t'),
            ('(fixnum? -1)', '#t'),
            ('(fixnum? 37287)', '#t'),
            ('(fixnum? -23873)', '#t'),
            ('(fixnum? 536870911)', '#t'),
            ('(fixnum? -536870912)', '#t'),
            ('(fixnum? #t)', '#f'),
            ('(fixnum? #f)', '#f'),
            ('(fixnum? ())', '#f'),
            ('(fixnum? #\\Q)', '#f'),
            ('(fixnum? (fixnum? 12))', '#f'),
            ('(fixnum? (fixnum? #f))', '#f'),
            ('(fixnum? (fixnum? #\\A))', '#f'),
            ('(fixnum? (char->fixnum #\\r))', '#t'),
            ('(fixnum? (fixnum->char 12))', '#f'),
        ]
        tests_fxzero_check = [
            ('(fxzero? 0)', '#t'),
            ('(fxzero? 1)', '#f'),
            ('(fxzero? -1)', '#f'),
        ]
        tests_null_check = [
            ('(null? ())', '#t'),
            ('(null? #f)', '#f'),
            ('(null? #t)', '#f'),
            ('(null? (null? ()))', '#f'),
            ('(null? #\\a)', '#f'),
            ('(null? 0)', '#f'),
            ('(null? -10)', '#f'),
            ('(null? 10)', '#f'),
        ]
        tests_boolean_check = [
            ('(boolean? #t)', '#t'),
            ('(boolean? #f)', '#t'),
            ('(boolean? 0)', '#f'),
            ('(boolean? 1)', '#f'),
            ('(boolean? -1)', '#f'),
            ('(boolean? ())', '#f'),
            ('(boolean? #\\a)', '#f'),
            ('(boolean? (boolean? 0))', '#t'),
            ('(boolean? (fixnum? (boolean? 0)))', '#t'),
        ]
        tests_char_check = [
            ('(char? #\\a)', '#t'),
            ('(char? #\\Z)', '#t'),
            ('(char? #\\\n)', '#t'),
            ('(char? #t)', '#f'),
            ('(char? #f)', '#f'),
            ('(char? ())', '#f'),
            ('(char? (char? #t))', '#f'),
            ('(char? 0)', '#f'),
            ('(char? 23870)', '#f'),
            ('(char? -23789)', '#f'),
        ]
        tests_not = [
            ('(not #t)', '#f'),
            ('(not #f)', '#t'),
            ('(not 15)', '#f'),
            ('(not ())', '#f'),
            ('(not #\\A)', '#f'),
            ('(not (not #t))', '#t'),
            ('(not (not #f))', '#f'),
            ('(not (not 15))', '#t'),
            ('(not (fixnum? 15))', '#f'),
            ('(not (fixnum? #f))', '#t'),
        ]
        tests_fxlognot = [
             ('(fxlognot 0)', "-1"),
             ('(fxlognot -1)', "0"),
             ('(fxlognot 1)', "-2"),
             ('(fxlognot -2)', "1"),
             ('(fxlognot 536870911)', "-536870912"),
             ('(fxlognot -536870912)', "536870911"),
             ('(fxlognot (fxlognot 237463))', "237463"),
        ]
        tests = {
            *tests_fxadd1,
            *tests_fixnum_char,
            *tests_fixnum_check,
            *tests_fxzero_check,
            *tests_null_check,
            *tests_boolean_check,
            *tests_char_check,
            *tests_not,
            *tests_fxlognot,
        }
        asm_runtime = clangruntime.compile_c_to_asm()
        for test in tests:
            with self.subTest(i=test[0]):
                program = str(test[0])
                asm_code = sc.main.generate_asm(program)
                compiled_runtime = clangruntime.compile_runtime(asm_runtime, asm_code)
                self.assertEqual(clangruntime.exec_runtime(compiled_runtime).decode('ascii'), str(test[1])+'\n')
        
    def test_if_statement(self): 
        print('Testing IF STATEMENT')
        if_tests = [
            ('(if #t 12 13)', '12'),
            ('(if #f 12 13)', '13'),
            ('(if 0 12 13)', '12'),
            ('(if () 43 ())', '43'),
            ('(if #t (if 12 13 4) 17)', '13'),
            ('(if #f 12 (if #f 13 4))', '4'),
            ('(if #\\X (if 1 2 3) (if 4 5 6))', '2'),
            ('(if (not (boolean? #t)) 15 (boolean? #f))', '#t'),
            ('(if (if (char? #\\a) (boolean? #\\b) (fixnum? #\\c)) 119 -23)', '-23'),
            ('(if (if (if (not 1) (not 2) (not 3)) 4 5) 6 7)', '6'),
            ('(if (not (if (if (not 1) (not 2) (not 3)) 4 5)) 6 7)', '7'),
            ('(not (if (not (if (if (not 1) (not 2) (not 3)) 4 5)) 6 7))', '#f'),
            ('(if (char? 12) 13 14)', '14'),
            ('(if (char? #\\a) 13 14)', '13'),
            ('(fxadd1 (if (fxsub1 1) (fxsub1 13) 14))', '13'),
        ]
        tests = {
            *if_tests,
        }
        asm_runtime = clangruntime.compile_c_to_asm()
        for test in tests:
            with self.subTest(i=test[0]):
                program = str(test[0])
                asm_code = sc.main.generate_asm(program)
                compiled_runtime = clangruntime.compile_runtime(asm_runtime, asm_code)
                self.assertEqual(clangruntime.exec_runtime(compiled_runtime).decode('ascii'), str(test[1])+'\n')

