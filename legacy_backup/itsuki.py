import random, json, sys
from utils.decorators import FRASES_ESTATICAS, TABLA_GRAMATICA

def cargar_lexico():
    try:
        with open('lexico.json', 'r') as f:
            return {int(k): v for k, v in json.load(f).items()}
    except:
        return {100: {'es': 'el', 'en': 'the', 'pt': 'o'}}

def cargar_gramatica():
    try:
        with open('gramatica.json', 'r') as f:
            return {int(k): v['expansiones'] for k, v in json.load(f).items()}
    except:
        return {}

def expandir(seed, gramatica):
    pila = list(reversed(seed))
    salida = []
    while pila:
        sym = pila.pop()
        if sym in gramatica:
            expansion = random.choice(gramatica[sym])
            for s in reversed(expansion):
                pila.append(s)
        else:
            salida.append(sym)
    return salida

class Itsuki:
    def __init__(self, idioma='es', nivel=1):
        self.idioma = idioma
        self.nivel = nivel
        self.historial = []
        self.lexico = cargar_lexico()
        self.gramatica = cargar_gramatica()
        self.semillas = {1: [201, 202, 203], 2: [204], 3: [205]}

    def recargar(self):
        self.lexico = cargar_lexico()
        self.gramatica = cargar_gramatica()
        return 'Léxico y gramática recargados. Nuevas palabras y reglas activas.'

    def generar_frase(self, semilla=None):
        if semilla is None:
            semilla = self.semillas.get(self.nivel, self.semillas[1])
        ids = expandir(semilla, self.gramatica)
        palabras = [self.lexico.get(id_, {}).get(self.idioma, f'[ID{id_}]') for id_ in ids]
        frase = ' '.join(palabras).strip()
        if frase:
            frase = frase[0].upper() + frase[1:] + '.'
        frase = frase.replace(' ,', ',').replace(' .', '.')
        self.historial.append(frase)
        return frase

    def responder(self, entrada):
        entrada_lower = entrada.strip().lower()
        if entrada_lower == '.exit':
            return None
        elif entrada_lower.startswith('/idioma '):
            nuevo = entrada_lower.split()[1]
            if nuevo in ('es', 'en', 'pt'):
                self.idioma = nuevo
                return f'Idioma cambiado a {nuevo}.'
            else:
                return 'Uso: /idioma es|en|pt'
        elif entrada_lower == '/estado':
            return f'Itsuki activa. Modo: {self.idioma}. Nivel: {self.nivel}. Frases generadas: {len(self.historial)}'
        elif entrada_lower.startswith('/nivel '):
            try:
                niv = int(entrada_lower.split()[1])
                if niv in (1,2,3):
                    self.nivel = niv
                    return f'Nivel de sofisticación cambiado a {niv}. (1=básico, 2=intermedio, 3=avanzado)'
                else:
                    return 'Nivel debe ser 1, 2 o 3.'
            except:
                return 'Uso: /nivel <1-3>'
        elif entrada_lower.startswith('/semilla '):
            try:
                seed_val = int(entrada_lower.split()[1])
                random.seed(seed_val)
                return f'Semilla aleatoria fijada a {seed_val}.'
            except:
                return 'Semilla inválida.'
        elif entrada_lower == '/recargar':
            return self.recargar()
        elif entrada_lower == '/dictamen':
            return random.choice(FRASES_ESTATICAS['dictamen'])
        elif entrada_lower == '/auditoria':
            return random.choice(FRASES_ESTATICAS['auditoria'])
        elif entrada_lower == '/gramatica':
            return TABLA_GRAMATICA
        # Si el usuario escribió una palabra conocida, generar frase
        for palabra in entrada_lower.split():
            for id_, trad in self.lexico.items():
                if trad.get(self.idioma, '').lower() == palabra:
                    return self.generar_frase()
        # Respuesta neutra aleatoria
        return random.choice([
            'Eso es ruido sintáctico. Repite con mejor estructura.',
            'Tu oración no supera mi auditoría semántica.',
            'El usuario comete un error de tipo. Depurando...',
            'Input inválido. Tu capacidad cognitiva parece estar en pausa.'
        ])

def main():
    print('=== Itsuki Mainframe – Optimización Pareto+Feynman ===')
    print('Comandos: .exit | /idioma es|en|pt | /nivel 1-3 | /estado | /semilla <n> | /recargar')
    print('         /dictamen | /auditoria | /gramatica')
    print('Cualquier palabra conocida activa una frase.\n')
    itsuki = Itsuki(idioma='es', nivel=1)
    while True:
        try:
            inp = input('>>> ')
            respuesta = itsuki.responder(inp)
            if respuesta is None:
                print('Itsuki: Cerrando sesión. Que tu código compile sin errores.')
                break
            print('Itsuki:', respuesta)
        except (KeyboardInterrupt, EOFError):
            print('\nItsuki: Sesión terminada.')
            break

if __name__ == '__main__':
    main()
