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
from tkinter.scrolledtext import ScrolledText
from documents import translate_document, SUPPORTED
from glossary import TERMS, AMBIGUOUS, TERM_CATEGORIES, fold
from directional import DirectionalTranslator, LANGUAGES
from i18n import LANGUAGE_NAMES, text, error_text
from version import VERSION
from branding import CREATOR, tk_logo
from conversation import PHRASES
from text_translation import TextWorker, LIVE_TEXT_CHARS, MAX_TEXT_CHARS


class App:
    def __init__(self, root):
        self.root=root; self.events=queue.Queue(); self.stop=threading.Event()
        self.busy=False; self.saved_output=self.saved_sha=None
        self.ui_code='en'; self.bindings=[]; self.source_code='auto'; self.active_extension='.pdf'
        self.processing_lock=threading.Lock()
        self.text_worker=TextWorker(self.events.put,self.processing_lock)
        self.text_generation=0; self.text_after=None; self.text_result=None
        root.geometry('1040x820'); root.minsize(940,760); root.configure(bg='#f0f4f7')
        style=ttk.Style(); style.theme_use('clam')
        style.configure('TFrame',background='#f0f4f7')
        style.configure('TLabel',background='#f0f4f7',font=('Segoe UI',11))
        style.configure('TButton',font=('Segoe UI',11),padding=8)
        frame=ttk.Frame(root,padding=26); frame.pack(fill='both',expand=True)
        self.logo=tk_logo(root,64); self.window_logo=tk_logo(root,128)
        root.iconphoto(True,self.window_logo)
        header=ttk.Frame(frame); header.pack(fill='x',pady=(0,16))
        ttk.Label(header,image=self.logo).pack(side='left',padx=(0,16))
        heading=ttk.Frame(header); heading.pack(side='left',fill='x',expand=True)
        self.label(heading,'title',font=('Segoe UI',22,'bold'),wraplength=830).pack(anchor='w')
        self.label(heading,'subtitle',foreground='#356576').pack(anchor='w',pady=(4,0))
        self.label(heading,'creator',foreground='#536675',font=('Segoe UI',10)).pack(anchor='w',pady=(3,0))
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
        self.output_box.bind('<<ComboboxSelected>>',self.invalidate_text)
        self.tabs=ttk.Notebook(frame); self.tabs.pack(fill='both',expand=True)
        self.text_tab=ttk.Frame(self.tabs,padding=14)
        self.document_tab=ttk.Frame(self.tabs,padding=14)
        self.tabs.add(self.text_tab,text=self.T('text_tab'))
        self.tabs.add(self.document_tab,text=self.T('documents_tab'))
        self.build_text_tab()
        self.button(frame,'glossary',self.show_glossary).pack(anchor='e',pady=(10,0))
        frame=self.document_tab
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
        self.tabs.tab(self.text_tab,text=self.T('text_tab'))
        self.tabs.tab(self.document_tab,text=self.T('documents_tab'))
        self.refresh_text_status()
        if not self.busy:
            if self.saved_output: self.status.set(self.T('verified',name=Path(self.saved_output).name))
            else: self.status.set(self.T('office_status') if Path(self.file.get()).suffix.lower() in ('.docx','.pptx') else self.T('begin'))

    def change_interface(self,*args):
        self.apply_interface(next(code for code,name in LANGUAGE_NAMES.items() if name==self.interface_language.get()))

    def change_source(self,*args):
        self.source_code=next(code for code,name in self.source_values.items() if name==self.language.get())
        self.invalidate_text()

    def target_code(self):
        return next(code for code,name in LANGUAGE_NAMES.items() if name==self.output_language.get())

    def build_text_tab(self):
        panel=self.text_tab
        self.text_style=tk.StringVar(value='conversation')
        choices=ttk.Frame(panel); choices.pack(fill='x',pady=(0,6))
        self.label(choices,'text_style').pack(side='left',padx=(0,12))
        for code,key in [('conversation','conversation_mode'),('engineering','engineering_mode')]:
            option=ttk.Radiobutton(choices,variable=self.text_style,value=code,command=self.invalidate_text)
            self.localize(option,key).pack(side='left',padx=(0,16))
        self.label(panel,'conversation_hint',foreground='#536675',wraplength=940,font=('Segoe UI',10)).pack(anchor='w',pady=(0,8))
        columns=ttk.Frame(panel); columns.pack(fill='both',expand=True)
        for column in range(2): columns.columnconfigure(column,weight=1,uniform='text')
        columns.rowconfigure(1,weight=1)
        self.label(columns,'text_input').grid(row=0,column=0,sticky='w',pady=(0,5))
        self.label(columns,'text_output').grid(row=0,column=1,sticky='w',pady=(0,5),padx=(12,0))
        self.text_input=ScrolledText(columns,wrap='word',undo=True,font=('Segoe UI',12),width=32,height=12,padx=10,pady=10)
        self.text_input.grid(row=1,column=0,sticky='nsew')
        self.text_output=ScrolledText(columns,wrap='word',state='disabled',font=('Segoe UI',12),width=32,height=12,padx=10,pady=10)
        self.text_output.grid(row=1,column=1,sticky='nsew',padx=(12,0))
        self.text_input.bind('<<Modified>>',self.on_text_edit)
        self.text_input.bind('<Control-Return>',lambda event:(self.translate_text_now(),'break')[1])
        self.text_input.edit_modified(False)
        controls=ttk.Frame(panel); controls.pack(fill='x',pady=(10,0))
        self.auto_text=tk.BooleanVar(value=True)
        self.auto_text_button=self.localize(ttk.Checkbutton(controls,variable=self.auto_text,command=self.invalidate_text),'text_auto')
        self.auto_text_button.pack(side='left')
        self.text_translate=self.button(controls,'text_translate',self.translate_text_now)
        self.text_translate.pack(side='right')
        actions=ttk.Frame(panel); actions.pack(fill='x',pady=6)
        self.button(actions,'text_paste',self.paste_text).pack(side='left')
        self.button(actions,'text_clear',self.clear_text).pack(side='left',padx=8)
        self.text_copy=self.button(actions,'text_copy',self.copy_text,state='disabled')
        self.text_copy.pack(side='right')
        self.text_status=tk.StringVar(value=self.T('text_ready'))
        ttk.Label(panel,textvariable=self.text_status,wraplength=940).pack(anchor='w',pady=(4,0))
        self.text_review=ScrolledText(panel,wrap='word',state='disabled',height=3,font=('Segoe UI',10),foreground='#865c0a')
        self.text_review.pack(fill='x',pady=(6,0))

    def set_text_output(self,value):
        self.text_output.configure(state='normal'); self.text_output.delete('1.0','end')
        self.text_output.insert('1.0',value); self.text_output.configure(state='disabled')

    def on_text_edit(self,*args):
        if self.text_input.edit_modified():
            self.text_input.edit_modified(False)
            self.invalidate_text()

    def invalidate_text(self,*args):
        self.text_generation+=1; self.text_worker.cancel()
        if self.text_after is not None:
            self.root.after_cancel(self.text_after); self.text_after=None
        self.text_result=None; self.set_text_output('')
        self.text_copy.configure(state='disabled'); self.set_text_reviews('')
        value=self.text_input.get('1.0','end-1c')
        if len(value)>MAX_TEXT_CHARS:
            self.text_status.set(self.T('text_limit')); return
        if self.busy:
            self.text_status.set(self.T('text_paused')); return
        if value.strip() and self.auto_text.get() and len(value)<=LIVE_TEXT_CHARS:
            self.text_status.set(self.T('text_waiting'))
            self.text_after=self.root.after(750,self.translate_text_now)
        else:
            self.text_status.set(self.T('text_long') if len(value)>LIVE_TEXT_CHARS else self.T('text_ready'))

    def translate_text_now(self):
        if self.text_after is not None:
            self.root.after_cancel(self.text_after); self.text_after=None
        if self.busy:
            self.text_status.set(self.T('text_paused')); return
        value=self.text_input.get('1.0','end-1c')
        if not value.strip():
            self.invalidate_text(); return
        if len(value)>MAX_TEXT_CHARS:
            self.text_status.set(self.T('text_limit')); return
        self.text_generation+=1; self.text_result=None
        self.set_text_output(''); self.text_copy.configure(state='disabled'); self.set_text_reviews('')
        self.text_status.set(self.T('text_working'))
        self.text_worker.submit(self.text_generation,value,self.source_code,self.target_code(),self.text_style.get())

    def refresh_text_status(self):
        if self.text_result is None:
            if not self.text_input.get('1.0','end-1c').strip(): self.text_status.set(self.T('text_ready'))
            return
        names=', '.join(LANGUAGE_NAMES.get(code,self.T('text_uncertain')) for code in self.text_result['languages'])
        self.text_status.set(self.T('text_complete',languages=names or '—',count=len(self.text_result['reviews'])))
        if self.text_result['reviews']:
            self.set_text_reviews(self.T('text_review')+'\n'+'\n'.join(self.text_result['reviews']))

    def set_text_reviews(self,value):
        self.text_review.configure(state='normal'); self.text_review.delete('1.0','end')
        self.text_review.insert('1.0',value); self.text_review.configure(state='disabled')

    def paste_text(self):
        try: value=self.root.clipboard_get()
        except tk.TclError:
            self.text_status.set(self.T('text_clipboard')); return
        try: self.text_input.delete('sel.first','sel.last')
        except tk.TclError: pass
        self.text_input.insert('insert',value); self.text_input.focus_set()

    def clear_text(self):
        self.text_input.delete('1.0','end'); self.text_input.edit_reset()
        self.text_input.edit_modified(False); self.invalidate_text(); self.text_input.focus_set()

    def copy_text(self):
        if self.text_result is not None:
            self.root.clipboard_clear(); self.root.clipboard_append(self.text_result['text'])
            self.text_status.set(self.T('text_copied'))

    def show_glossary(self):
        window=tk.Toplevel(self.root); window.title(self.T('glossary_title'))
        window.geometry('980x600'); window.transient(self.root)
        panel=ttk.Frame(window,padding=16); panel.pack(fill='both',expand=True)
        initial=self.source_code if self.source_code in LANGUAGE_NAMES else self.ui_code
        language=tk.StringVar(value=LANGUAGE_NAMES[initial]); search=tk.StringVar(); count=tk.StringVar()
        row=ttk.Frame(panel); row.pack(fill='x',pady=(0,12))
        ttk.Combobox(row,values=list(LANGUAGE_NAMES.values()),textvariable=language,state='readonly',width=14).pack(side='left')
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
            reviews={fold(k):v for k,v in AMBIGUOUS.get(code,{}).items()}
            entries=[(source,english,TERM_CATEGORIES[code].get(fold(source),'Core engineering'))
                     for line in TERMS.get(code,'').strip().splitlines() for source,english in [line.split('|',1)]]
            entries.extend((row[code].replace(';',' / '),row['en'].split(';')[0],row['category']) for row in PHRASES)
            entries.sort()
            for source,english,category in entries:
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
        self.text_worker.cancel()
        if self.text_after is not None:
            self.root.after_cancel(self.text_after); self.text_after=None
        self.text_translate.configure(state='disabled'); self.text_status.set(self.T('text_paused'))
        self.open_output.configure(state='disabled'); self.stop.clear()
        for widget in (self.start,self.browse,self.lang_box,self.ui_box,self.output_box,self.replace_mode,self.notes_mode):
            widget.configure(state='disabled')
        self.cancel.configure(state='normal'); self.status.set(self.T('loading'))
        def worker():
            try:
                with self.processing_lock:
                    translate=DirectionalTranslator(code,target_code)
                    result=translate_document(source,target,translate,mode,lambda a,b:self.events.put(('progress',(a,b))),self.stop.is_set)
                result['target_code']=target_code; self.events.put(('done',(target,result)))
            except Exception as exc: self.events.put(('error',str(exc)))
        threading.Thread(target=worker,daemon=True).start()

    def poll(self):
        try:
            while True:
                kind,data=self.events.get_nowait()
                if kind=='text_done':
                    generation,result,error=data
                    if generation==self.text_generation and not self.busy:
                        if error: self.text_status.set(error_text(self.ui_code,error))
                        else:
                            self.text_result=result; self.set_text_output(result['text'])
                            self.text_copy.configure(state='normal' if result['text'] else 'disabled')
                            self.refresh_text_status()
                    continue
                if kind=='progress':
                    current,total=data; self.bar['value']=current/total*100
                    self.status.set(self.T('page_progress' if self.active_extension=='.pdf' else 'part_progress',current=current,total=total))
                    continue
                self.busy=False
                self.text_translate.configure(state='normal'); self.invalidate_text()
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
        self.stop.set(); self.text_worker.close(); self.root.destroy()


if __name__=='__main__':
    if '--self-test' in sys.argv:
        from selftest import run
        try:
            run(Path(sys.argv[sys.argv.index('--self-test')+1]),App)
        except Exception:
            # The JSON report records the exception. A windowed error dialog
            # would otherwise keep CI running until its five-minute timeout.
            sys.exit(1)
    else: App(tk.Tk()).root.mainloop()
