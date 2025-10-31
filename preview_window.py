# preview_window.py
import customtkinter as ctk
from tkinter import ttk
import os

class PreviewWindow(ctk.CTkToplevel):
    """Jendela pop-up untuk menampilkan pratinjau pemindahan file."""
    def __init__(self, parent, planned_moves):
        super().__init__(parent)
        self.title(f"Pratinjau Aksi: {len(planned_moves)} File Akan Dipindah")
        self.geometry("700x550")
        self.transient(parent)
        self.grab_set()
        
        self.planned_moves = planned_moves
        self.result = False # Hasil keputusan pengguna (Lanjutkan atau Batal)
        
        # --- Styling untuk Treeview ---
        style = ttk.Style()
        style.theme_use("default")
        # Sesuaikan warna ini agar cocok dengan tema Light/Dark CustomTkinter
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        
        # --- Widget ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        # Treeview untuk menampilkan rencana
        columns = ("asal", "tujuan")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", style="Treeview")
        self.tree.heading("asal", text="File Asal")
        self.tree.heading("tujuan", text="Tujuan Baru")
        self.tree.column("asal", width=350)
        self.tree.column("tujuan", width=350)
        self.tree.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.populate_tree()

        # Tombol Aksi
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=1, column=0, padx=15, pady=8)
        
        ctk.CTkButton(btn_frame, text="Batal", command=self.cancel, width=110, height=32, fg_color="gray", hover_color="#555555").pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Lanjutkan Proses", command=self.proceed, width=140, height=32, fg_color="#4CAF50", hover_color="#388E3C").pack(side="left", padx=8)

    def populate_tree(self):
        """Mengisi Treeview dengan data dari planned_moves."""
        for source, destination in self.planned_moves:
            # Tampilkan path yang lebih relatif dan mudah dibaca
            asal = os.path.basename(source)
            tujuan = os.path.join(os.path.basename(os.path.dirname(destination)), os.path.basename(destination))
            self.tree.insert("", "end", values=(asal, tujuan))
            
    def proceed(self):
        self.result = True
        self.destroy()

    def cancel(self):
        self.result = False
        self.destroy()