import os
import tkinter as tk
from tkinter import ttk, filedialog
from index import indexar_archivo, trie_titulos,  trie_contenidos, normalizar, matrizDocumentos, buscar_palabra
from model import UIFile

class UI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Buscador de archivos")
        self.root.geometry("1050x700")
        self.root.configure(bg="#F5F5F5")
        self.files = []
        self.results = []

        # ---- ESTILOS ----
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#F5F5F5")
        self.style.configure("TLabel", background="#F5F5F5")
        self.style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), background="#F5F5F5")
        self.style.configure("Sub.TLabel", font=("Segoe UI", 11), foreground="#555", background="#F5F5F5")
        self.style.configure("Search.TButton", font=("Segoe UI", 11, "bold"))
        self.style.configure("Card.TFrame", relief="raised", borderwidth=1)
        self.style.configure("Category.TLabel", foreground="#0A84FF", font=("Segoe UI", 10, "bold"))

        # header
        self.header = ttk.Frame(self.root, padding=20)
        self.header.pack(fill="x")
        ttk.Label(self.header, text="Buscar documentos", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.header, text="Buscar documentos por título o contenido", style="Sub.TLabel").pack(anchor="w")
        self.upload_button = tk.Button(self.header, text="⬆️Subir archivo", bg="#0A84FF", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=5)
        self.upload_button.bind("<Button-1>", self.on_upload_click)
        self.upload_button.pack(anchor="e")

        # barra de busqueda
        search_row = ttk.Frame(self.root, padding=(20, 10))
        search_row.pack(fill="x")

        # caja de búsqueda
        self.search_entry = ttk.Entry(search_row, width=70, font=("Segoe UI", 12))
        self.search_entry.pack(side="left", padx=(0, 10))

        # botón search
        self.search_button = ttk.Button(search_row, text="Buscar", style="Search.TButton", command=self.perform_search)
        self.search_button.pack(side="left", padx=(0, 10))

        # botón para mostrar todos y limpiar filtro
        self.reset_button = ttk.Button(search_row, text="Mostrar todos", command=self.reset_view)
        self.reset_button.pack(side="left", padx=(6, 10))

        # radio buttons
        self.filter_var = tk.StringVar(value="all")

        ttk.Radiobutton(search_row, text="Todo", variable=self.filter_var, value="all").pack(side="left")
        ttk.Radiobutton(search_row, text="Título", variable=self.filter_var, value="title").pack(side="left", padx=15)
        ttk.Radiobutton(search_row, text="Contenido", variable=self.filter_var, value="content").pack(side="left")

        # bind Enter para buscar (ejecuta búsqueda final)
        self.search_entry.bind('<Return>', lambda e: self.perform_search())

        
        self.suggestions_window = tk.Toplevel(self.root)
        self.suggestions_window.wm_overrideredirect(True)
        self.suggestions_window.attributes("-topmost", True)
        self.suggestions_window.withdraw()

        self.suggestions_listbox = tk.Listbox(self.suggestions_window, height=6, font=("Segoe UI", 10))
        self.suggestions_listbox.pack(side="left", fill="both", expand=True)

        suggestions_scroll = ttk.Scrollbar(self.suggestions_window, orient="vertical", command=self.suggestions_listbox.yview)
        suggestions_scroll.pack(side="right", fill="y")
        self.suggestions_listbox.config(yscrollcommand=suggestions_scroll.set)

        # eventos
        self.search_entry.bind('<KeyRelease>', self.on_type)
        self.search_entry.bind('<FocusIn>', lambda e: self.show_suggestions())
        self.search_entry.bind('<Button-1>', lambda e: self.show_suggestions())
        self.suggestions_listbox.bind('<Double-Button-1>', self.on_suggestion_select)
        self.suggestions_listbox.bind('<ButtonRelease-1>', self.on_suggestion_click)

        # almacenamiento de items: lista de tuplas (kind, value)
        self.suggestions_items = []

        # cerrar si se hace click fuera (global)
        self.root.bind_all('<Button-1>', self.on_global_click, add='+')

        # ocultar si el foco se pierde fuera del entry/listbox
        self.search_entry.bind('<FocusOut>', lambda e: self.root.after(100, self.hide_suggestions_if_needed))
        self.suggestions_listbox.bind('<FocusOut>', lambda e: self.root.after(100, self.hide_suggestions_if_needed))

        

        # ---- SCROLL AREA ----
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=20, pady=10)

        canvas = tk.Canvas(container, bg="#F5F5F5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.cards_frame = ttk.Frame(canvas)

        self.cards_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---- TARJETAS  ----
        

        row = 0
        col = 0

        for name, file_path, size, date_modified in self.files:
            card = ttk.Frame(self.cards_frame, padding=15, style="Card.TFrame")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="n")

            # Ícono + título
            header = ttk.Frame(card)
            header.pack(anchor="w")

            ttk.Label(header, text="📄", font=("Segoe UI", 20)).pack(side="left", padx=(0, 8))
            ttk.Label(header, text=name, style="Title.TLabel").pack(side="left", anchor="center")

            # Ruta del archivo
            ttk.Label(
                card,
                text=file_path,
                font=("Segoe UI", 9),
                foreground="#555",
                wraplength=250
            ).pack(anchor="w", pady=(5, 5))

            # Línea divisoria
            ttk.Separator(card).pack(fill="x", pady=5)

            # Descripción simulada o tamaño
            ttk.Label(
                card,
                text=f"Size: {size} KB",
                foreground="#333",
                font=("Segoe UI", 10)
            ).pack(anchor="w")

            # Pie de card
            bottom = ttk.Frame(card)
            bottom.pack(anchor="w", pady=(10, 0))

            ttk.Label(bottom, text=f"📅 {date_modified}").pack(side="left")

            # GRID
            col += 1
            if col == 3:
                col = 0
                row += 1

    def on_search(self, event=None):
        # Reutilizamos on_search para poblar el desplegable (suggestions_listbox)
        query = self.search_entry.get().strip()
        filter_option = self.filter_var.get()

        # limpiar listbox y items
        if hasattr(self, 'suggestions_listbox'):
            self.suggestions_listbox.delete(0, tk.END)
        self.suggestions_items = []

        if not query:
            self.hide_suggestions()
            return

        q = normalizar(query)

        # según filtro: title -> sugerencias de títulos (nombres de archivos)
        # content -> sugerencias de palabras
        # all -> combinar ambos
        to_display = []

        if filter_option in ("all", "title"):
            titulos = trie_titulos.autocompletar(q)
            for t in titulos:
                for fname in matrizDocumentos.keys():
                    if os.path.splitext(fname)[0].lower() == t.lower():
                        # mostrar el nombre de archivo (con extensión)
                        to_display.append(("title", fname))

        if filter_option in ("all", "content"):
            palabras = trie_contenidos.autocompletar(q)
            for palabra in palabras:
                to_display.append(("word", palabra))

        if not to_display:
            self.suggestions_listbox.insert(tk.END, "No se encontraron resultados")
            self.suggestions_items = []
            self.show_suggestions()
            return

        # poblar listbox y registro de items
        for kind, val in to_display:
            if kind == "title":
                label = f"📄 {val}"
            else:
                label = f"🔎 {val}"
            self.suggestions_listbox.insert(tk.END, label)
            self.suggestions_items.append((kind, val))

        self.show_suggestions()

    def perform_search(self, event=None):
        """Ejecuta la búsqueda final y actualiza las tarjetas según el filtro seleccionado.
        Usa `buscar_palabra` para búsquedas por contenido."""
        query = self.search_entry.get().strip()
        if not query:
            self.reset_view()
            return

        mode = self.filter_var.get()
        filenames = []

        if mode in ("all", "content"):
            # buscar por contenido usando buscar_palabra (normaliza internamente)
            resultados = buscar_palabra(query)
            filenames.extend([r[0] for r in resultados])

        if mode in ("all", "title"):
            pref = normalizar(query)
            titulos = trie_titulos.autocompletar(pref)
            for fname in matrizDocumentos.keys():
                if os.path.splitext(fname)[0].lower() in (t.lower() for t in titulos):
                    filenames.append(fname)

        # eliminar duplicados manteniendo orden
        seen = set()
        unique_filenames = []
        for f in filenames:
            if f not in seen:
                seen.add(f)
                unique_filenames.append(f)

        # mapear a objetos UIFile en self.files
        filtered_ui_files = [ui_file for ui_file in self.files if ui_file.name in unique_filenames]
        self.update_cards(filtered_ui_files)


    def on_upload_click(self, event=None):
        file_path = filedialog.askopenfilename(title="Seleccionar archivo", filetypes=[("Text files", "*.txt")])
        if file_path:
            self.files.insert(0, self.create_ui_file(file_path))
            indexar_archivo(file_path)
            self.update_cards()

    # autocompletar
    def position_suggestions(self):
        try:
            x = self.search_entry.winfo_rootx()
            y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height()
            width = self.search_entry.winfo_width()
            height = 150
            self.suggestions_window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass

    def show_suggestions(self):
        # posicionar y mostrar
        self.position_suggestions()
        try:
            self.suggestions_window.deiconify()
        except Exception:
            pass

    def hide_suggestions(self):
        try:
            self.suggestions_window.withdraw()
        except Exception:
            pass

    def hide_suggestions_if_needed(self):
        focused = self.root.focus_get()
        if focused not in (self.search_entry, self.suggestions_listbox):
            self.hide_suggestions()

    def on_global_click(self, event):
        # cierra el desplegable si el click fue fuera del entry o del suggestions_window
        try:
            if not self.suggestions_window.winfo_ismapped():
                return
        except Exception:
            return

        # widget bajo el puntero
        w = self.root.winfo_containing(event.x_root, event.y_root)
        # si el widget es None o no está dentro del entry ni dentro de la ventana de sugerencias -> ocultar
        if w is None:
            self.hide_suggestions()
            return

        # comprobar ascendencia para ver si pertenece a suggestions_window
        temp = w
        inside_suggestions = False
        while temp:
            if str(temp) == str(self.suggestions_window):
                inside_suggestions = True
                break
            temp = getattr(temp, 'master', None)

        if w is self.search_entry or inside_suggestions:
            return

        # click fuera
        self.hide_suggestions()

    def on_type(self, event=None):
        # actualizar la lista mientras se escribe
        self.on_search()

    def on_suggestion_select(self, event=None):
        self.on_suggestion_click(event)

    def on_suggestion_click(self, event=None):
        # obtener selección
        try:
            widget = event.widget
            idxs = widget.curselection()
            if not idxs:
                return
            idx = idxs[0]
        except Exception:
            return

        if idx < 0 or idx >= len(self.suggestions_items):
            return

        type, val = self.suggestions_items[idx]

        # poner valor en el entry
        self.search_entry.delete(0, tk.END)
        if type == 'title':
            base = os.path.splitext(val)[0]
            self.search_entry.insert(0, base)
        else:
            self.search_entry.insert(0, val)

        # aplicar filtro a las tarjetas
        self.apply_filter(type, val)
        self.hide_suggestions()

    def create_ui_file(self, file_path):
        import os
        from datetime import datetime

        name = os.path.basename(file_path)
        path = file_path
        size = os.path.getsize(file_path)
        date_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")

        return UIFile(name, path, size, date_modified)

    def clean_cards(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

    def update_cards(self, files_list=None):
        """Actualiza las tarjetas usando `files_list` si se proporciona, sino `self.files`."""
        self.clean_cards()
        col = 0
        row = 0

        list_to_iterate = files_list if files_list is not None else self.files

        for ui_file in list_to_iterate:
            card = ttk.Frame(self.cards_frame, padding=15, style="Card.TFrame")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="n")

            # --- Header con ícono y nombre ---
            header = ttk.Frame(card)
            header.pack(anchor="w")

            ttk.Label(header, text="📄", font=("Segoe UI", 20)).pack(side="left", padx=(0, 8))
            ttk.Label(header, text=ui_file.name, style="Title.TLabel").pack(side="left")

            # --- Ruta del archivo ---
            ttk.Label(
                card,
                text=ui_file.path,
                font=("Segoe UI", 9),
                foreground="#555",
                wraplength=250
            ).pack(anchor="w", pady=5)

            ttk.Separator(card).pack(fill="x", pady=5)

            # --- Tamaño ---
            ttk.Label(
                card,
                text=f"Tamaño: {round(ui_file.size / 1024, 2)} KB",
                font=("Segoe UI", 10)
            ).pack(anchor="w")

            # --- Fecha ---
            bottom = ttk.Frame(card)
            bottom.pack(anchor="w", pady=(10, 0))

            ttk.Label(bottom, text=f"📅 {ui_file.date_modified}").pack(side="left")

            # manejo de columnas
            col += 1
            if col == 3:
                col = 0
                row += 1



    def run(self):
        self.root.mainloop()

    def apply_filter(self, kind, value):
        """Filtra `self.files` según la selección: 'title' corresponde a nombre de archivo,
        'word' corresponde a palabra de contenido."""
        filtered = []

        if kind == 'title':
            # value contiene filename con extensión (como lo guardó matrizDocumentos)
            for ui_file in self.files:
                if ui_file.name == value or os.path.splitext(ui_file.name)[0].lower() == os.path.splitext(value)[0].lower():
                    filtered.append(ui_file)

        elif kind == 'word':
            # value es la palabra normalizada
            for ui_file in self.files:
                fname = ui_file.name
                if fname in matrizDocumentos:
                    try:
                        # Trae las que tengan esa palabra en contenido
                        if matrizDocumentos[fname][value]:
                            filtered.append(ui_file)
                    except Exception:
                        pass

        # actualizar tarjetas con los resultados filtrados
        self.update_cards(filtered)

    def reset_view(self):
        # limpiar entry, ocultar sugerencias y mostrar todas las cards
        try:
            self.search_entry.delete(0, tk.END)
        except Exception:
            pass
        self.hide_suggestions()
        self.update_cards()


