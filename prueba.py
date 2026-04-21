from lexico import *
from sintactico import * 
from semantico import *

codigoPrueba = """
inicio
    a = 10
    b = 20
    c = a + b * 2
    si (c > 30) entonces
        escribir(c)
        d = c - 10
    finsi
    escribir(d)
fin
"""

tokens = identificarTokens(codigoPrueba)

print("========= Elementos ==========")
for elemento in tokens:
    print(f"{elemento}\n")

print("=======Analisis Sintactico ===========")
# Análisis sintáctico
try:
    print("Iniciando analisis sintactico")
    parser = Parse(tokens)
    arbol_ast = parser.parsear()
    print("Analisis sintactico exitoso")
    print("==========Asembler=========")
    print(arbol_ast.generarCodigo)
except SyntaxError as e:
    print(f"Error sintáctico: {e}")
