# vector_disperso.py
class SparseVector:
    def __init__(self):
        self.valores = {}

    def asignar(self, indice, valor):
        if valor != 0:
            self.valores[indice] = valor
        elif indice in self.valores:
            del self.valores[indice]

    def __getitem__(self, indice):
        return self.valores.get(indice, 0)

    def __repr__(self):
        return f"{self.valores}"