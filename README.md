# Buscador de archivos

**Introducción**  
   El programa es un sistema de búsqueda y gestión de documentos, donde el usuario puede cargar archivos de texto y buscarlos por nombre o por contenido. Internamente, el sistema organiza la información mediante estructuras como tries y vectores dispersos, permitiendo búsquedas rápidas, autocompletado y filtrado preciso de resultados.  
     
**Objetivo del uso de estructuras de datos**  
    El programa utiliza estructuras de datos para almacenar, indexar y buscar el contenido de múltiples documentos de texto. El uso combinado de tries, vectores dispersos y diccionarios permite organizar las palabras, contabilizar sus apariciones y relacionarlas rápidamente con los archivos donde se encuentran. Gracias a estas estructuras, el sistema puede ofrecer funciones como autocompletado, búsquedas rápidas, filtrado por archivo y reporte de coincidencias, manteniendo un rendimiento óptimo incluso con grandes cantidades de texto.  
     
**Uso de herramientas de inteligencia artificial**  
    Aproximadamente entre el 45% y el 55% del código fue desarrollado con apoyo de herramientas de inteligencia artificial, principalmente para generación de fragmentos de código, asesoría técnica y organización de módulos.  
     
   **Estructuras de datos utilizadas**  
   **Trie (árbol prefijo)**  
   **Por qué se usó**  
    El trie permite almacenar palabras de manera jerárquica, donde cada nodo representa un carácter. Esto hace posible autocompletar palabras con rapidez, verificar si una palabra existe sin recorrer listas y evitar duplicados. Es ideal para motores de búsqueda con sugerencias instantáneas.  
   **Cómo se usó**

   Se implementaron dos tries: uno para los nombres de los archivos (trie\_titulos) y otro para las palabras dentro del contenido de cada documento (trie\_contenidos). Cada palabra se inserta carácter por carácter y se marca el nodo final como palabra completa.

   **Vector disperso (SparseVector)**

   **Por qué se usó**  
   Un vector disperso permite almacenar pares palabra → cantidad de apariciones sin desperdiciar memoria. En un documento normal solo aparece una pequeña fracción de todas las palabras posibles, por lo que usar un vector disperso evita listas enormes llenas de ceros. Ofrece eficiencia en memoria y acceso rápido a la frecuencia de cada palabra.  
   **Cómo se usó**  
   Cada archivo se convierte en un SparseVector donde la clave es la palabra normalizada y el valor es la cantidad de veces que aparece. Ese vector se guarda luego en la matriz de documentos.

   **Diccionario (matriz dispersa de documentos)**

   **Por qué se usó**  
   En Python, un diccionario permite representar de forma eficiente una matriz dispersa donde las claves no son numéricas. En este caso, representa la relación documento → vector de palabras. Permite acceso directo al vector de cada archivo, evita almacenar grandes cantidades de valores nulos y facilita saber rápidamente en qué archivos aparece una palabra.  
   **Cómo se usó**  
   Se implementó como un diccionario donde cada clave es el nombre del archivo y cada valor es un SparseVector. Al buscar una palabra, se consulta su frecuencia en cada vector.

**Interacciones entre las estructuras**  
Las estructuras trabajan juntas para permitir las funciones del sistema:

* Cada vez que se indexa un archivo, su nombre se guarda en el trie de títulos.  
* Cada palabra del contenido se inserta en el trie de contenidos.  
* El conteo de palabras del archivo se almacena en un vector disperso.  
* Ese vector se guarda en el diccionario matrizDocumentos.  
* Cuando el usuario busca una palabra, se normaliza, se valida con el trie y se revisa en qué archivos aparece según los vectores dispersos.

  