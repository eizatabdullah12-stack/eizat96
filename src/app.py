"""Native four-language Windows UI. Processing stays on this computer."""
import os
import sys
from pathlib import Path
import queue
import threading
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from documents import translate_document, SUPPORTED
from glossary import TERMS, AMBIGUOUS, TERM_CATEGORIES, fold
from directional import DirectionalTranslator, LANGUAGES
from i18n import LANGUAGE_NAMES, text, error_text
from version import VERSION


class App:
    def __init__(self, root):
        self.root=root; self.events=queue.Queue(); self.stop=threading.Event()
        self.busy=False; self.saved_output=self.saved_sha=None
        self.ui_code='en'; self.bindings=[]; self.source_code='auto'; self.active_extension='.pdf'
        root.geometry('980x750'); root.minsize(900,720); root.configure(bg='#f0f4f7')
        style=ttk.Style(); style.theme_use('clam')
        style.configure('TFrame',background='#f0f4f7')
        style.configure('TLabel',background='#f0f4f7',font=('Segoe UI',11))
        style.configure('TButton',font=('Segoe UI',11),padding=8)
        frame=ttk.Frame(root,padding=26); frame.pack(fill='both',expand=True)
        self.label(frame,'title',font=('Segoe UI',22,'bold'),wraplength=900).pack(anchor='w')
        self.label(frame,'subtitle',foreground='#356576').pack(anchor='w',pady=(4,16))
        selectors=ttk.Frame(frame); selectors.pack(fill='x',pady=(0,20))
        for column,key in enumerate(('display_language','source_language','output_language')):
            selectors.columnconfigure(column,weight=1)
            self.label(selectors,key).grid(row=0,column=column,sticky='w',padx=(0,12))
        self.interface_language=tk.StringVar(value=LANGUAGE_NAMES['en'])
        self.ui_box=ttk.Combobox(selectors,textvariable=self.interface_language,
            values=list(LANGUAGE_NAMES.values()),state='readonly',width=23)
        self.ui_box.grid(row=1,column=0,sticky='ew',padx=(0,12),pady=5)
        self.language=tk.StringVar()
        self.lang_box=ttk.Combobox(selectors,textvariable=self.language,state='readonly',width=29)
        self.lang_box.grid(row=1,column=1,sticky='ew',padx=(0,12),pady=5)
        self.output_language=tk.StringVar(value=LANGUAGE_NAMES['en'])
        self.output_box=ttk.Combobox(selectors,textvariable=self.output_language,
            values=list(LANGUAGE_NAMES.values()),state='readonly',width=23)
        self.output_box.grid(row=1,column=2,sticky='ew',pady=5)
        self.ui_box.bind('<<ComboboxSelected>>',self.change_interface)
        self.lang_box.bind('<<ComboboxSelected>>',self.change_source)
        self.label(frame,'document').pack(anchor='w')
        self.file=tk.StringVar(); row=ttk.Frame(frame); row.pack(fill='x',pady=(5,18))
        ttk.Entry(row,textvariable=self.file).pack(side='left',fill='x',expand=True,ipady=6)
        self.browse=self.button(row,'choose_file',self.choose); self.browse.pack(side='right',padx=(10,0))
        self.mode=tk.StringVar(value='replace')
        self.replace_mode=ttk.Radiobutton(frame,variable=self.mode,value='replace')
        self.localize(self.replace_mode,'replace_mode'); self.replace_mode.pack(anchor='w',pady=4)
        self.notes_mode=ttk.Radiobutton(frame,variable=self.mode,value='notes')
        self.localize(self.notes_mode,'notes_mode'); self.notes_mode.pack(anchor='w',pady=4)
        self.label(frame,'help',foreground='#536675',wraplength=910).pack(anchor='w',pady=16)
        self.bar=ttk.Progressbar(frame,mode='determinate'); self.bar.pack(fill='x')
        self.status=tk.StringVar()
        ttk.Label(frame,textvariable=self.status,wraplength=900).pack(anchor='w',pady=10)
        controls=ttk.Frame(frame); controls.pack(fill='x')
        self.start=self.button(controls,'translate_save',self.run); self.start.pack(side='left')
        self.cancel=self.button(controls,'cancel',self.stop.set,state='disabled'); self.cancel.pack(side='left',padx=10)
        self.button(controls,'glossary',self.show_glossary).pack(side='right')
        self.open_output=self.button(frame,'open_verified',self.open_saved,state='disabled')
        self.open_output.pack(anchor='w',pady=(12,0))
        self.file.trace_add('write',self.update_file_type)
        self.apply_interface('en'); root.protocol('WM_DELETE_WINDOW',self.close); root.after(100,self.poll)

    def T(self,key,**values):
        return text(self.ui_code,key,**values)

    def localize(self,widget,key):
        self.bindings.append((widget,key)); widget.configure(text=self.T(key)); return widget

    def label(self,parent,key,**kwargs):
        return self.localize(ttk.Label(parent,**kwargs),key)

    def button(self,parent,key,command,**kwargs):
        return self.localize(ttk.Button(parent,command=command,**kwargs),key)

    def apply_interface(self,language):
        if language not in LANGUAGE_NAMES: raise ValueError('Unsupported interface language')
        self.ui_code=language; self.interface_language.set(LANGUAGE_NAMES[language])
        self.root.title(self.T('title')+' '+VERSION)
        for widget,key in self.bindings:
            if widget.winfo_exists(): widget.configure(text=self.T(key))
        self.source_values={'auto':self.T('auto'),**LANGUAGE_NAMES}
        self.lang_box.configure(values=list(self.source_values.values()))
        self.language.set(self.source_values[self.source_code])
        if not self.busy:
            if self.saved_output: self.status.set(self.T('verified',name=Path(self.saved_output).name))
            else: self.status.set(self.T('office_status') if Path(self.file.get()).suffix.lower() in ('.docx','.pptx') else self.T('begin'))

    def change_interface(self,*args):
        self.apply_interface(next(code for code,name in LANGUAGE_NAMES.items() if name==self.interface_language.get()))

    def change_source(self,*args):
        self.source_code=next(code for code,name in self.source_values.items() if name==self.language.get())

    def target_code(self):
        return next(code for code,name in LANGUAGE_NAMES.items() if name==self.output_language.get())

    def show_glossary(self):
        window=tk.Toplevel(self.root); window.title(self.T('glossary_title'))
        window.geometry('980x600'); window.transient(self.root)
        panel=ttk.Frame(window,padding=16); panel.pack(fill='both',expand=True)
        initial=self.source_code if self.source_code in TERMS else self.ui_code if self.ui_code in TERMS else 'fr'
        language=tk.StringVar(value=LANGUAGE_NAMES[initial]); search=tk.StringVar(); count=tk.StringVar()
        row=ttk.Frame(panel); row.pack(fill='x',pady=(0,12))
        ttk.Combobox(row,values=[LANGUAGE_NAMES[k] for k in TERMS],textvariable=language,state='readonly',width=14).pack(side='left')
        ttk.Label(row,text=self.T('search')).pack(side='left',padx=10)
        ttk.Entry(row,textvariable=search).pack(side='left',fill='x',expand=True)
        ttk.Label(panel,textvariable=count).pack(anchor='w',pady=(0,8))
        grid=ttk.Frame(panel); grid.pack(fill='both',expand=True)
        table=ttk.Treeview(grid,columns=('source','english','category'),show='headings',selectmode='browse')
        for key,label,width in [('source','source_term',300),('english','english_meaning',330),('category','category',240)]:
            table.heading(key,text=self.T(label)); table.column(key,width=width)
        scroll=ttk.Scrollbar(grid,orient='vertical',command=table.yview); table.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y'); table.pack(fill='both',expand=True)
        context=tk.StringVar(value=self.T('select_term'))
        ttk.Label(panel,textvariable=context,wraplength=920).pack(anchor='w',pady=12)
        notes={}
        def refresh(*args):
            code=next(k for k,v in LANGUAGE_NAMES.items() if v==language.get())
            query=fold(search.get().strip()); table.delete(*table.get_children()); notes.clear()
            reviews={fold(k):v for k,v in AMBIGUOUS[code].items()}
            entries=sorted(line.split('|',1) for line in TERMS[code].strip().splitlines())
            for source,english in entries:
                category=TERM_CATEGORIES[code].get(fold(source),'Core engineering')
                if query and query not in fold(' '.join((source,english,category))): continue
                item=table.insert('','end',values=(source,english,category))
                notes[item]=self.T('context_english',note=reviews[fold(source)]) if fold(source) in reviews else self.T('term_default')
            count.set(self.T('term_count',shown=len(table.get_children()),total=len(entries)))
            context.set(self.T('select_term'))
        def select(*args):
            selected=table.selection()
            if selected: context.set(notes[selected[0]])
        language.trace_add('write',refresh); search.trace_add('write',refresh)
        table.bind('<<TreeviewSelect>>',select); refresh()
        return window,table

    def choose(self):
        name=filedialog.askopenfilename(title=self.T('choose_document'),filetypes=[
            (self.T('supported_documents'),'*.pdf *.docx *.pptx'),('PDF','*.pdf'),('Word','*.docx'),('PowerPoint','*.pptx')])
        if name: self.file.set(name)

    def update_file_type(self,*args):
        extension=Path(self.file.get()).suffix.lower()
        state='normal' if extension=='.pdf' and not self.busy else 'disabled'
        self.replace_mode.configure(state=state); self.notes_mode.configure(state=state)
        if not self.busy:
            self.bar['value']=0; self.saved_output=None; self.open_output.configure(state='disabled')
            self.status.set(self.T('office_status') if extension in ('.docx','.pptx') else self.T('begin'))

    def run(self):
        source=Path(self.file.get()); extension=source.suffix.lower()
        if not source.is_file() or extension not in SUPPORTED:
            messagebox.showerror(self.T('choose_document'),self.T('invalid_document')); return
        target_code=self.target_code(); stamp=datetime.now().strftime('%Y%m%d_%H%M%S')
        target=filedialog.asksaveasfilename(title=self.T('save_copy'),initialdir=source.parent,
            initialfile=source.stem+'_'+LANGUAGES[target_code]+'_'+stamp+extension,
            defaultextension=extension,filetypes=[(SUPPORTED[extension],'*'+extension)])
        if not target: return
        if Path(target).resolve()==source.resolve():
            messagebox.showerror(self.T('keep_original'),self.T('different_name')); return
        if Path(target).suffix.lower()!=extension:
            messagebox.showerror(self.T('keep_format'),self.T('same_extension',extension=extension)); return
        code=self.source_code; mode=self.mode.get()
        self.busy=True; self.active_extension=extension; self.saved_output=None
        self.open_output.configure(state='disabled'); self.stop.clear()
        for widget in (self.start,self.browse,self.lang_box,self.ui_box,self.output_box,self.replace_mode,self.notes_mode):
            widget.configure(state='disabled')
        self.cancel.configure(state='normal'); self.status.set(self.T('loading'))
        def worker():
            try:
                translate=DirectionalTranslator(code,target_code)
                result=translate_document(source,target,translate,mode,lambda a,b:self.events.put(('progress',(a,b))),self.stop.is_set)
                result['target_code']=target_code; self.events.put(('done',(target,result)))
            except Exception as exc: self.events.put(('error',str(exc)))
        threading.Thread(target=worker,daemon=True).start()

    def poll(self):
        try:
            while True:
                kind,data=self.events.get_nowait()
                if kind=='progress':
                    current,total=data; self.bar['value']=current/total*100
                    self.status.set(self.T('page_progress' if self.active_extension=='.pdf' else 'part_progress',current=current,total=total))
                    continue
                self.busy=False
                for widget in (self.start,self.browse): widget.configure(state='normal')
                for widget in (self.lang_box,self.ui_box,self.output_box): widget.configure(state='readonly')
                self.cancel.configure(state='disabled')
                state='normal' if Path(self.file.get()).suffix.lower()=='.pdf' else 'disabled'
                self.replace_mode.configure(state=state); self.notes_mode.configure(state=state)
                if kind=='error':
                    self.status.set(self.T('stopped'))
                    messagebox.showerror(self.T('stopped_title'),error_text(self.ui_code,data)); continue
                target,result=data; self.saved_output=str(Path(target).resolve()); self.saved_sha=result['file_sha256']
                self.open_output.configure(state='normal'); self.status.set(self.T('verified',name=Path(target).name))
                if result['format']=='.pdf':
                    message=self.T('pdf_result',replaced=result['verified_replaced'],notes=result['verified_notes'])
                    if result['scanned_pages']: message+='\n'+self.T('scanned_warning',pages=result['scanned_pages'])
                else:
                    message=self.T('office_result',groups=result['verified_groups'],parts=result['verified_parts'])+'\n'+self.T('office_warning')
                message+='\n\n'+self.T('result_details',language=LANGUAGE_NAMES[result['target_code']],unchanged=result['unchanged'],
                    glossary=result['glossary_terms'],reviews=result['review_labels'],path=target)
                if 'detection' in result: message+='\n'+self.T('language_reviews',count=result['detection']['review_segments'])
                if not result['translated']: messagebox.showwarning(self.T('no_changes_title'),self.T('no_changes')+'\n\n'+message)
                else: messagebox.showinfo(self.T('saved_title'),message)
        except queue.Empty: pass
        self.root.after(100,self.poll)

    def open_saved(self):
        if not self.saved_output: return
        try:
            if hashlib.sha256(Path(self.saved_output).read_bytes()).hexdigest()!=self.saved_sha:
                messagebox.showerror(self.T('file_changed_title'),self.T('file_changed')); return
            os.startfile(self.saved_output)
        except OSError as exc: messagebox.showerror(self.T('open_failed'),str(exc))

    def close(self):
        if self.busy and not messagebox.askyesno(self.T('close_title'),self.T('close_question')): return
        self.stop.set(); self.root.destroy()


if __name__=='__main__':
    if '--self-test' in sys.argv:
        from selftest import run
        run(Path(sys.argv[sys.argv.index('--self-test')+1]),App)
    else: App(tk.Tk()).root.mainloop()
