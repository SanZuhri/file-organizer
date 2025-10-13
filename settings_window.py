# settings_window.py (Versi 2.0 - Ditingkatkan dengan CustomTkinter)
import customtkinter as ctk
from tkinter import ttk # Kita masih butuh ttk untuk Treeview
import json

class SettingsWindow(ctk.CTkToplevel):
    """Jendela pop-up untuk mengelola aturan kategori file."""
    def __init__(self, parent, rules):
        super().__init__(parent)
        self.title("Pengaturan Aturan Kustom")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        
        self.rules = rules.copy()
        self.parent = parent
        
        # --- Konfigurasi Grid ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Styling untuk Treeview agar cocok ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        rowheight=25, 
                        fieldbackground="#2b2b2b",
                        bordercolor="#2b2b2b",
                        lightcolor="#2b2b2b",
                        darkcolor="#2b2b2b")
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", font=('Calibri', 10, 'bold'))

        # --- Widget ---
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        frame.grid_columnconfigure((0, 1), weight=1)

        # Treeview untuk menampilkan aturan
        columns = ("kategori", "ekstensi")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=10, style="Treeview")
        self.tree.heading("kategori", text="Nama Kategori")
        self.tree.heading("ekstensi", text="Ekstensi (dipisah koma)")
        self.tree.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.populate_tree()
        
        # Form untuk menambah/mengedit
        self.category_var = ctk.StringVar()
        ctk.CTkEntry(frame, textvariable=self.category_var, placeholder_text="NAMA KATEGORI").grid(row=1, column=0, padx=(10,5), pady=10, sticky="we")
        
        self.extensions_var = ctk.StringVar()
        ctk.CTkEntry(frame, textvariable=self.extensions_var, placeholder_text=".jpg, .png, .gif").grid(row=1, column=1, padx=(5,10), pady=10, sticky="we")
        
        # Tombol Aksi
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ctk.CTkButton(btn_frame, text="Tambah/Update", command=self.add_or_update_rule).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Hapus Terpilih", command=self.delete_rule, fg_color="#D32F2F", hover_color="#B71C1C").pack(side="left", padx=5)
        
        # Tombol Simpan & Tutup
        ctk.CTkButton(frame, text="Simpan dan Tutup", command=self.save_and_close, fg_color="#4CAF50", hover_color="#388E3C").grid(row=3, column=0, columnspan=2, pady=10, ipady=5)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
    
    # Fungsi lainnya (populate_tree, on_item_select, dll) tetap sama persis
    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for category, extensions in self.rules.items():
            self.tree.insert("", "end", values=(category, ", ".join(extensions)))

    def on_item_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            self.category_var.set(values[0])
            self.extensions_var.set(values[1])

    def add_or_update_rule(self):
        category = self.category_var.get().upper().strip()
        extensions = [f".{ext.strip().lstrip('.')}".lower() for ext in self.extensions_var.get().split(',') if ext.strip()]
        if category and extensions:
            self.rules[category] = extensions
            self.populate_tree()
            self.category_var.set("")
            self.extensions_var.set("")

    def delete_rule(self):
        category = self.category_var.get().upper().strip()
        if category and category in self.rules:
            del self.rules[category]
            self.populate_tree()
            self.category_var.set("")
            self.extensions_var.set("")
            
    def save_and_close(self):
        self.parent.update_rules(self.rules)
        self.destroy()