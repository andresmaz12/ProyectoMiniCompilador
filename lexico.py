#-------------------------- Lexico Pseudo-Código -----------------------------------------------
import re

tokenPatron = {
    "CADENA": r'"[^"]*"',
    "NUMERO": r'\b\d+(?:\.\d+)?\b',
    "PALABRA_CLAVE": r'\b(inicio|fin|finsi|si|sino|entonces|mientras|finmientras|escribir|leer|entero|flotante|cadena|retorna|metodo)\b',
    "IDENTIFICADOR": r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    "OPERADOR": r'>=|<=|==|!=|[+\-*/=<>]',
    "DELIMITADOR": r'[(),]',
    "ESPACIO_BLANCO": r'\s+',
}

def identificarTokens(texto):
    patronGeneral = '|'.join(
        f'(?P<{token}>{patron})'
        for token, patron in tokenPatron.items()
    )
    patronRegex = re.compile(patronGeneral)

    tokensEncontrados = []
    for match in patronRegex.finditer(texto):
        for token, valor in match.groupdict().items():
            if valor is not None and token != "ESPACIO_BLANCO":
                tokensEncontrados.append((token, valor))

    return tokensEncontrados
