#------------------------ ARBOL de SINTAXIS ABSTRACTA ------------------

class NodoAST:
    def generarCodigo(self):
        raise NotImplementedError("Método generarCodigo() no implementado en este Nodo")

class NodoPrograma(NodoAST):
    def __init__(self, instrucciones):
       self.instrucciones = instrucciones

    def generarCodigo(self):
       codigo = ["section .text", "global _start", "_start:"]
       data = ["section .bss"]
       for inst in self.instrucciones:
           codigo.append(inst.generarCodigo())
       codigo.append("    mov eax, 1")
       codigo.append("    xor ebx, ebx")
       codigo.append("    int 0x80")
       return "\n".join(data) + "\n" + "\n".join(codigo)

class NodoDeclaracion(NodoAST):
    def __init__(self, tipo, nombre, expresion=None):
        self.tipo = tipo
        self.nombre = nombre
        self.expresion = expresion

class NodoBloque(NodoAST):
    def __init__(self, instrucciones):
        self.instrucciones = instrucciones

class NodoAsignacion(NodoAST):
    def __init__(self, nombre, expresion):
        self.nombre = nombre
        self.expresion = expresion

    def generarCodigo(self):
        codigo = self.expresion.generarCodigo()
        codigo += f"\n    mov [{self.nombre[1]}], eax"
        return codigo

