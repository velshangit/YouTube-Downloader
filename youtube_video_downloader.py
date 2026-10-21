import os, re, sys, threading, queue, tkinter as tk
from tkinter import ttk, filedialog, messagebox
try:
    import yt_dlp
except ImportError:
    yt_dlp = None

APP_TITLE = "Youtube Video Downloader"

def resource_path(filename):
    """Find bundled resources in both Python and PyInstaller builds."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)
BG, PANEL, PANEL2 = "#0b1220", "#111c2f", "#17243a"
TEXT, MUTED, ACCENT = "#eef4ff", "#9aacc7", "#5b8cff"

class App:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        try:
            root.iconbitmap(resource_path("logo.ico"))
        except (tk.TclError, OSError):
            pass
        root.geometry("820x660"); root.minsize(700, 590); root.configure(bg=BG)
        self.folder = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Videos", "Downloaded Videos"))
        self.quality = tk.StringVar(value="Best available")
        self.status = tk.StringVar(value="Ready — paste one or more video links below.")
        self.events = queue.Queue(); self.busy = False
        self.styles()
        self.ui()
        root.after(120, self.poll)

    def styles(self):
        s = ttk.Style()
        try: s.theme_use("clam")
        except tk.TclError: pass
        s.configure("TCombobox", padding=7, fieldbackground=PANEL2, background=PANEL2, foreground=TEXT, arrowcolor=TEXT)
        s.map("TCombobox", fieldbackground=[("readonly", PANEL2)], foreground=[("readonly", TEXT)])
        s.configure("Horizontal.TProgressbar", troughcolor=PANEL2, background=ACCENT, bordercolor=PANEL2)

    def label(self, parent, text, size=10, color=TEXT, bold=False):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color, font=("Segoe UI", size, "bold" if bold else "normal"))

    def btn(self, parent, text, command, primary=False):
        return tk.Button(parent, text=text, command=command, bg=ACCENT if primary else PANEL2, fg=TEXT,
            activebackground="#4678e8" if primary else "#22334e", activeforeground=TEXT, relief="flat", bd=0,
            padx=15, pady=10, font=("Segoe UI", 10, "bold" if primary else "normal"), cursor="hand2")

    def ui(self):
        outer = tk.Frame(self.root, bg=BG); outer.pack(fill="both", expand=True, padx=24, pady=20)
        head = tk.Frame(outer, bg=BG); head.pack(fill="x", pady=(0, 17))
        titles = tk.Frame(head, bg=BG); titles.pack(side="left", fill="x", expand=True)
        self.label(titles, APP_TITLE, 21, TEXT, True).pack(anchor="w")
        self.label(titles, "Batch downloads  •  Local storage  •  Simple and fast", 10, MUTED).pack(anchor="w", pady=(4,0))
        tk.Label(head, text="WINDOWS APP", bg=PANEL2, fg="#bcd0ff", font=("Segoe UI",8,"bold"), padx=10,pady=7).pack(side="right")
        card = tk.Frame(outer, bg=PANEL, highlightbackground="#243550", highlightthickness=1); card.pack(fill="both",expand=True)
        c = tk.Frame(card,bg=PANEL); c.pack(fill="both",expand=True,padx=20,pady=18)
        self.label(c,"Video links",12,TEXT,True).pack(anchor="w")
        self.label(c,"Paste one URL or multiple YouTube URLs separated by commas, spaces, or new lines.",9,MUTED).pack(anchor="w",pady=(5,9))
        self.links = tk.Text(c,height=5,wrap="word",bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",font=("Segoe UI",10),padx=12,pady=10,highlightthickness=1,highlightbackground="#2a3c59",highlightcolor=ACCENT)
        self.links.pack(fill="x")
        row = tk.Frame(c,bg=PANEL); row.pack(fill="x",pady=(16,0))
        left=tk.Frame(row,bg=PANEL); left.pack(side="left",fill="x",expand=True)
        self.label(left,"Video quality",10,TEXT,True).pack(anchor="w",pady=(0,6))
        ttk.Combobox(left,textvariable=self.quality,state="readonly",width=22,values=("Best available","1080p max","720p max","480p max","360p max","Audio/video combined format")).pack(anchor="w")
        right=tk.Frame(row,bg=PANEL); right.pack(side="right",fill="x",expand=True,padx=(18,0))
        self.label(right,"Save to",10,TEXT,True).pack(anchor="w",pady=(0,6))
        fr=tk.Frame(right,bg=PANEL); fr.pack(fill="x")
        tk.Entry(fr,textvariable=self.folder,state="readonly",bg=PANEL2,fg=TEXT,readonlybackground=PANEL2,relief="flat",font=("Segoe UI",9)).pack(side="left",fill="x",expand=True,ipady=10,padx=(0,8))
        self.btn(fr,"Browse",self.choose).pack(side="right")
        self.progress=ttk.Progressbar(c,mode="determinate",maximum=100); self.progress.pack(fill="x",pady=(20,8))
        tk.Label(c,textvariable=self.status,bg=PANEL,fg=MUTED,font=("Segoe UI",9),anchor="w",justify="left",wraplength=720).pack(fill="x")
        actions=tk.Frame(c,bg=PANEL); actions.pack(fill="x",pady=(15,0))
        self.download=self.btn(actions,"↓   Download videos",self.start,True); self.download.pack(side="left")
        self.btn(actions,"Open folder",self.open_folder).pack(side="left",padx=(8,0))
        self.btn(actions,"Clear links",self.clear).pack(side="right")
        self.label(c,"DOWNLOAD QUEUE",9,MUTED,True).pack(anchor="w",pady=(18,6))
        self.queue=tk.Listbox(c,height=5,bg=PANEL2,fg=TEXT,selectbackground=ACCENT,relief="flat",bd=0,font=("Segoe UI",9),activestyle="none",highlightthickness=1,highlightbackground="#2a3c59")
        self.queue.pack(fill="both",expand=True)
        self.label(outer,"Only download content you own or are authorized to save. Follow the website's terms.",9,MUTED).pack(anchor="w",pady=(10,0))

    def parse(self):
        raw=self.links.get("1.0","end").strip()
        result=[]
        for u in re.split(r"[\s,;]+",raw):
            u=u.strip().strip("<>()[]{}'\"")
            if u.startswith(("https://","http://")) and u not in result: result.append(u)
        return result

    def choose(self):
        p=filedialog.askdirectory(title="Choose download folder")
        if p: self.folder.set(p)

    def open_folder(self):
        p=self.folder.get().strip(); os.makedirs(p,exist_ok=True)
        try: os.startfile(p)
        except Exception as e: messagebox.showerror("Could not open folder",str(e))

    def clear(self):
        if not self.busy: self.links.delete("1.0","end"); self.queue.delete(0,"end"); self.status.set("Links cleared.")

    def selector(self):
        q=self.quality.get()
        heights={"1080p max":1080,"720p max":720,"480p max":480,"360p max":360}
        if q in heights:
            h=heights[q]; return f"bestvideo[height<={h}]+bestaudio/best[height<={h}]/best"
        return "best" if q=="Audio/video combined format" else "bestvideo*+bestaudio/best"

    def start(self):
        if self.busy:return
        if yt_dlp is None: messagebox.showerror("Missing dependency","Run install_dependencies.bat first."); return
        urls=self.parse()
        if not urls: messagebox.showwarning("No valid links","Paste one or more complete http(s) video URLs."); return
        folder=self.folder.get().strip()
        if not folder: messagebox.showwarning("Choose a folder","Select a save folder first."); return
        os.makedirs(folder,exist_ok=True); self.queue.delete(0,"end")
        for u in urls:self.queue.insert("end","Queued  •  "+u)
        self.busy=True; self.download.configure(state="disabled",text="Downloading…"); self.progress.configure(value=0)
        self.status.set(f"Starting {len(urls)} download(s)…")
        threading.Thread(target=self.worker,args=(urls,folder,self.quality.get()),daemon=True).start()

    def worker(self,urls,folder,quality):
        total=len(urls); ok=0; failed=[]
        heights={"1080p max":1080,"720p max":720,"480p max":480,"360p max":360}
        fmt="best"
        if quality in heights:
            h=heights[quality]; fmt=f"bestvideo[height<={h}]+bestaudio/best[height<={h}]/best"
        elif quality=="Best available": fmt="bestvideo*+bestaudio/best"
        for i,url in enumerate(urls):
            def hook(d,idx=i):
                if d.get("status")=="downloading":
                    totalbytes=d.get("total_bytes") or d.get("total_bytes_estimate"); done=d.get("downloaded_bytes",0)
                    pct=done/totalbytes*100 if totalbytes else 0
                    self.events.put(("progress",(idx+pct/100)/total*100,f"Video {idx+1}/{total} • {pct:.1f}% • {d.get('_speed_str','')} • ETA {d.get('_eta_str','')}"))
                elif d.get("status")=="finished": self.events.put(("progress",(idx+1)/total*100,f"Processing video {idx+1}/{total}…"))
            self.events.put(("item",i,"Downloading  •  "+url))
            opts={"format":fmt,"merge_output_format":"mp4","outtmpl":os.path.join(folder,"%(title).180B [%(id)s].%(ext)s"),"noplaylist":True,"progress_hooks":[hook],"windowsfilenames":True,"retries":3,"quiet":True}
            try:
                with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
                ok+=1; self.events.put(("item",i,"Completed  •  "+url))
            except Exception as e:
                failed.append((url,str(e))); self.events.put(("item",i,"FAILED  •  "+url))
        self.events.put(("done",ok,total,failed,folder))

    def poll(self):
        try:
            while True:
                e=self.events.get_nowait()
                if e[0]=="progress": self.progress.configure(value=e[1]); self.status.set(e[2])
                elif e[0]=="item":
                    idx,msg=e[1],e[2]
                    if idx<self.queue.size(): self.queue.delete(idx); self.queue.insert(idx,msg)
                elif e[0]=="done":
                    ok,total,failed,folder=e[1:]; self.busy=False; self.download.configure(state="normal",text="↓   Download videos")
                    self.progress.configure(value=100 if ok==total else ok/total*100)
                    if failed:
                        self.status.set(f"Finished: {ok}/{total} successful; {len(failed)} failed. Saved in {folder}")
                        messagebox.showwarning("Finished with errors",f"Successful: {ok}/{total}\\nFailed: {len(failed)}\\n\\n"+ "\\n\\n".join(f"{u}\\n{err}" for u,err in failed[:4]))
                    else:
                        self.status.set(f"All {total} video(s) downloaded. Saved in: {folder}")
                        messagebox.showinfo("Downloads complete",f"Downloaded {total} video(s).\\n\\nSaved to:\\n{folder}")
        except queue.Empty: pass
        self.root.after(120,self.poll)

if __name__=="__main__":
    root=tk.Tk(); App(root); root.mainloop()
