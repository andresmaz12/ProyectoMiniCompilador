from lexico import *
from sintactico import * 
from semantico import *

codigoPrueba = """
int x = 10;
void test(int a) {
    int y = a * 2;
    {
        float x = 5.5; 
        y = y + x;
    }
    x = y + 1;
    escribir(z);    
}
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
except SyntaxError as e:
    print(f"Error sintáctico: {e}")

print("=======Analisis Semantico ===========")
try:
    print("Iniciando analisis semantico")
    semantico = AnalizadorSemantico()
    semantico.analizar(arbol_ast)
    print("Analisis semantico exitoso")
except Exception as e:
    print(f"Error semantico: {e}")

print("=======Momentos ===========")
try:
    print(semantico.imprimir_ambitos())
except Exception as e:
    print(f"Error al ejecutar: {e}")