from sintactico import *
import json

def imprimir_pila_ambitos(ambitos):
    print("\n=== Pila de Ámbitos ===")
    for i, ambito in enumerate(reversed(ambitos)):
        nivel = len(ambitos) - 1 - i
        print(f"Nivel [{nivel}] -> {ambito}")
    print("=======================\n")

#--------------------------- Tabla de simbolos -------------------------------
class TablaSimbolos:
    def __init__(self):
        # LIsdta de diccionarios: 
        self.ambitos = [{}] #Almacenar las variables con el formato {nombre: tipo}
        self.funciones = {} #Almacenar las funciones con el formato {nombre: (tipo_ret, [parametros])}
        self.historial_ambitos = {}

    def entrar_ambito(self):
        self.ambitos.append({})
        print("-> Entrando a un nuevo ámbito")
        imprimir_pila_ambitos(self.ambitos)

    def salir_ambito(self):
        if len(self.ambitos) > 1:
            self.ambitos.pop()
            print("<- Saliendo de ámbito")
            imprimir_pila_ambitos(self.ambitos)
        else:
            raise Exception("No se puede salir del ambito global")
        
    def declararVariable(self, nombre, tipo):
        #Verificar que existe el ambito actual 
        ambito_actual = self.ambitos[-1]
        if nombre in ambito_actual: 
            raise Exception(f"Error: variable '{nombre}' ya existe dentro del ambito actual")
        ambito_actual[nombre] = tipo
        print(f"   (Se declaró la variable '{nombre}' de tipo '{tipo}')")
        imprimir_pila_ambitos(self.ambitos)

    def obtenerTipoVariable(self, nombre):
        # Buscar la variable desde el ambito mas interno hacia el golbal (shadowing)
        for ambito in reversed(self.ambitos):
            if nombre in ambito:
                return ambito[nombre]
        raise Exception(f"Error: variable '{nombre}' aun no definida o declarada propiamente dentro del ambito")
            
    def declararFuncion(self, nombre, tipo, parametros):
        if nombre in self.funciones: 
            raise Exception(f"Error: funcion '{nombre}' ya declarada anteriormente")
        self.funciones[nombre] = (tipo, parametros)

    def obtenerInfoFuncion(self, nombre):
        if nombre not in self.funciones:
            raise Exception(f"Error: funcion '{nombre}' no definida")
        return self.funciones[nombre]
        
#--------------------------- Sistema de Tipos ----------------------------------
class SistemaTipo:
    
    @staticmethod
    def es_compatible(t1, t2):
        return t1==t2 or (t1 == 'int' and t2 == 'int') or (t1 == 'int' and t2 == 'float') or (t1 == 'float' and t2 == 'int')
    
    @staticmethod
    def tipo_resultante(t1, t2, operador):
        #Promocion de tipos
        if t1 == 'float' or t2 == 'float':
            return 'float'
        return 'int'
    
    @staticmethod
    def jerarquia_tipos(t1, t2):
        if t1 == 'float' and t2 == 'float':
            return 'float'
        elif t1 == 'float' and t2 == 'int':
            return 'float'
        elif t1 == 'int' and t2 == 'int': 
            return 'int'

