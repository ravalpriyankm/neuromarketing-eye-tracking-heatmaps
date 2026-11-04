"""Simple local Tk interface. No internet, cloud uploads or tracking."""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from neuromarketing_heatmaps import NONNEGATIVE_EXPRESSIONS
from neuromarketing_heatmaps.processing import clean_folder, load_cleaned, workbook_from_cleaned
from neuromarketing_heatmaps.visualisation import render_heatmap


def main() -> None:
    root = tk.Tk()
    root.title("Neuromarketing Research | Gaze & Expression Heatmaps")
    root.geometry("810x560")
    root.minsize(690, 490)
    wrapper = ttk.Frame(root, padding=18)
    wrapper.pack(fill="both", expand=True)
    ttk.Label(wrapper, text="Gaze & Facial-Expression Research", font=("Arial", 18, "bold")).pack(anchor="w")
    ttk.Label(wrapper, text="Offline tools | University of Essex MSc final project | Research visualisation, not emotion diagnosis",
              foreground="#555555").pack(anchor="w", pady=(4, 15))
    notebook = ttk.Notebook(wrapper)
    notebook.pack(fill="both", expand=True)

    def labelled_entry(parent, label, row, initial="", browse=None):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=8, pady=8)
        var = tk.StringVar(value=initial)
        ttk.Entry(parent, textvariable=var, width=55).grid(row=row, column=1, sticky="ew", padx=8, pady=8)
        if browse:
            ttk.Button(parent, text="Browse", command=lambda: var.set(browse() or var.get())).grid(row=row, column=2, padx=8)
        parent.columnconfigure(1, weight=1)
        return var

    def action(task, success=None):
        try:
            value = task()
        except Exception as exc:
            messagebox.showerror("Research workflow error", str(exc))
        else:
            messagebox.showinfo("Completed", success(value) if success else str(value))

    step1 = ttk.Frame(notebook, padding=18)
    notebook.add(step1, text="1. Clean iMotions CSV")
    ttk.Label(step1, text="Select a folder containing original iMotions CSV exports. Raw participant data stays on your computer.", wraplength=660).grid(row=0, column=0, columnspan=3, sticky="w")
    src = labelled_entry(step1, "CSV input folder", 1, browse=filedialog.askdirectory)
    dst = labelled_entry(step1, "Cleaned output folder", 2, browse=filedialog.askdirectory)
    ttk.Button(step1, text="Clean CSV files", command=lambda: action(lambda: clean_folder(src.get(), dst.get()),
              lambda x: f"Cleaned {len(x)} files into {dst.get()}")).grid(row=3, column=1, sticky="w", pady=18)

    step2 = ttk.Frame(notebook, padding=18)
    notebook.add(step2, text="2. Excel by stimulus")
    cfile = labelled_entry(step2, "Cleaned CSV", 0, browse=lambda: filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("Compressed CSV", "*.gz"), ("All files", "*.*")]))
    outfile = labelled_entry(step2, "Workbook (.xlsx)", 1, browse=lambda: filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel workbook", "*.xlsx")]))
    ttk.Button(step2, text="Create workbook", command=lambda: action(lambda: workbook_from_cleaned(load_cleaned(cfile.get()), outfile.get()))).grid(row=2, column=1, sticky="w", pady=18)

    step3 = ttk.Frame(notebook, padding=16)
    notebook.add(step3, text="3. Generate heatmap")
    clean = labelled_entry(step3, "Cleaned CSV", 0, browse=lambda: filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("Compressed CSV", "*.gz"), ("All files", "*.*")]))
    image = labelled_entry(step3, "Original stimulus image", 1, browse=lambda: filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")]))
    ttk.Label(step3, text="Stimulus name").grid(row=2, column=0, sticky="w", padx=8, pady=8)
    stimulus = tk.StringVar()
    stimulus_picker = ttk.Combobox(step3, textvariable=stimulus, width=52)
    stimulus_picker.grid(row=2, column=1, sticky="ew", padx=8, pady=8)
    def update_stimuli():
        try:
            frame = load_cleaned(clean.get())
            names = sorted(frame["SourceStimuliName"].dropna().astype(str).unique().tolist())
            if not names:
                raise ValueError("The file contains no stimulus names")
            stimulus_picker["values"] = names
            stimulus.set(names[0])
        except Exception as exc:
            messagebox.showerror("Could not read stimuli", str(exc))
    ttk.Button(step3, text="Load names", command=update_stimuli).grid(row=2, column=2, padx=8)
    coords = ttk.Frame(step3)
    coords.grid(row=3, column=0, columnspan=3, sticky="w", pady=10)
    param = {}
    for i,(name,val) in enumerate([("left", "0"), ("top", "0"), ("width", "1920"), ("height", "1080")]):
        ttk.Label(coords, text=name.title()).grid(row=0, column=i*2, padx=4)
        var = tk.StringVar(value=val)
        ttk.Entry(coords, textvariable=var, width=10).grid(row=0, column=i*2+1, padx=4)
        param[name]=var
    ttk.Label(step3, text="Media bounds in recorded screen pixels. Defaults are examples: verify display and image placement.", foreground="#7F4B24", wraplength=650).grid(row=4, column=0, columnspan=3, sticky="w")
    ttk.Label(step3, text="Overlay type").grid(row=5, column=0, sticky="w", pady=8)
    opt = ttk.Combobox(step3, state="readonly", values=["Gaze sample density", *NONNEGATIVE_EXPRESSIONS])
    opt.set("Gaze sample density")
    opt.grid(row=5, column=1, sticky="w", padx=8)
    destination = labelled_entry(step3, "Output image (.png)", 6, browse=lambda: filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")]))
    def generate():
        mode = None if opt.get() == "Gaze sample density" else opt.get()
        result = render_heatmap(load_cleaned(clean.get()), image.get(), destination.get(), stimulus=stimulus.get(),
                                display_left=float(param["left"].get()), display_top=float(param["top"].get()),
                                display_width=int(param["width"].get()), display_height=int(param["height"].get()),
                                expression=mode)
        return result
    ttk.Button(step3, text="Generate overlay", command=lambda: action(generate,
               lambda value: f"Saved: {value['output']}\n\nSamples used: {value['temporally_matched_and_in_bounds_samples']}\n\n{value['warning']}")).grid(row=7, column=1, sticky="w", pady=12)
    root.mainloop()


if __name__ == "__main__":
    main()
