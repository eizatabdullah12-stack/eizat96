"""Localized personal glossary editor; network work never blocks Tk."""
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import webbrowser
from i18n import LANGUAGE_NAMES
from personal_glossary import PersonalStore, entry_key, normalized
from online_lookup import lookup, search_url, PROVIDER


class PersonalGlossaryWindow:
    def __init__(self, app):
        self.app = app
        self.T = app.T
        self.store = PersonalStore()
        self.window = tk.Toplevel(app.root)
        self.window.title(self.T('personal_title'))
        self.window.geometry('1100x'+str(min(900,self.window.winfo_screenheight()-100))); self.window.minsize(850, 620)
        self.window.transient(app.root)
        self.edit_key = None
        self.lookup_generation = 0
        self.lookup_events = queue.Queue()
        self.poll_after = None
        self.window.bind('<Destroy>',self.destroyed,add='+')
        self.rows = {}
        self.fields = {key: tk.StringVar() for key in ('source','target','scope','term','translation','context','url')}
        self.scopes = {self.T('scope_'+key): key for key in ('engineering','conversation','both')}
        self.filter = tk.StringVar()
        self.status = tk.StringVar(value=self.T('personal_pick'))
        viewport=ttk.Frame(self.window); viewport.pack(fill='both',expand=True)
        canvas=tk.Canvas(viewport,highlightthickness=0,bg='#f0f4f7')
        page_scroll=ttk.Scrollbar(viewport,orient='vertical',command=canvas.yview)
        page_scroll.pack(side='right',fill='y'); canvas.pack(side='left',fill='both',expand=True)
        canvas.configure(yscrollcommand=page_scroll.set)
        panel = ttk.Frame(canvas, padding=14)
        body=canvas.create_window((0,0),window=panel,anchor='nw')
        panel.bind('<Configure>',lambda event:canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>',lambda event:canvas.itemconfigure(body,width=event.width))
        ttk.Label(panel, text=self.T('personal_help'), wraplength=1030).pack(fill='x', pady=(0,8))
        search = ttk.Frame(panel); search.pack(fill='x')
        ttk.Label(search,text=self.T('search')).pack(side='left')
        ttk.Entry(search,textvariable=self.filter).pack(side='left', fill='x',expand=True,padx=8)
        self.count=ttk.Label(search); self.count.pack(side='right')
        grid=ttk.Frame(panel); grid.pack(fill='both', expand=True,pady=6)
        self.table=ttk.Treeview(grid,columns=('source','target','term','translation','scope'),show='headings',height=6,selectmode='browse')
        for key,label,width in [('source','personal_from',100),('target','personal_to',100),('term','source_term',270),('translation','personal_translation',270),('scope','personal_scope',180)]:
            self.table.heading(key,text=self.T(label)); self.table.column(key,width=width,minwidth=60)
        scroll=ttk.Scrollbar(grid,command=self.table.yview); self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y'); self.table.pack(fill='both',expand=True)
        self.table.bind('<<TreeviewSelect>>',self.select)
        form=ttk.Frame(panel); form.pack(fill='x')
        for column in range(3): form.columnconfigure(column,weight=1)
        for col,key,label in [(0,'source','source_language'),(1,'target','output_language'),(2,'scope','personal_scope')]:
            ttk.Label(form,text=self.T(label)).grid(row=0,column=col,sticky='w')
            ttk.Combobox(form,textvariable=self.fields[key],values=list(self.scopes) if key=='scope' else list(LANGUAGE_NAMES.values()),state='readonly').grid(row=1,column=col,sticky='ew',padx=(0,8),pady=(0,5))
        for row,key,label in [(2,'term','source_term'),(4,'translation','personal_translation'),(6,'context','personal_context'),(8,'url','personal_url')]:
            ttk.Label(form,text=self.T(label)).grid(row=row,column=0,sticky='w',columnspan=3)
            ttk.Entry(form,textvariable=self.fields[key]).grid(row=row+1,column=0,columnspan=3,sticky='ew',pady=(0,4))
        actions=ttk.Frame(panel); actions.pack(fill='x',pady=4)
        self.buttons={}
        for index,(key,command) in enumerate([('personal_new',self.new),('personal_save',self.save),('personal_delete',self.delete),('personal_export',self.export),('personal_import',self.import_backup)]):
            actions.columnconfigure(index%3,weight=1)
            button=ttk.Button(actions,text=self.T(key),command=command,padding=5); button.grid(row=index//3,column=index%3,sticky='ew',padx=(0,5),pady=3); self.buttons[key]=button
        actions=ttk.Frame(panel); actions.pack(fill='x',pady=4)
        for index,(key,command) in enumerate([('personal_selected',self.use_input),('personal_pdf',self.from_pdf),('personal_lookup',self.find_online),('personal_search_web',self.search_web)]):
            actions.columnconfigure(index%2,weight=1)
            button=ttk.Button(actions,text=self.T(key),command=command,padding=5); button.grid(row=index//2,column=index%2,sticky='ew',padx=(0,5),pady=3); self.buttons[key]=button
        ttk.Label(panel,text=self.T('personal_online_help'),wraplength=1030,font=('Segoe UI',9)).pack(fill='x',pady=5)
        ttk.Label(panel,text=self.T('personal_candidates'),font=('Segoe UI',9)).pack(anchor='w')
        self.candidates=tk.Listbox(panel,height=3,exportselection=False,font=('Segoe UI',10))
        self.candidates.pack(fill='x'); self.candidates.bind('<<ListboxSelect>>',self.choose_candidate)
        ttk.Label(panel,textvariable=self.status,wraplength=1030).pack(fill='x',pady=(5,0))
        self.filter.trace_add('write',self.refresh)
        for key in ('source','target','term'):
            self.fields[key].trace_add('write',self.invalidate_lookup)
        self.new()
        self.refresh()
        self.poll_after=self.window.after(100,self.poll)

    def error(self, exc):
        messagebox.showerror(self.T('personal_title'),self.T('personal_error')+'\n\n'+str(exc),parent=self.window)

    def code(self, field):
        return next(k for k,v in LANGUAGE_NAMES.items() if v==self.fields[field].get())

    def scope_name(self, code):
        return next(k for k,v in self.scopes.items() if v==code)

    def new(self):
        self.edit_key=None
        for value in self.fields.values(): value.set('')
        source=self.app.source_code if self.app.source_code!='auto' else 'nl'
        target=self.app.target_code()
        if target==source: target='fr' if source=='en' else 'en'
        self.fields['source'].set(LANGUAGE_NAMES[source]); self.fields['target'].set(LANGUAGE_NAMES[target])
        self.fields['scope'].set(self.scope_name('both'))
        self.table.selection_remove(*self.table.selection())
        self.status.set(self.T('personal_pick'))

    def refresh(self,*args):
        try: rows=self.store.read()
        except Exception as exc:
            self.status.set(self.T('personal_error')+' '+str(exc)); return
        query=normalized(self.filter.get())
        self.table.delete(*self.table.get_children()); self.rows.clear()
        for row in sorted(rows,key=lambda r:(r['source'],r['target'],normalized(r['term']))):
            if query and query not in normalized(' '.join(row.values())): continue
            item=self.table.insert('','end',values=(LANGUAGE_NAMES[row['source']],LANGUAGE_NAMES[row['target']],row['term'],row['translation'],self.scope_name(row['scope'])))
            self.rows[item]=row
        self.count.configure(text=self.T('personal_count',count=len(self.rows)))

    def select(self,*args):
        chosen=self.table.selection()
        if not chosen or chosen[0] not in self.rows: return
        row=self.rows[chosen[0]]; self.edit_key=entry_key(row)
        for key,value in row.items():
            self.fields[key].set(LANGUAGE_NAMES[value] if key in ('source','target') else self.scope_name(value) if key=='scope' else value)

    def save(self):
        try:
            row={key:value.get() for key,value in self.fields.items()}
            row.update(source=self.code('source'),target=self.code('target'),scope=self.scopes[row['scope']])
            key=entry_key(row)
            if key!=self.edit_key and any(entry_key(r)==key for r in self.store.read()):
                if not messagebox.askyesno(self.T('personal_title'),self.T('personal_replace_question'),parent=self.window): return
            self.store.upsert(row,self.edit_key)
            self.edit_key=key
            self.refresh(); self.app.invalidate_text()
            self.status.set(self.T('personal_saved'))
        except Exception as exc: self.error(exc)

    def delete(self):
        if self.edit_key is None: return
        if not messagebox.askyesno(self.T('personal_title'),self.T('personal_delete_question'),parent=self.window): return
        try:
            self.store.delete(self.edit_key); self.new(); self.refresh(); self.app.invalidate_text()
            self.status.set(self.T('personal_deleted'))
        except Exception as exc: self.error(exc)

    def export(self):
        path=filedialog.asksaveasfilename(parent=self.window,title=self.T('personal_export'),initialfile='Eizat-personal-glossary-backup.json',defaultextension='.json',filetypes=[('JSON','*.json')])
        if not path: return
        try: self.store.export(path); self.status.set(self.T('personal_exported'))
        except Exception as exc: self.error(exc)

    def import_backup(self):
        path=filedialog.askopenfilename(parent=self.window,title=self.T('personal_import'),filetypes=[('JSON','*.json')])
        if not path: return
        try:
            try:
                self.store.read()
            except ValueError:
                if not messagebox.askyesno(self.T('personal_title'),self.T('personal_restore_question'),parent=self.window): return
                count=self.store.restore_backup(path)
            else:
                count=self.store.import_backup(path)
            self.new(); self.refresh(); self.app.invalidate_text()
            self.status.set(self.T('personal_imported',count=count))
        except Exception as exc: self.error(exc)

    def use_input(self):
        try:
            value=self.app.text_input.get('sel.first','sel.last').strip()
            if not value or len(value)>500: raise ValueError(self.T('personal_no_selection'))
            self.fields['term'].set(value)
        except (tk.TclError,ValueError): self.status.set(self.T('personal_no_selection'))

    def from_pdf(self):
        path=filedialog.askopenfilename(parent=self.window,title=self.T('personal_pdf'),filetypes=[('PDF','*.pdf')])
        if not path: return
        try:
            import fitz
            content=[]; length=0
            with fitz.open(path) as pdf:
                for page in list(range(min(100,len(pdf)))):
                    value=pdf[page].get_text()[:500000-length]
                    content.append(value); length+=len(value)
                    if length>=500000: break
            if not ''.join(content).strip(): raise ValueError(self.T('error_no_text'))
            viewer=tk.Toplevel(self.window); viewer.title(Path(path).name); viewer.geometry('850x650')
            ttk.Label(viewer,text=self.T('personal_pdf_help'),wraplength=810).pack(fill='x',padx=12,pady=8)
            area=ScrolledText(viewer,wrap='word',font=('Segoe UI',11)); area.pack(fill='both',expand=True,padx=12)
            area.insert('1.0','\n'.join(content)); area.configure(state='disabled')
            ttk.Label(viewer,text=self.T('personal_pdf_limit')).pack(pady=4)
            def use():
                try: value=area.get('sel.first','sel.last').strip()
                except tk.TclError: value=''
                if not value or len(value)>500:
                    messagebox.showinfo(self.T('personal_title'),self.T('personal_no_selection'),parent=viewer); return
                self.fields['term'].set(value); viewer.destroy()
            ttk.Button(viewer,text=self.T('personal_use_selection'),command=use).pack(pady=8)
        except Exception as exc: self.error(exc)

    def invalidate_lookup(self,*args):
        self.lookup_generation+=1
        self.candidates.delete(0,'end')
        self.buttons['personal_lookup'].configure(state='normal')

    def find_online(self):
        try:
            term=self.fields['term'].get().strip(); source=self.code('source'); target=self.code('target')
            if not term or len(term.encode('utf-8'))>500 or source==target: raise ValueError(self.T('personal_no_selection'))
        except Exception as exc: self.error(exc); return
        self.invalidate_lookup(); generation=self.lookup_generation
        self.status.set(self.T('personal_lookup_working')); self.buttons['personal_lookup'].configure(state='disabled')
        def worker():
            try: result,error=lookup(term,source,target),None
            except Exception as exc: result,error=None,str(exc)
            self.lookup_events.put((generation,result,error))
        threading.Thread(target=worker,daemon=True).start()

    def destroyed(self,event):
        if event.widget!=self.window: return
        self.lookup_generation+=1
        if self.poll_after is not None:
            self.window.after_cancel(self.poll_after); self.poll_after=None

    def poll(self):
        if self.poll_after is not None:
            self.window.after_cancel(self.poll_after); self.poll_after=None
        if not self.window.winfo_exists(): return
        try:
            while True:
                generation,result,error=self.lookup_events.get_nowait()
                if generation!=self.lookup_generation: continue
                self.buttons['personal_lookup'].configure(state='normal')
                if error: self.status.set(self.T('personal_error')+' '+error)
                else:
                    for value in result: self.candidates.insert('end',value)
                    self.status.set(self.T('personal_lookup_ready'))
        except queue.Empty: pass
        self.poll_after=self.window.after(100,self.poll)

    def choose_candidate(self,*args):
        selected=self.candidates.curselection()
        if selected:
            self.fields['translation'].set(self.candidates.get(selected[0]))
            self.fields['url'].set(PROVIDER)

    def search_web(self):
        try:
            url=search_url(self.fields['term'].get(),self.code('source'),self.code('target'),self.fields['context'].get())
            webbrowser.open(url)
        except Exception as exc: self.error(exc)
