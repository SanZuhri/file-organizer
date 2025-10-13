# organizer_logic.py (Versi 6.0 - Dengan Kemampuan Undo)
import os
import shutil
import json

# Fungsi get_planned_moves tidak berubah sama sekali
def get_planned_moves(path_folder, kategori_rules, recursive=False):
    if not os.path.isdir(path_folder):
        raise ValueError("Path yang diberikan bukan folder yang valid.")
    planned_moves = []
    def get_destination(file_path, filename):
        file_extension = os.path.splitext(filename)[1].lower()
        for category, extensions in kategori_rules.items():
            if file_extension in extensions:
                return os.path.join(path_folder, category, filename)
        return None
    if not recursive:
        for filename in os.listdir(path_folder):
            source_path = os.path.join(path_folder, filename)
            if os.path.isfile(source_path):
                destination_path = get_destination(source_path, filename)
                if destination_path:
                    planned_moves.append((source_path, destination_path))
    else:
        for root, dirs, files in os.walk(path_folder):
            if os.path.basename(root) not in kategori_rules:
                for filename in files:
                    source_path = os.path.join(root, filename)
                    destination_path = get_destination(source_path, filename)
                    if destination_path:
                        planned_moves.append((source_path, destination_path))
    return planned_moves

def execute_moves(planned_moves, progress_queue=None):
    """
    Mengeksekusi pemindahan DAN MENCATATNYA untuk kemungkinan Undo.
    """
    # --- PENAMBAHAN UTAMA: Catat rencana sebelum dieksekusi ---
    try:
        with open("last_operation_log.json", "w") as f:
            json.dump(planned_moves, f, indent=4)
    except Exception as e:
        # Jika gagal mencatat, batalkan seluruh operasi demi keamanan
        if progress_queue:
            progress_queue.put(("LOG_ERROR", f"Gagal membuat log Undo: {e}"))
        return 0

    # Logika pemindahan file yang sudah ada (tidak berubah)
    moved_count = 0
    total_moves = len(planned_moves)
    for i, (source_path, destination_path) in enumerate(planned_moves):
        try:
            destination_folder = os.path.dirname(destination_path)
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            if not os.path.exists(destination_path):
                shutil.move(source_path, destination_path)
                moved_count += 1
                if progress_queue:
                    progress = (i + 1) / total_moves
                    log_message = f"Memindahkan: {os.path.basename(source_path)}"
                    progress_queue.put((progress, log_message))
        except Exception as e:
            if progress_queue:
                progress_queue.put((-1, f"ERROR: Gagal memindahkan {os.path.basename(source_path)}"))
    if progress_queue:
        progress_queue.put(("DONE", moved_count))
    return moved_count

# --- FUNGSI BARU: Logika untuk Undo ---
def undo_last_operation(progress_queue=None):
    """
    Membaca log, membalikkan, dan mengeksekusi pemindahan terbalik.
    """
    try:
        with open("last_operation_log.json", "r") as f:
            moves_to_undo = json.load(f)
    except FileNotFoundError:
        if progress_queue: progress_queue.put(("LOG_ERROR", "Tidak ada operasi terakhir untuk dibatalkan."))
        return 0
    except json.JSONDecodeError:
        if progress_queue: progress_queue.put(("LOG_ERROR", "File log rusak."))
        return 0

    # Membalikkan operasi: tujuan -> asal
    reversed_moves = [(dest, src) for src, dest in moves_to_undo]
    
    # Lakukan eksekusi terbalik (mirip dengan execute_moves)
    moved_count = execute_moves(reversed_moves, progress_queue)

    # Hapus log setelah berhasil undo
    try:
        os.remove("last_operation_log.json")
    except OSError as e:
        if progress_queue: progress_queue.put((-1, f"Peringatan: Gagal menghapus file log: {e}"))

    return moved_count