class NodoOperacion(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.derecha = derecha
        self.operador = operador

    def generarCodigo(self):
        lineas = []
        lineas.append(self.izquierda.generarCodigo())
        lineas.append("    push eax")
        lineas.append(self.derecha.generarCodigo())
        lineas.append("    mov ebx, eax")
        lineas.append("    pop eax")
        op = self.operador[1]
        if op == "+":
            lineas.append("    add eax, ebx")
        elif op == "-":
            lineas.append("    sub eax, ebx")
        elif op == "*":
            lineas.append("    imul eax, ebx")
        elif op == "/":
            lineas.append("    cdq")
            lineas.append("    idiv ebx")
        elif op in (">", "<", ">=", "<=", "==", "!="):
            lineas.append("    cmp eax, ebx")
        return "\n".join(lineas)

class NodoNumero(NodoAST):
    def __init__(self, valor):
        self.valor = valor

    def generarCodigo(self):
       return f"    mov eax, {self.valor[1]}"

class NodoIdent(NodoAST):
    def __init__(self, nombre):
        self.nombre = nombre

    def generarCodigo(self):
       return f"    mov eax, [{self.nombre[1]}]"

class NodoString(NodoAST):
    def __init__(self, valor):
        self.valor = valor

    def generarCodigo(self):
       raise NotImplementedError("Strings en ensamblador aún no implementado")

class NodoCondicional(NodoAST):
    def __init__(self, condicion, cuerpo_si, cuerpo_sino):
        self.condicion = condicion
        self.cuerpo_si = cuerpo_si
        self.cuerpo_sino = cuerpo_sino

class NodoImprimir(NodoAST):
    def __init__(self, argumentos):
        self.argumentos = argumentos

class NodoWhile(NodoAST):
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo

class NodoRetorno(NodoAST):
    def __init__(self, expresion):
        self.expresion = expresion

    def generarCodigo(self):
        return self.expresion.generarCodigo()

class NodoFuncion(NodoAST):
    def __init__(self, tipo_retorno, nombre, parametros, cuerpo):
      self.tipo_retorno = tipo_retorno
      self.nombre = nombre
      self.parametros = parametros
      self.cuerpo = cuerpo

    def generarCodigo(self):
        codigo = f"{self.nombre}:\n"
        # cuerpo es NodoBloque ahora
        codigo += self.cuerpo.generarCodigo()
        codigo += "\n    ret\n"
        return codigo

class NodoParametro(NodoAST):
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre

class NodoLlamadaFuncion(NodoAST):
    def __init__(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos

    def generarCodigo(self):
        codigo = []
        for arg in reversed(self.argumentos):
            codigo.append(arg.generarCodigo())
            codigo.append("    push eax")
        codigo.append(f"    call {self.nombre}")
        codigo.append(f"    add esp, {len(self.argumentos) * 4}")
        return "\n".join(codigo)

class NodoEntrada(NodoAST):
    def __init__(self, variable):
        self.variable = variable

class NodoIncremento(NodoAST):
    def __init__(self, nombre, operador):
        self.nombre = nombre
        self.operador = operador


#---------------------------- PARSER ---------------------------------
class Parse:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def obtener_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def coincidir(self, tipo_esperado):
        token_actual = self.obtener_token()
        if token_actual and token_actual[0] == tipo_esperado:
            self.pos += 1
            return token_actual
        raise SyntaxError(
            f"Se esperaba {tipo_esperado} pero se encontró: {token_actual}"
        )

    def coincidir_valor(self, valor_esperado):
        token_actual = self.obtener_token()
        if token_actual and token_actual[1] == valor_esperado:
            self.pos += 1
            return token_actual
        raise SyntaxError(
            f"Se esperaba '{valor_esperado}' pero se encontró: {token_actual}"
        )

    # ── Punto de entrada ──────────────────────────────────────────────

    def parsear(self):
        instrucciones = []
        while self.obtener_token() is not None:
            instrucciones.append(self.declaracion_global_o_funcion())
        return NodoPrograma(instrucciones)

    def declaracion_global_o_funcion(self):
        tipo = self.coincidir('PALABRA_CLAVE')
        nombre = self.coincidir('IDENTIFICADOR')
        
        if self.obtener_token() and self.obtener_token()[1] == '(':
            self.coincidir_valor('(')
            parametros = []
            if self.obtener_token() and self.obtener_token()[1] != ')':
                p_tipo = self.coincidir('PALABRA_CLAVE')
                p_nombre = self.coincidir('IDENTIFICADOR')
                parametros.append(NodoParametro(p_tipo, p_nombre))
                while self.obtener_token() and self.obtener_token()[1] == ',':
                    self.coincidir_valor(',')
                    p_tipo = self.coincidir('PALABRA_CLAVE')
                    p_nombre = self.coincidir('IDENTIFICADOR')
                    parametros.append(NodoParametro(p_tipo, p_nombre))
            self.coincidir_valor(')')
            cuerpo = self.bloque()
            return NodoFuncion(tipo, nombre, parametros, cuerpo)
        else:
            expr = None
            if self.obtener_token() and self.obtener_token()[1] == '=':
                self.coincidir_valor('=')
                expr = self.expresion()
            self.coincidir_valor(';')
            return NodoDeclaracion(tipo, nombre, expr)

    def bloque(self):
        self.coincidir_valor('{')
        instrucciones = []
        while self.obtener_token() and self.obtener_token()[1] != '}':
            instrucciones.append(self.instruccion())
        self.coincidir_valor('}')
        return NodoBloque(instrucciones)

    def instruccion(self):
        tok = self.obtener_token()
        if tok is None:
            raise SyntaxError("Se esperaba una instrucción pero se llegó al final del archivo")

        if tok[1] == '{':
            return self.bloque()

        if tok[1] in ('int', 'float', 'void', 'entero', 'flotante', 'cadena'):
            tipo = self.coincidir('PALABRA_CLAVE')
            nombre = self.coincidir('IDENTIFICADOR')
            expr = None
            if self.obtener_token() and self.obtener_token()[1] == '=':
                self.coincidir_valor('=')
                expr = self.expresion()
            self.coincidir_valor(';')
            return NodoDeclaracion(tipo, nombre, expr)

        if tok[1] == 'si':
            return self.condicional()
        if tok[1] == 'mientras':
            return self.cicloMientras()
        if tok[1] == 'escribir':
            return self.llamadaEscribir()
        if tok[1] == 'leer':
            return self.llamadaLeer()
        
        if tok[0] == 'IDENTIFICADOR':
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1][1] == '(':
                nombre = self.coincidir('IDENTIFICADOR')
                self.coincidir_valor('(')
                args = []
                if self.obtener_token() and self.obtener_token()[1] != ')':
                    args.append(self.expresion())
                    while self.obtener_token() and self.obtener_token()[1] == ',':
                        self.coincidir_valor(',')
                        args.append(self.expresion())
                self.coincidir_valor(')')
                self.coincidir_valor(';')
                return NodoLlamadaFuncion(nombre, args)
            else:
                nombre = self.coincidir('IDENTIFICADOR')
                self.coincidir_valor('=')
                expr = self.expresion()
                self.coincidir_valor(';')
                return NodoAsignacion(nombre, expr)

        raise SyntaxError(f"Instrucción no reconocida: {tok}")

    def condicional(self):
        self.coincidir_valor('si')
        self.coincidir_valor('(')
        condicion = self.expresion()
        self.coincidir_valor(')')
        cuerpo_si = self.bloque()

        cuerpo_sino = None
        if self.obtener_token() and self.obtener_token()[1] == 'sino':
            self.coincidir_valor('sino')
            cuerpo_sino = self.bloque()

        return NodoCondicional(condicion, cuerpo_si, cuerpo_sino)

    def cicloMientras(self):
        self.coincidir_valor('mientras')
        self.coincidir_valor('(')
        condicion = self.expresion()
        self.coincidir_valor(')')
        cuerpo = self.bloque()
        return NodoWhile(condicion, cuerpo)

    def llamadaEscribir(self):
        self.coincidir_valor('escribir')
        self.coincidir_valor('(')
        argumentos = [self.expresion()]
        while self.obtener_token() and self.obtener_token()[1] == ',':
            self.coincidir_valor(',')
            argumentos.append(self.expresion())
        self.coincidir_valor(')')
        self.coincidir_valor(';')
        return NodoImprimir(argumentos)

    def llamadaLeer(self):
        self.coincidir_valor('leer')
        self.coincidir_valor('(')
        variable = self.coincidir('IDENTIFICADOR')
        self.coincidir_valor(')')
        self.coincidir_valor(';')
        return NodoEntrada(variable)

    def expresion(self):
        return self.comparacion()

    def comparacion(self):
        izquierda = self.aritmetica()
        if self.obtener_token() and self.obtener_token()[1] in ('>', '<', '>=', '<=', '==', '!='):
            operador = self.coincidir('OPERADOR')
            derecha = self.aritmetica()
            return NodoOperacion(izquierda, operador, derecha)
        return izquierda

    def aritmetica(self):
        izquierda = self.termino()
        while self.obtener_token() and self.obtener_token()[1] in ('+', '-'):
            operador = self.coincidir('OPERADOR')
            derecha = self.termino()
            izquierda = NodoOperacion(izquierda, operador, derecha)
        return izquierda

    def termino(self):
        izquierda = self.factor()
        while self.obtener_token() and self.obtener_token()[1] in ('*', '/'):
            operador = self.coincidir('OPERADOR')
            derecha = self.factor()
            izquierda = NodoOperacion(izquierda, operador, derecha)
        return izquierda

    def factor(self):
        token = self.obtener_token()
        if token is None:
            raise SyntaxError("Se esperaba un valor pero se llegó al final del archivo")

        if token[0] == 'NUMERO':
            return NodoNumero(self.coincidir('NUMERO'))

        if token[0] == 'IDENTIFICADOR':
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1][1] == '(':
                nombre = self.coincidir('IDENTIFICADOR')
                self.coincidir_valor('(')
                args = []
                if self.obtener_token() and self.obtener_token()[1] != ')':
                    args.append(self.expresion())
                    while self.obtener_token() and self.obtener_token()[1] == ',':
                        self.coincidir_valor(',')
                        args.append(self.expresion())
                self.coincidir_valor(')')
                return NodoLlamadaFuncion(nombre, args)
            else:
                return NodoIdent(self.coincidir('IDENTIFICADOR'))

        if token[0] == 'CADENA':
            return NodoString(self.coincidir('CADENA'))

        if token[1] == '(':
            self.coincidir_valor('(')
            expr = self.expresion()
            self.coincidir_valor(')')
            return expr

        raise SyntaxError(f"Factor no válido: {token}")
