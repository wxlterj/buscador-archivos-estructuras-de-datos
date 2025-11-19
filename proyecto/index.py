from trie import Trie
from sparsevector import SparseVector
import os
from collections import Counter
import unicodedata
import re

# Trie que guarda las palabras
trie_titulos = Trie()
trie_contenidos = Trie()
matrizDocumentos = {}

# Quitar tildes
def normalizar(palabra):
    palabra = unicodedata.normalize("NFD", palabra)
    palabra = "".join(c for c in palabra if unicodedata.category(c) != "Mn")
    return palabra

def indexar_archivo(ruta_archivo):
  with open(ruta_archivo, "r", encoding="utf-8") as f:
    texto = f.read()

  nombre_archivo = os.path.basename(ruta_archivo).split('.')[0]
  trie_titulos.insertar(normalizar(nombre_archivo))

  # Quitar signo de puntuación y pasar a minúsculas
  palabras = re.findall(r"\w+", texto.lower(), flags=re.UNICODE)

  palabras = [normalizar(p) for p in palabras]

  for palabra in palabras:
    trie_contenidos.insertar(palabra)
  
  conteo = Counter(palabras)
  ocurrencias = SparseVector()
  for palabra, frecuencia in conteo.items():
      ocurrencias.asignar(palabra, frecuencia)

  nombre_archivo = os.path.basename(ruta_archivo)
  matrizDocumentos[nombre_archivo] = ocurrencias

def buscar_palabra(palabra):
    palabra = normalizar(palabra)
    resultados = []
    for nombre_archivo, vector in matrizDocumentos.items():
        frecuencia = vector[palabra]
        if frecuencia > 0:
            resultados.append((nombre_archivo, frecuencia))

    # Ordenar por frecuencia de mayor a menor
    resultados.sort(key=lambda x: x[1], reverse=True)
    return resultados