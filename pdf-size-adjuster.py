#!/usr/bin/env python3

"""
PDF Size Adjuster

This application provides a graphical user interface for adjusting the page size of PDF files using the cpdf tool.
Linux, macOS, and Windows platforms are supported (64-bit only).

Most code generated by ChatGPT 4.
"""

import tkinter as tk
from tkinter import filedialog
import subprocess
import sys
import urllib.request
import os
import platform
import re
import threading
from datetime import datetime

def download_cpdf():
    if sys.platform.startswith('linux'):
        platform_name = 'Linux-Intel-64bit'
        binary_name = 'cpdf'
    elif sys.platform == 'darwin':
        platform_name = 'OSX-Intel' if platform.processor() == 'i386' else 'OSX-ARM'
        binary_name = 'cpdf'
    elif sys.platform == 'win32':
        platform_name = 'Windows64bit'
        binary_name = 'cpdf.exe'
    else:
        raise Exception("Unsupported platform")

    save_path = os.path.join(os.getcwd(), binary_name)
    if os.path.exists(save_path):
        return save_path

    download_url = f"https://github.com/coherentgraphics/cpdf-binaries/raw/master/{platform_name}/{binary_name}"

    update_message_box(f"Downloading CPDF for {platform_name}...")
    urllib.request.urlretrieve(download_url, save_path)
    update_message_box(f"CPDF downloaded to script directory.")

    if platform_name != 'Windows64bit':
        os.chmod(save_path, 0o755)

    return save_path

def select_file():
    filepath = filedialog.askopenfilename(filetypes=(("PDF files", "*.pdf"),))
    if filepath:
        file_path_var.set(filepath)
        # Automatically update the output file path when a new file is selected
        outfilepattern = re.compile(r'\.pdf$', re.IGNORECASE)
        if outfilepattern.search(filepath):
            outputpath = outfilepattern.sub("-output.pdf", filepath)
            output_file_path_var.set(outputpath)
        else:
            output_file_path_var.set(filepath.replace('.pdf', '-output.pdf'))

def run_cpdf_command_thread():
    filepath = file_path_var.get()
    outputpath = output_file_path_var.get()  # Use the output path from the output_file_path_var
    pagesize = page_size_var.get()
    if pagesize == "Other (e.g. 297mm 210mm)":
        pagesize = custom_page_size_var.get()
    if filepath and pagesize and outputpath:
        try:
            command = [download_cpdf(), '-scale-to-fit', pagesize, filepath, "-o", outputpath]
            subprocess.run(command, check=True, stderr=subprocess.PIPE, text=True)
            update_message_box(f"Success: Adjusted PDF saved to {os.path.basename(outputpath)}")
        except subprocess.CalledProcessError as e:
            lasterrline = e.stderr.strip().split("\n")[-1] if e.stderr else "Unknown error."
            update_message_box(f"CPDF error: {lasterrline}")
        except Exception as e:
            update_message_box(f"Error: {str(e)}")
    else:
        update_message_box("Error: File, output path or page size not given.")

def run_cpdf_command():
    threading.Thread(target=run_cpdf_command_thread).start()

def update_page_size_option(*args):
    if page_size_var.get() == "Other (e.g. 297mm 210mm)":
        custom_page_size_entry.grid(row=3, column=1, columnspan=2, sticky='ew', padx=(10, 0), pady=(5, 0))
        run_button.grid(row=4, column=0, columnspan=3, sticky='ew', pady=(10, 0))
        message_box.grid(row=5, column=0, columnspan=3, sticky='ew', pady=(10, 0))
    else:
        custom_page_size_entry.grid_remove()
        run_button.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(10, 0))
        message_box.grid(row=4, column=0, columnspan=3, sticky='ew', pady=(10, 0))

def update_message_box(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    current_text = message_box.get(1.0, tk.END)
    if current_text != "\n":
        formatted_message = "\n" + formatted_message

    message_box.config(state='normal')
    message_box.insert(tk.END, formatted_message)
    message_box.see(tk.END)
    message_box.config(state='disabled')

root = tk.Tk()
root.title("PDF Size Adjuster")
root.configure(padx=10, pady=10)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(4, weight=1)

file_path_var = tk.StringVar()
output_file_path_var = tk.StringVar()
page_size_var = tk.StringVar()
page_size_var.set("a4portrait")
custom_page_size_var = tk.StringVar()

tk.Label(root, text="Input File:").grid(row=0, column=0, sticky='w')
pdf_entry = tk.Entry(root, textvariable=file_path_var, state='disabled')
pdf_entry.grid(row=0, column=1, sticky='ew', padx=(10, 10))
tk.Button(root, text="Select", command=select_file).grid(row=0, column=2, sticky='ew')

tk.Label(root, text="Output File:").grid(row=1, column=0, sticky='w', pady=(10, 0))
output_file_entry = tk.Entry(root, textvariable=output_file_path_var)
output_file_entry.grid(row=1, column=1, columnspan=2, sticky='ew', padx=(10, 0), pady=(10, 0))

tk.Label(root, text="Page Size:").grid(row=2, column=0, sticky='w', pady=(10, 0))
page_size_options = ["a4portrait", "a4landscape", "Other (e.g. 297mm 210mm)"]
page_size_menu = tk.OptionMenu(root, page_size_var, *page_size_options, command=update_page_size_option)
page_size_menu.grid(row=2, column=1, columnspan=2, sticky='ew', padx=(10, 0), pady=(10, 0))

# Custom Page Size entry (hidden by default)
custom_page_size_entry = tk.Entry(root, textvariable=custom_page_size_var)
custom_page_size_entry.grid_remove()

root.columnconfigure(1, weight=1)

run_button = tk.Button(root, text="Run", command=run_cpdf_command)
run_button.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(10, 0))

message_box = tk.Text(root, height=4, state='disabled')
message_box.grid(row=4, column=0, columnspan=3, sticky='ew', pady=(10, 0))

root.mainloop()
