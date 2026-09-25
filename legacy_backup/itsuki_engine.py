import random, json

class ItsukiCore:

    def __init__(self, idioma='es', nivel=1):
        self.idioma = idioma
        self.nivel = nivel
        self.lexico = self._cargar_lexico()
        self.gramatica = self._cargar_gramatica()
        self.semillas = {1: [201, 202, 203], 2: [204], 3: [205]}

    def _cargar_lexico(self):
        try:
            with open('lexico.json') as f:
                return {int(k): v for k, v in json.load(f).items()}
        except:
            return {}

    def _cargar_gramatica(self):
        try:
            with open('gramatica.json') as f:
                return {int(k): v['expansiones'] for k, v in json.load(f).items()}
        except:
            return {}

    def expandir(self, semilla):
        pila = list(reversed(semilla))
        salida = []
        while pila:
            sym = pila.pop()
            if sym in self.gramatica:
                exp = random.choice(self.gramatica[sym])
                for s in reversed(exp):
                    pila.append(s)
            else:
                salida.append(sym)
        return salida

    def generar_frase(self, semilla=None):
        if semilla is None:
            semilla = self.semillas.get(self.nivel, self.semillas[1])
        ids = self.expandir(semilla)
        palabras = [self.lexico.get(id_, {}).get(self.idioma, f'[{id_}]') for id_ in ids]
        frase = ' '.join(palabras).strip()
        if frase:
            frase = frase[0].upper() + frase[1:] + '.'
        return frase

    def recargar(self):
        self.lexico = self._cargar_lexico()
        self.gramatica = self._cargar_gramatica()
        return True