#---------------------------- Analizador Semantico ------------------------------
class AnalizadorSemantico:
    def __init__(self):
        self.tablaSimbolos = TablaSimbolos()

    def analizar(self, nodo):
        if isinstance(nodo, NodoPrograma):
            for instruccion in nodo.instrucciones:
                self.analizar(instruccion)
       
        elif isinstance(nodo, NodoBloque):
            self.tablaSimbolos.entrar_ambito()
            for instruccion in nodo.instrucciones:
                self.analizar(instruccion)
            self.tablaSimbolos.salir_ambito()

        elif isinstance(nodo, NodoDeclaracion):
            if nodo.expresion:
                tipoExpresion = self.analizar(nodo.expresion)
                if not SistemaTipo.es_compatible(nodo.tipo[1], tipoExpresion):
                    raise Exception(f"Error: no coinciden los tipos en la declaración {nodo.tipo[1]} != {tipoExpresion}")
            self.tablaSimbolos.declararVariable(nodo.nombre[1], nodo.tipo[1])

        elif isinstance(nodo, NodoAsignacion):
            tipoVariable = self.tablaSimbolos.obtenerTipoVariable(nodo.nombre[1])
            tipoExpresion = self.analizar(nodo.expresion)
            if not SistemaTipo.es_compatible(tipoVariable, tipoExpresion):
                raise Exception(f"Error: tipos incompatibles al asignar {tipoVariable} = {tipoExpresion}")

        elif isinstance(nodo, NodoFuncion):
            # 1 Declarar la función en el ambito global 
            parametros_info = [(p.nombre[1], p.tipo[1]) for p in nodo.parametros]
            self.tablaSimbolos.declararFuncion(nodo.nombre[1], nodo.tipo_retorno[1], parametros_info)
            
            # 2 Crear un nuevo ambito para los parámetros de la funcion 
            self.tablaSimbolos.entrar_ambito()

            # 3 Declarar parámetros dentro del nuevo ambito
            for p_nombre, p_tipo in parametros_info:
                self.tablaSimbolos.declararVariable(p_nombre, p_tipo)
            
            # 4 Analizar el cuerpo de la función
            # En nuestro parser, el cuerpo de una función es un NodoBloque que abrirá y cerrará su propio sub-ámbito.
            # Alternativamente, podríamos no dejar que NodoBloque abra un ámbito si ya estamos en uno,
            # pero en C-like es correcto que el bloque raíz tenga su propio ámbito debajo del ámbito de parámetros.
            self.analizar(nodo.cuerpo)
            
            # 5 Salir del ámbito de la firma de la función
            self.tablaSimbolos.salir_ambito()

        elif isinstance(nodo, NodoOperacion):
            tipoIzquierda = self.analizar(nodo.izquierda)
            tipoDercha = self.analizar(nodo.derecha)

            if not SistemaTipo.es_compatible(tipoIzquierda, tipoDercha):
                raise Exception(f"Error: tipos incompatibles {tipoIzquierda} {nodo.operador[1]} {tipoDercha}")

            return SistemaTipo.tipo_resultante(tipoIzquierda, tipoDercha, nodo.operador[1])

        elif isinstance(nodo, NodoIdent):
            return self.tablaSimbolos.obtenerTipoVariable(nodo.nombre[1])

        elif isinstance(nodo, NodoNumero):
            return 'int' if '.' not in nodo.valor[1] else 'float'

        elif isinstance(nodo, NodoLlamadaFuncion):
            tipo_retorno, parametros_esperados = self.tablaSimbolos.obtenerInfoFuncion(nodo.nombre[1])

            # 1. Verificar cantidad de argumentos
            if len(nodo.argumentos) != len(parametros_esperados):
                raise Exception(f"Número incorrecto de argumentos en la llamada a '{nodo.nombre[1]}'")

            # 2. Verificar tipos de los argumentos
            for arg_pasado, param_esperado in zip(nodo.argumentos, parametros_esperados):
                tipo_arg = self.analizar(arg_pasado)
                if not SistemaTipo.es_compatible(tipo_arg, param_esperado[1]):
                    raise Exception(f"Tipo de argumento incompatible en '{nodo.nombre[1]}'. Esperaba {param_esperado[1]}, recibió {tipo_arg}")

            # 3. Retornar el tipo que devuelve la función
            return tipo_retorno
            
        elif isinstance(nodo, NodoImprimir):
            for arg in nodo.argumentos:
                self.analizar(arg)
                
    def imprimir_ambitos(self):
        imprimir_pila_ambitos(self.tablaSimbolos.ambitos)
        return "Pila de ámbitos impresa correctamente."
