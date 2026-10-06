"""Native Windows desktop UI. All processing stays on this computer."""
import os
import sys
from pathlib import Path
import queue
import threading
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
os.environ["ARGOS_PACKAGES_DIR"] = str(ROOT / "models")
os.environ["ARGOS_TRANSLATE_PACKAGE_DIR"] = str(ROOT / "models")
os.environ["ARGOS_DEVICE_TYPE"] = "cpu"
from engine import translate_pdf
from glossary import TERMS, AMBIGUOUS, TERM_CATEGORIES, fold
from version import VERSION


class App:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()
        self.stop = threading.Event()
        self.busy = False
        self.saved_output = None
        self.saved_sha = None
        root.title(f"Engineering PDF Translator {VERSION}")
        root.geometry("780x640")
        root.minsize(720, 620)
        root.configure(bg="#f0f4f7")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f4f7")
        style.configure("TLabel", background="#f0f4f7", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11), padding=8)
        frame = ttk.Frame(root, padding=28)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Engineering PDF Translator", font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(frame, text="French / Dutch / German → English · Offline", foreground="#356576").pack(anchor="w", pady=(4,24))
        self.file = tk.StringVar()
        ttk.Label(frame, text="PDF document").pack(anchor="w")
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(5,18))
        ttk.Entry(row, textvariable=self.file).pack(side="left", fill="x", expand=True, ipady=6)
        self.browse = ttk.Button(row, text="Choose PDF…", command=self.choose)
        self.browse.pack(side="right", padx=(10,0))
        ttk.Label(frame, text="Source language").pack(anchor="w")
        self.language = tk.StringVar(value="Choose language…")
        self.lang_box = ttk.Combobox(frame, values=["French", "Dutch", "German"], textvariable=self.language, state="readonly")
        self.lang_box.pack(anchor="w", pady=(5,18), ipady=5)
        self.mode = tk.StringVar(value="replace")
        ttk.Radiobutton(frame, text="Replace text where it fits; add notes for other labels", variable=self.mode, value="replace").pack(anchor="w", pady=4)
        ttk.Radiobutton(frame, text="Keep the original drawing and add translation notes", variable=self.mode, value="notes").pack(anchor="w", pady=4)
        ttk.Label(frame, text="Engineering glossary enabled. Ambiguous terms are marked in the translation list.\nOriginal PDF is retained. Scanned PDFs require OCR and are not supported.", foreground="#536675", wraplength=700).pack(anchor="w", pady=16)
        self.bar = ttk.Progressbar(frame, mode="determinate")
        self.bar.pack(fill="x")
        self.status = tk.StringVar(value="Choose a PDF to begin.")
        ttk.Label(frame, textvariable=self.status, wraplength=680).pack(anchor="w", pady=10)
        controls = ttk.Frame(frame)
        controls.pack(fill="x")
        self.start = ttk.Button(controls, text="Translate and save…", command=self.run)
        self.start.pack(side="left")
        self.cancel = ttk.Button(controls, text="Cancel", command=self.stop.set, state="disabled")
        self.cancel.pack(side="left", padx=10)
        ttk.Button(controls,text="Browse terminology…",command=self.show_glossary).pack(side="right")
        self.open_output = ttk.Button(frame, text="Open verified PDF", command=self.open_saved, state="disabled")
        self.open_output.pack(anchor="w", pady=(10,0))
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(100, self.poll)

    def show_glossary(self):
        window=tk.Toplevel(self.root)
        window.title('Engineering and architectural terminology')
        window.geometry('980x600')
        window.transient(self.root)
        panel=ttk.Frame(window,padding=16);panel.pack(fill='both',expand=True)
        language=tk.StringVar(value=self.language.get() if self.language.get() in ('French','Dutch','German') else 'French')
        search=tk.StringVar()
        count=tk.StringVar()
        row=ttk.Frame(panel);row.pack(fill='x',pady=(0,12))
        ttk.Combobox(row,values=['French','Dutch','German'],textvariable=language,state='readonly',width=12).pack(side='left')
        ttk.Label(row,text='Search term or category:').pack(side='left',padx=10)
        ttk.Entry(row,textvariable=search).pack(side='left',fill='x',expand=True)
        ttk.Label(panel,textvariable=count).pack(anchor='w',pady=(0,8))
        table_frame=ttk.Frame(panel);table_frame.pack(fill='both',expand=True)
        table=ttk.Treeview(table_frame,columns=('source','english','category'),show='headings',selectmode='browse')
        for key,label,width in [('source','Source term',300),('english','English meaning',330),('category','Category',240)]:
            table.heading(key,text=label);table.column(key,width=width)
        scroll=ttk.Scrollbar(table_frame,orient='vertical',command=table.yview)
        table.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y');table.pack(fill='both',expand=True)
        context=tk.StringVar(value='Select a term to view its context note.')
        ttk.Label(panel,textvariable=context,wraplength=920).pack(anchor='w',pady=12)
        notes={}
        def refresh(*args):
            code={'French':'fr','Dutch':'nl','German':'de'}[language.get()]
            query=fold(search.get().strip())
            table.delete(*table.get_children());notes.clear()
            reviews={fold(k):v for k,v in AMBIGUOUS[code].items()}
            entries=sorted(line.split('|',1) for line in TERMS[code].strip().splitlines())
            for source,english in entries:
                category=TERM_CATEGORIES[code].get(fold(source),'Core engineering')
                if query and query not in fold(' '.join((source,english,category))):
                    continue
                item=table.insert('', 'end',values=(source,english,category))
                notes[item]=reviews.get(fold(source),'No special context flag. Check project-specific usage against the drawing legend.')
            count.set(f'{len(table.get_children())} shown / {len(entries)} {language.get()} entries. English is the target language.')
            context.set('Select a term to view its context note.')
        def select(*args):
            selected=table.selection()
            if selected:context.set(notes[selected[0]])
        search.trace_add('write',refresh);language.trace_add('write',refresh)
        table.bind('<<TreeviewSelect>>',select)
        refresh()
        return window,table

    def choose(self):
        name = filedialog.askopenfilename(filetypes=[("PDF documents", "*.pdf")])
        if name:
            self.file.set(name)

    def run(self):
        if self.language.get() not in ('French','Dutch','German'):
            messagebox.showerror('Choose source language','Select French, Dutch or German before translating.')
            return
        source = Path(self.file.get())
        if not source.is_file() or source.suffix.lower() != ".pdf":
            messagebox.showerror("Choose a PDF", "Please select an existing PDF document.")
            return
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        target = filedialog.asksaveasfilename(initialdir=source.parent, initialfile=source.stem + f"_English_{stamp}.pdf", defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not target:
            return
        if Path(target).resolve() == source.resolve():
            messagebox.showerror("Keep the original", "Choose a different filename for the translated PDF.")
            return
        code = {"French": "fr", "Dutch": "nl", "German": "de"}[self.language.get()]
        mode = self.mode.get()
        self.busy = True
        self.saved_output = None
        self.open_output.configure(state="disabled")
        self.stop.clear()
        self.start.configure(state="disabled")
        self.browse.configure(state="disabled")
        self.lang_box.configure(state="disabled")
        self.cancel.configure(state="normal")
        self.status.set(f"Loading {self.language.get()} → English translation model…")
        def worker():
            try:
                from offline import OfflineTranslator
                translate = OfflineTranslator(code)
                result = translate_pdf(source, target, translate, mode, lambda a,b:self.events.put(("progress", (a,b))), self.stop.is_set)
                self.events.put(("done", (target,result)))
            except Exception as exc:
                self.events.put(("error", str(exc)))
        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        try:
            while True:
                kind, data = self.events.get_nowait()
                if kind == "progress":
                    a,b = data
                    self.bar["value"] = a/b*100
                    self.status.set(f"Translated page {a} of {b}…")
                else:
                    self.busy = False
                    self.start.configure(state="normal")
                    self.browse.configure(state="normal")
                    self.lang_box.configure(state="readonly")
                    self.cancel.configure(state="disabled")
                    if kind == "error":
                        self.status.set("Translation stopped.")
                        messagebox.showerror("Translation stopped", data)
                    else:
                        target, result = data
                        self.saved_output = str(Path(target).resolve())
                        self.saved_sha = result['pdf_sha256']
                        self.open_output.configure(state="normal")
                        self.status.set(f"Verified saved PDF: {Path(target).name}")
                        warning = f"\nPages {result['scanned_pages']} contain no selectable text and were not translated." if result['scanned_pages'] else ""
                        message = f"Saved PDF reopened and checked:\n{result['verified_replaced']} replacement labels; {result['verified_notes']} translation notes.\nUnchanged labels to check: {result['unchanged']}.\nRetained drawing references/units: {result['retained']}.\nEngineering glossary matches: {result['glossary_terms']}.\nLabels needing context review: {result['review_labels']}.\n\n{target}\n\nUse Open verified PDF to open this exact file. A .translations.txt list records each label's result." + warning
                        if not result["translated"]:
                            messagebox.showwarning("No labels translated", "No labels changed. Check the selected source language and the .translations.txt report.\n\n" + message)
                        else:
                            messagebox.showinfo(f"Saved — {self.language.get()} to English", message)
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def open_saved(self):
        if self.saved_output:
            try:
                if hashlib.sha256(Path(self.saved_output).read_bytes()).hexdigest() != self.saved_sha:
                    messagebox.showerror('PDF changed', 'This PDF has changed since translation. Translate again to verify a new copy.')
                    return
                os.startfile(self.saved_output)
            except OSError as exc:
                messagebox.showerror('Cannot open PDF', str(exc))

    def close(self):
        if self.busy and not messagebox.askyesno("Translation in progress", "Cancel translation and close?"):
            return
        self.stop.set()
        self.root.destroy()


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        from selftest import run
        run(Path(sys.argv[sys.argv.index("--self-test") + 1]), App)
    else:
        App(tk.Tk()).root.mainloop()
