import os
import shutil
import subprocess
import threading
import time
import customtkinter as ctk
from tkinter import messagebox
import psutil

# Configure modern UI styling
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SystemCleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Hadziq's Advanced System Cleaner")
        self.geometry("650x700")
        self.resizable(False, False)
        
        # --- TOP FRAME: System Info ---
        self.sys_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.sys_frame.pack(pady=(15, 5), padx=20, fill="x")
        
        self.title_label = ctk.CTkLabel(self.sys_frame, text="System Optimizer", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(side="left")
        
        self.ram_label = ctk.CTkLabel(self.sys_frame, text="RAM: Calculating...", font=ctk.CTkFont(size=12))
        self.ram_label.pack(side="right", padx=10)
        
        self.disk_label = ctk.CTkLabel(self.sys_frame, text="Disk: Calculating...", font=ctk.CTkFont(size=12))
        self.disk_label.pack(side="right", padx=10)

        # --- MIDDLE FRAME: Scrollable Options ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=250)
        self.scroll_frame.pack(pady=10, padx=20, fill="x")
        
        # Variables
        self.var_temp = ctk.BooleanVar(value=True)
        self.var_update = ctk.BooleanVar(value=True)
        self.var_recycle = ctk.BooleanVar(value=True)
        self.var_wer = ctk.BooleanVar(value=False)
        self.var_discord = ctk.BooleanVar(value=True)
        self.var_shaders = ctk.BooleanVar(value=True)
        self.var_games = ctk.BooleanVar(value=True)
        
        # Checkboxes
        ctk.CTkLabel(self.scroll_frame, text="Windows System", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5,0), padx=5)
        ctk.CTkCheckBox(self.scroll_frame, text="Temporary Files & Prefetch", variable=self.var_temp).pack(pady=5, padx=20, anchor="w")
        ctk.CTkCheckBox(self.scroll_frame, text="Windows Update Residue", variable=self.var_update).pack(pady=5, padx=20, anchor="w")
        ctk.CTkCheckBox(self.scroll_frame, text="Empty Recycle Bin", variable=self.var_recycle).pack(pady=5, padx=20, anchor="w")
        ctk.CTkCheckBox(self.scroll_frame, text="Windows Error Reporting (Crash Dumps)", variable=self.var_wer).pack(pady=5, padx=20, anchor="w")
        
        ctk.CTkLabel(self.scroll_frame, text="Applications & Browsers", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(15,0), padx=5)
        ctk.CTkCheckBox(self.scroll_frame, text="Discord Cache", variable=self.var_discord).pack(pady=5, padx=20, anchor="w")
        
        ctk.CTkLabel(self.scroll_frame, text="Gaming Optimization", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(15,0), padx=5)
        ctk.CTkCheckBox(self.scroll_frame, text="DirectX / AMD / NVIDIA Shader Caches", variable=self.var_shaders).pack(pady=5, padx=20, anchor="w")
        ctk.CTkCheckBox(self.scroll_frame, text="Game Logs & Caches (Cyberpunk, Genshin, etc.)", variable=self.var_games).pack(pady=5, padx=20, anchor="w")

        # --- BOTTOM FRAME: Controls & Console ---
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(pady=(15, 5), padx=20, fill="x")
        self.progress_bar.set(0)
        
        self.clean_btn = ctk.CTkButton(self, text="Scan & Clean", command=self.confirm_and_start, height=40, font=ctk.CTkFont(weight="bold"))
        self.clean_btn.pack(pady=10)
        
        self.status_box = ctk.CTkTextbox(self, height=120)
        self.status_box.pack(pady=10, padx=20, fill="x")
        self.status_box.insert("0.0", "Ready to optimize your system...\n")
        self.status_box.configure(state="disabled")

        # Start background monitoring
        self.update_system_stats()

    def update_system_stats(self):
        """Updates RAM and Disk usage every 2 seconds."""
        try:
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\')
            
            ram_gb = ram.used / (1024**3)
            total_ram_gb = ram.total / (1024**3)
            self.ram_label.configure(text=f"RAM: {ram_gb:.1f} / {total_ram_gb:.1f} GB ({ram.percent}%)")
            
            free_disk_gb = disk.free / (1024**3)
            self.disk_label.configure(text=f"Free Space (C:): {free_disk_gb:.1f} GB")
        except Exception:
            pass
        self.after(2000, self.update_system_stats)

    def log_status(self, message):
        self.status_box.configure(state="normal")
        self.status_box.insert("end", message + "\n")
        self.status_box.see("end")
        self.status_box.configure(state="disabled")

    def confirm_and_start(self):
        # Confirmation Dialog
        confirm = messagebox.askyesno("Confirm Cleanup", "Are you sure you want to permanently delete these junk files?")
        if confirm:
            self.clean_btn.configure(state="disabled")
            self.progress_bar.set(0)
            self.log_status("\n--- Starting Deep Cleanup ---")
            threading.Thread(target=self.run_cleaner, daemon=True).start()

    def get_size(self, path):
        """Safely gets file size for calculation."""
        try:
            return os.path.getsize(path)
        except Exception:
            return 0

    def clean_directory(self, paths_to_clean):
        freed_space = 0
        skipped = 0
        total_paths = len(paths_to_clean)
        
        for i, path in enumerate(paths_to_clean):
            if path and os.path.exists(path):
                try:
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        try:
                            if os.path.isfile(item_path):
                                freed_space += self.get_size(item_path)
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                # Accumulate directory size before deleting
                                for dirpath, _, filenames in os.walk(item_path):
                                    for f in filenames:
                                        freed_space += self.get_size(os.path.join(dirpath, f))
                                shutil.rmtree(item_path)
                        except Exception:
                            skipped += 1 # File likely in use
                except Exception:
                    pass
            
            # Update progress bar
            self.progress_bar.set((i + 1) / total_paths)
            
        return freed_space, skipped

    def run_cleaner(self):
        total_freed_bytes = 0
        total_skipped = 0
        paths_target = []
        
        local_app_data = os.environ.get('LOCALAPPDATA')
        roaming_app_data = os.environ.get('APPDATA')

        if self.var_temp.get():
            self.log_status("[*] Targeting Temp & Prefetch...")
            paths_target.extend([os.environ.get('TEMP'), r"C:\Windows\Temp", r"C:\Windows\Prefetch"])
            
        if self.var_wer.get():
            self.log_status("[*] Targeting Crash Dumps...")
            paths_target.append(r"C:\ProgramData\Microsoft\Windows\WER\ReportArchive")

        if self.var_discord.get() and roaming_app_data:
            self.log_status("[*] Targeting Discord Cache...")
            paths_target.extend([
                os.path.join(roaming_app_data, r"discord\Cache\Cache_Data"),
                os.path.join(roaming_app_data, r"discord\Code Cache")
            ])

        if self.var_shaders.get() and local_app_data:
            self.log_status("[*] Targeting GPU Shader Caches...")
            paths_target.extend([
                os.path.join(local_app_data, r"D3DSCache"),
                os.path.join(local_app_data, r"NVIDIA\GLCache"),
                os.path.join(local_app_data, r"AMD\DxCache")
            ])

        if self.var_games.get() and local_app_data:
            self.log_status("[*] Targeting Game Specific Caches...")
            paths_target.extend([
                os.path.join(local_app_data, r"CD Projekt Red\Cyberpunk 2077\cache"),
                os.path.join(os.environ.get('USERPROFILE'), r"AppData\LocalLow\miHoYo\Genshin Impact\Temp")
            ])

        # Execute standard directory cleaning
        if paths_target:
            self.log_status("Sweeping directories...")
            freed, skipped = self.clean_directory(paths_target)
            total_freed_bytes += freed
            total_skipped += skipped

        # Special Case: Windows Update Cache
        if self.var_update.get():
            self.log_status("[*] Halting Windows Update Services...")
            subprocess.run("net stop wuauserv", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("net stop bits", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            freed, skipped = self.clean_directory([r"C:\Windows\SoftwareDistribution\Download"])
            total_freed_bytes += freed
            total_skipped += skipped
            
            self.log_status("[*] Restarting Update Services...")
            subprocess.run("net start wuauserv", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("net start bits", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Special Case: Recycle Bin
        if self.var_recycle.get():
            self.log_status("[*] Flushing Recycle Bin...")
            subprocess.run("rd /s /q %systemdrive%\\$Recycle.Bin", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Format Final Results
        freed_mb = total_freed_bytes / (1024 * 1024)
        if freed_mb > 1024:
            freed_str = f"{freed_mb / 1024:.2f} GB"
        else:
            freed_str = f"{freed_mb:.2f} MB"

        self.progress_bar.set(1.0)
        self.log_status(f"\n✅ Cleanup Complete!")
        self.log_status(f"🚀 Space Freed: {freed_str}")
        if total_skipped > 0:
            self.log_status(f"⚠️ Files skipped (currently in use by Windows): {total_skipped}")
            
        self.clean_btn.configure(state="normal")
        
        # Pop up success message
        messagebox.showinfo("Success", f"Cleanup finished successfully!\nFreed up {freed_str} of space.")

if __name__ == "__main__":
    app = SystemCleanerApp()
    app.mainloop()