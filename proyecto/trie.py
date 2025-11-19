# trie.py
class TrieNode:
    def __init__(self):
        self.hijos = {}      # char -> TrieNode
        self.es_fin = False  # fin de palabra

class Trie:
    def __init__(self):
        self.raiz = TrieNode()

    def insertar(self, palabra: str):
        nodo = self.raiz
        for ch in palabra:
            if ch not in nodo.hijos:
                nodo.hijos[ch] = TrieNode()
            nodo = nodo.hijos[ch]
        nodo.es_fin = True

    def existe(self, palabra: str) -> bool:
        nodo = self.raiz
        for ch in palabra:
            if ch not in nodo.hijos:
                return False
            nodo = nodo.hijos[ch]
        return nodo.es_fin

    def _dfs(self, nodo, prefijo, resultados):
        if nodo.es_fin:
            resultados.append(prefijo)
        for ch, hijo in nodo.hijos.items():
            self._dfs(hijo, prefijo + ch, resultados)

    def autocompletar(self, prefijo: str):
        nodo = self.raiz
        for ch in prefijo:
            if ch not in nodo.hijos:
                return []
            nodo = nodo.hijos[ch]
        resultados = []
        self._dfs(nodo, prefijo, resultados)
        return resultados
