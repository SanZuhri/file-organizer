# main.py (Versi 9.0 - Final dengan Fitur Undo)
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import json
import threading
import queue

from organizer_logic import get_planned_moves, execute_moves, undo_last_operation
from settings_window import SettingsWindow
from preview_window import PreviewWindow

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("File Organizer Pro"); self.geometry("700x550"); self.resizable(False, False)
        self.rules = {}; self.load_rules()
        
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(5, weight=1)

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, rowspan=5, padx=25, pady=20, sticky="nsew")
        
        # --- PERBAIKAN: Konfigurasi grid agar kolom 0 melebar, kolom 1 tidak ---
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=0)

        # Tombol-tombol utama
        self.btn_organize = ctk.CTkButton(main_frame, text="PRATINJAU & RAPİKAN", command=self.run_organization, height=50, font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_organize.grid(row=3, column=0, columnspan=2, pady=10, sticky="we")
        
        self.btn_undo = ctk.CTkButton(main_frame, text="Batalkan Aksi Terakhir (Undo)", command=self.run_undo, fg_color="#F44336", hover_color="#D32F2F")
        self.btn_undo.grid(row=4, column=0, pady=5, sticky="we")

        self.btn_settings = ctk.CTkButton(main_frame, text="Pengaturan Aturan", command=self.open_settings_window, fg_color="gray", hover_color="#555555")
        self.btn_settings.grid(row=4, column=1, padx=(10,0), pady=5, sticky="we")

        # Widget lainnya...
        ctk.CTkLabel(main_frame, text="Folder untuk Dirapikan", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        
        self.target_directory = ctk.StringVar()
        
        # --- PERBAIKAN: Entry sekarang hanya di kolom 0 ---
        entry = ctk.CTkEntry(main_frame, textvariable=self.target_directory, state="readonly", height=35)
        entry.grid(row=1, column=0, pady=10, sticky="we") # Dulu: columnspan=2
        
        # --- PERBAIKAN: Tombol "Pilih Folder" dikembalikan ke kolom 1 ---
        self.btn_select = ctk.CTkButton(main_frame, text="Pilih Folder...", command=self.select_folder, width=120, height=35)
        self.btn_select.grid(row=1, column=1, padx=(10, 0))

        self.recursive_var = ctk.BooleanVar(value=False)
        recursive_check = ctk.CTkCheckBox(main_frame, text="Jelajahi semua sub-folder (Rekursif)", variable=self.recursive_var)
        recursive_check.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(self, mode='determinate')
        self.progress_bar.set(0)
        self.progress_bar.grid(row=5, column=0, padx=25, pady=5, sticky="ew")

        self.log_box = ctk.CTkTextbox(self, height=150, state="disabled", text_color="cyan")
        self.log_box.grid(row=6, column=0, padx=25, pady=(0,20), sticky="nsew")

        self.check_undo_availability() # Cek saat startup apakah ada aksi yang bisa di-undo

    def toggle_buttons(self, enabled=True):
        """Fungsi bantuan untuk mengaktifkan/menonaktifkan semua tombol."""
        state = "normal" if enabled else "disabled"
        self.btn_organize.configure(state=state)
        self.btn_settings.configure(state=state)
        # Tombol Undo hanya diaktifkan jika file log ada
        if enabled:
            self.check_undo_availability()
        else:
            self.btn_undo.configure(state="disabled")

    def check_undo_availability(self):
        """Mengaktifkan tombol Undo jika file log ada."""
        if os.path.exists("last_operation_log.json"):
            self.btn_undo.configure(state="normal")
        else:
            self.btn_undo.configure(state="disabled")

    def run_organization(self):
        # ... (fungsi ini sama, hanya memanggil self.toggle_buttons())
        folder_path = self.target_directory.get();
        if not folder_path: messagebox.showwarning("Peringatan", "Pilih folder dulu!"); return
        
        try:
            planned_moves = get_planned_moves(folder_path, self.rules, self.recursive_var.get())
            if not planned_moves: messagebox.showinfo("Informasi", "Tidak ada file yang perlu dirapikan."); return

            preview_win = PreviewWindow(self, planned_moves)
            self.wait_window(preview_win)

            if preview_win.result:
                self.progress_queue = queue.Queue()
                self.log_box.configure(state="normal"); self.log_box.delete("1.0", "end"); self.log_box.configure(state="disabled")
                self.progress_bar.set(0)
                self.toggle_buttons(enabled=False) # Nonaktifkan tombol
                self.btn_organize.configure(text="Sedang Bekerja...")

                threading.Thread(target=execute_moves, args=(planned_moves, self.progress_queue)).start()
                self.monitor_progress(is_undo=False)
        except Exception as e: messagebox.showerror("Error", f"Terjadi error:\n{e}")
    
    def run_undo(self):
        """Memicu proses Undo."""
        if not messagebox.askyesno("Konfirmasi Undo", "Anda yakin ingin membatalkan aksi perapian terakhir?"):
            return
        
        self.progress_queue = queue.Queue()
        self.log_box.configure(state="normal"); self.log_box.delete("1.0", "end"); self.log_box.configure(state="disabled")
        self.progress_bar.set(0)
        self.toggle_buttons(enabled=False) # Nonaktifkan tombol
        self.btn_undo.configure(text="Membatalkan...")
        
        threading.Thread(target=undo_last_operation, args=(self.progress_queue,)).start()
        self.monitor_progress(is_undo=True) # Monitor proses Undo

    def monitor_progress(self, is_undo=False):
        """Satu fungsi monitor untuk menangani proses Rapikan dan Undo."""
        try:
            message = self.progress_queue.get_nowait()
            progress, log_text = message
            
            if progress == "DONE":
                self.progress_bar.set(1)
                final_log = f"\n--- {'UNDO SELESAI' if is_undo else 'SELESAI'}: {log_text} file {'dikembalikan' if is_undo else 'dipindahkan'} ---\n"
                self.log_box.configure(state="normal"); self.log_box.insert("end", final_log); self.log_box.configure(state="disabled")
                messagebox.showinfo("Sukses", "Proses berhasil diselesaikan!")
                
                self.toggle_buttons(enabled=True) # Aktifkan kembali tombol
                self.btn_organize.configure(text="PRATINJAU & RAPİKAN")
                self.btn_undo.configure(text="Batalkan Aksi Terakhir (Undo)")
                return
            elif progress == "LOG_ERROR":
                 messagebox.showerror("Error Kritis", log_text)
                 self.toggle_buttons(enabled=True); self.btn_organize.configure(text="PRATINJAU & RAPİKAN")
                 return
            
            # Update UI seperti biasa
            self.progress_bar.set(progress if progress != -1 else self.progress_bar.get())
            self.log_box.configure(state="normal"); self.log_box.insert("end", log_text + "\n"); self.log_box.configure(state="disabled")
            self.log_box.see("end")

            self.after(100, self.monitor_progress, is_undo)
        except queue.Empty:
            self.after(100, self.monitor_progress, is_undo)

    # Fungsi lain-lain (load_rules, update_rules, dll) tidak berubah
    def load_rules(self):
        try:
            with open("rules.json", "r") as f: self.rules = json.load(f)
        except FileNotFoundError:
            self.rules = {}; print("Warning: 'rules.json' not found.")
    def update_rules(self, new_rules):
        self.rules = new_rules
        try:
            with open("rules.json", "w") as f: json.dump(self.rules, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", "Gagal menyimpan aturan: " + str(e))
        self.load_rules()
    def open_settings_window(self):
        SettingsWindow(self, self.rules)
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected: self.target_directory.set(folder_selected)

if __name__ == "__main__":
    app = App()
    app.mainloop()