#--------------------------- Tabla de simbolos -------------------------------
class TablaSimbolos:
    def __init__(self):
        self.variables = {} #Almacenar las variables con el formato {nombre: tipo}
        self.funciones = {} #Almacenar las funciones con el formato {nombre: (tipo_ret, [parametros])}
        
    def  declararVariable(self, nombre, tipo):
        if nombre in self.variables: 
            raise Exception(f"Error: variable '{nombre}' ya existe dentro del codigo")
        self.variables[nombre] = tipo

    def obtenerTipoVariable(self, nombre):
        if nombre not in self.variables:
            raise Exception(f"Error: variable '{nombre}' aun no definida o delcarada proipiamente")
        else: 
            return self.variables[nombre]
        
    def declararFuncion(self, nombre, tipo, parametros):
        if nombre in self.funciones: 
            raise Exception(f"Error: funcion '{nombre}' ya delcarada anteriormente")
        self.funciones[nombre] = (tipo, parametros)

    def obtenerInfoFuncion(self, nombre):
        if nombre not in self.funciones:
            raise Exception(f"Error: funcion '{nombre}' no definda")
        else:
            return self.funciones[nombre]


#---------------------------- Analizador Semantico ------------------------------
class AnalizadorSemantico:
    def __init__(self):
        self.tablaSimbolos = TablaSimbolos()

    def analizar(self, nodo):
        if isinstance(nodo, NodoPrograma):
            for funcion in nodo.funciones:
                self.analizar(funcion)
            self.analizar(main)
        elif isinstance(nodo, NodoFuncion):
            self.tablaSimbolos.declararFuncion(nodo.nombre, nodo.tipo, nodo.parametros)
            for instruccion in nodo.cuerpo:
                self.analizar(instruccion)
        elif isinstance(nodo, NodoAsignacion):
            tipoExpresion = self.analizar(nodo.expresion)
            if tipoExpresion != nodo.tipo:
                raise Exception(f"Error: no coinciden los tipos {nodo.tipo} != {tipoExpresion}")
            else:
                self.tablaSimbolos.declararVariable(nodo.nombre, nodo.tipo)
        elif isinstance(nodo, NodoOperacion):
            tipoIzquierda = self.analizar(nodo.izquierda)
            tipoDercha = self.analizar(nodo.derecha)
            if tipoIzquierda != tipoDercha:
                raise Exception(f"Error: tipos incompatibles en la expresion {tipoIzquierda} {nodo.operador} {tipoDercha}")
        elif isinstance(nodo, NodoIdentificador):
            return self.tablaSimbolos.obtenerTipoVariable(nodo.nombre)
        elif isinstance(nodo, NodoNumero):
            return 'int' if '.' not in nodo.valor[1] else 'float'
        elif isinstance(nodo, NodoLlamadaFuncion):
            tipo, parametros = self.tablaSimbolos.obtenerInfoFuncion(nodo.nombre[1])