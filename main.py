import tkinter as tk
from tkinter import filedialog, messagebox
from zipfile import ZipFile
import threading
import time
from datetime import datetime

class ZipCrackerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("ZIP Password Cracker")
        self.master.geometry("800x400")  # Set width and height

        self.zip_file_path = ""
        self.wordlist_path = ""
        self.start_time = None
        self.terminate_flag = False

        # Frame to hold file paths and buttons
        self.frame = tk.Frame(master)
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)

        # Labels to display file paths
        self.zip_label = tk.Label(self.frame, text="ZIP File Path:")
        self.zip_label.grid(row=0, column=0, pady=5, padx=10, sticky=tk.W)

        self.zip_button = tk.Button(self.frame, text="Select ZIP File", command=self.select_zip_file)
        self.zip_button.grid(row=1, column=0, pady=10, padx=10, sticky=tk.W)

        self.wordlist_label = tk.Label(self.frame, text="Wordlist File Path:")
        self.wordlist_label.grid(row=2, column=0, pady=5, padx=10, sticky=tk.W)

        self.wordlist_button = tk.Button(self.frame, text="Select Wordlist File", command=self.select_wordlist_file)
        self.wordlist_button.grid(row=3, column=0, pady=10, padx=10, sticky=tk.W)

        # Text widget for logging
        self.log_text = tk.Text(master, height=20, width=50, wrap=tk.NONE)
        self.log_text.grid(row=0, column=1, rowspan=4, sticky=tk.NS, padx=10)

        # Scrollbar for the log text
        self.scrollbar = tk.Scrollbar(master, command=self.log_text.yview)
        self.scrollbar.grid(row=0, column=2, rowspan=4, sticky=tk.NS)
        self.log_text.config(yscrollcommand=self.scrollbar.set)

        # Buttons
        self.crack_button = tk.Button(master, text="Start Cracking", command=self.start_crack)
        self.crack_button.grid(row=4, column=0, columnspan=3, pady=20)

        self.terminate_button = tk.Button(master, text="Terminate", command=self.terminate_crack)
        self.terminate_button.grid(row=5, column=0, columnspan=3, pady=10)
        self.terminate_button.config(state=tk.DISABLED)

        self.restart_button = tk.Button(master, text="Restart", command=self.restart_app)
        self.restart_button.grid(row=6, column=0, columnspan=3, pady=10)
        self.restart_button.config(state=tk.DISABLED)

        # Time progress label
        self.time_progress_label = tk.Label(master, text="Time Progress: 0%")
        self.time_progress_label.grid(row=7, column=0, columnspan=3)

        # Estimated time label
        self.estimated_time_label = tk.Label(master, text="Estimated Time to Finish: N/A")
        self.estimated_time_label.grid(row=8, column=0, columnspan=3)

        # Duration label for success message
        self.success_duration_label = tk.Label(master, text="")
        self.success_duration_label.grid(row=9, column=0, columnspan=3)

        # Configure row and column weights
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

    def select_zip_file(self):
        self.zip_file_path = filedialog.askopenfilename(filetypes=[("ZIP Files", "*.zip")])
        self.zip_label.config(text=f"ZIP File Path: {self.zip_file_path}")

    def select_wordlist_file(self):
        self.wordlist_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        self.wordlist_label.config(text=f"Wordlist File Path: {self.wordlist_path}")

    def crack_zip(self):
        with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as wordlist_file:
            passwords = wordlist_file.read().splitlines()

        total_passwords = len(passwords)
        self.start_time = time.time()
        self.terminate_flag = False

        for idx, password in enumerate(passwords, start=1):
            if self.terminate_flag:
                self.log_text.insert(tk.END, "Terminating...\n")
                self.log_text.yview(tk.END)
                return

            try:
                with ZipFile(self.zip_file_path, 'r') as zip_file:
                    zip_file.extractall(pwd=password.encode('utf-8'))
                    success_message = f"Success! Password found: {password}"
                    self.log_text.insert(tk.END, success_message + "\n")
                    duration = self.get_duration(self.start_time)
                    self.success_duration_label.config(text=f"Time spent: {duration}")
                    return
            except Exception:
                pass

            self.log_text.insert(tk.END, f"Trying: {password}\n")
            self.log_text.yview(tk.END)
            self.master.update()

            # Calculate and update time progress
            elapsed_time = time.time() - self.start_time
            progress_percentage = (idx / total_passwords) * 100
            remaining_time = (elapsed_time / idx) * (total_passwords - idx)
            remaining_days, remaining_hours, remaining_minutes, remaining_seconds = self.convert_seconds(remaining_time)
            self.time_progress_label.config(
                text=f"Time Progress: {progress_percentage:.2f}%"
            )
            self.estimated_time_label.config(
                text=f"Estimated Time to Finish: {remaining_days} days, {remaining_hours} hours, {remaining_minutes} minutes, {int(remaining_seconds)} seconds"
            )

        self.log_text.insert(tk.END, "Failure! Password not found in the wordlist.\n")
        self.log_text.yview(tk.END)
        self.terminate_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.NORMAL)

    def start_crack(self):
        if not self.zip_file_path or not self.wordlist_path:
            messagebox.showwarning("Warning", "Please select both ZIP file and Wordlist file.")
            return

        self.zip_button.config(state=tk.DISABLED)
        self.wordlist_button.config(state=tk.DISABLED)
        self.crack_button.config(state=tk.DISABLED)
        self.terminate_button.config(state=tk.NORMAL)
        self.restart_button.config(state=tk.DISABLED)

        self.log_text.delete(1.0, tk.END)  # Clear the log
        self.log_text.insert(tk.END, "Cracking in progress...\n")

        threading.Thread(target=self.crack_zip).start()

    def terminate_crack(self):
        self.terminate_flag = True
        self.terminate_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.NORMAL)

    def restart_app(self):
        self.zip_file_path = ""
        self.wordlist_path = ""
        self.start_time = None
        self.terminate_flag = False

        self.zip_label.config(text="ZIP File Path:")
        self.wordlist_label.config(text="Wordlist File Path:")
        self.log_text.delete(1.0, tk.END)
        self.time_progress_label.config(text="Time Progress: 0%")
        self.estimated_time_label.config(text="Estimated Time to Finish: N/A")
        self.success_duration_label.config(text="")

        self.zip_button.config(state=tk.NORMAL)
        self.wordlist_button.config(state=tk.NORMAL)
        self.crack_button.config(state=tk.NORMAL)
        self.terminate_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)

    def convert_seconds(self, seconds):
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return int(days), int(hours), int(minutes), int(seconds)

    def get_duration(self, start_time):
        elapsed_time = time.time() - start_time
        duration = self.convert_seconds(elapsed_time)
        return f"{duration[0]} days, {duration[1]} hours, {duration[2]} minutes, {int(duration[3])} seconds"


if __name__ == "__main__":
    root = tk.Tk()
    app = ZipCrackerApp(root)
    root.mainloop()
