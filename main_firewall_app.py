# main_firewall_app.py

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as bstrap
from ttkbootstrap.constants import *
import psutil
import sys
import os
import subprocess
import threading

class FirewallApp:
    def __init__(self, root):
        self.root = root
        self.full_app_list = []  
        self.setup_gui()
        self.start_populate_thread()

    def setup_gui(self):
        
        self.root.title("Aegis Firewall")
        self.root.geometry("800x600")
        main_frame = bstrap.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        list_header = bstrap.Label(main_frame, text="Active Applications", font=("Helvetica", 14, "bold"))
        list_header.pack(pady=(0, 5))
        search_frame = bstrap.Frame(main_frame)
        search_frame.pack(fill=X, pady=(0, 10), padx=10)
        search_label = bstrap.Label(search_frame, text="Search:")
        search_label.pack(side=LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        
        self.search_var.trace_add("write", self._update_gui_from_cache)
        search_entry = bstrap.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=LEFT, fill=X, expand=YES)
        columns = ("app_name", "status")
        self.app_list_tree = bstrap.Treeview(main_frame, columns=columns, show="headings", bootstyle="info")
        self.app_list_tree.heading("app_name", text="Application Name")
        self.app_list_tree.heading("status", text="Status")
        self.app_list_tree.column("status", width=120, anchor="center")
        self.app_list_tree.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        self.app_list_tree.tag_configure("blocked_row", foreground="tomato")
        button_frame = bstrap.Frame(main_frame)
        button_frame.pack(fill=X, pady=10)
        self.block_btn = bstrap.Button(button_frame, text="Block Selected", bootstyle="danger", command=self.block_selected_app)
        self.block_btn.pack(side=LEFT, expand=YES, padx=5)
        self.unblock_btn = bstrap.Button(button_frame, text="Unblock Selected", bootstyle="success", command=self.unblock_selected_app)
        self.unblock_btn.pack(side=LEFT, expand=YES, padx=5)
        
        self.refresh_btn = bstrap.Button(button_frame, text="Refresh List", bootstyle="info-outline", command=self.refresh_and_clear)
        self.refresh_btn.pack(side=RIGHT, padx=5)
        
        self.progress_bar = bstrap.Progressbar(self.root, mode='indeterminate', bootstyle="info-striped")
        self.progress_bar.pack(side=BOTTOM, fill=X, padx=10, pady=5)
        self.status_label = bstrap.Label(self.root, text="Status: Initializing...", anchor=W, padding=10, bootstyle="inverse-secondary")
        self.status_label.pack(side=BOTTOM, fill=X)


    def set_ui_state(self, is_busy):
        
        state = "disabled" if is_busy else "normal"
        self.block_btn.config(state=state)
        self.unblock_btn.config(state=state)
        self.refresh_btn.config(state=state)
        if is_busy:
            self.progress_bar.start()
        else:
            self.progress_bar.stop()

    def start_populate_thread(self):
        
        self.set_ui_state(True)
        self.update_status("Refreshing application list... Please wait.")
        thread = threading.Thread(target=self._populate_app_list_logic, daemon=True)
        thread.start()

    def _populate_app_list_logic(self):
        """Worker thread: Sirf user applications laata hai, system processes ko filter karta hai."""
        temp_app_info = []
        processed_names = set()

        
        windows_path = os.path.normcase(os.environ.get("SystemRoot", "C:\\Windows"))

        for process in psutil.process_iter(['name', 'exe']):
            try:
                proc_name = process.info['name']
                if proc_name in processed_names:
                    continue

                proc_path = process.info['exe']

                if proc_path and os.path.normcase(proc_path).startswith(windows_path):
                    continue

                if proc_path and proc_name.endswith('.exe'):
                    rule_name = f"ProjectAegis_{proc_name}"
                    status = "Blocked" if self.check_rule_exists(rule_name) else "Not Blocked"
                    temp_app_info.append({'name': proc_name, 'path': proc_path, 'status': status})
                    processed_names.add(proc_name)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        self.root.after(0, self._process_fetched_data, temp_app_info)
        
    def _process_fetched_data(self, results):
        """Main thread: Naye data ko cache me store karta hai aur GUI update karta hai"""
        self.full_app_list = sorted(results, key=lambda x: x['name'].lower())
        self._update_gui_from_cache() # GUI ko nayi cache se update karo
        self.set_ui_state(False)
        self.update_status("Ready")

    def _update_gui_from_cache(self, *args):
        """Sirf cache se data filter karke GUI me dikhata hai (Tez Kaam)"""
        search_term = self.search_var.get().lower()
        
        for item in self.app_list_tree.get_children():
            self.app_list_tree.delete(item)

        for app_info in self.full_app_list:
            if search_term in app_info['name'].lower():
                tags = ("blocked_row",) if app_info['status'] == "Blocked" else ()
                self.app_list_tree.insert("", END, values=(app_info['name'], app_info['status']), tags=tags)

    def refresh_and_clear(self):
        """Search box ko clear karta hai aur data fetching shuru karta hai"""
        self.search_var.set("")
        self.start_populate_thread()
        
    def block_selected_app(self):
        selected_item, app_name, app_path = self.get_selected_app_info()
        if not selected_item: return
        rule_name = f"ProjectAegis_{app_name}"
        command = f'netsh advfirewall firewall add rule name="{rule_name}" dir=out action=block program="{app_path}"'
        if self.run_firewall_command(command, f"Success: '{app_name}' blocked.", f"Error blocking '{app_name}'."):
            self.refresh_and_clear()

    def unblock_selected_app(self):
        selected_item, app_name, app_path = self.get_selected_app_info()
        if not selected_item: return
        rule_name = f"ProjectAegis_{app_name}"
        command = f'netsh advfirewall firewall delete rule name="{rule_name}"'
        if self.run_firewall_command(command, f"Success: '{app_name}' unblocked.", f"Error unblocking '{app_name}'."):
            self.refresh_and_clear()

    def update_status(self, message): self.status_label.config(text=f"Status: {message}")
    def check_rule_exists(self, rule_name):
        command = f'netsh advfirewall firewall show rule name="{rule_name}"'
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return "No rules match" not in result.stdout
        except subprocess.CalledProcessError: return False
    def run_firewall_command(self, command, success_msg, failure_msg):
        try:
            subprocess.run(command, shell=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.update_status(success_msg); return True
        except: self.update_status(failure_msg); return False
    def get_selected_app_info(self):
        selected_items = self.app_list_tree.selection()
        if not selected_items: self.update_status("Error: Koi application select nahi ki gayi hai."); return None, None, None
        selected_item = selected_items[0]
        app_name = self.app_list_tree.item(selected_item, "values")[0]
        app_data = next((item for item in self.full_app_list if item["name"] == app_name), None)
        app_path = app_data['path'] if app_data else None
        return selected_item, app_name, app_path


if __name__ == "__main__":
    root = bstrap.Window(themename="darkly")
    app = FirewallApp(root)
    root.mainloop()