from _thread import start_new_thread
from ctypes import windll
from json import dumps, loads
from os import execl, listdir, system
from os.path import join, splitext
from random import choice, choices, shuffle
from sys import executable, exit
from tkinter import (BOTH, END, INSERT, Canvas, IntVar, Menu, StringVar, Tk,
                     Toplevel, Variable, X)
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText
from tkinter.simpledialog import askinteger
from tkinter.ttk import Button, Frame, Notebook, Progressbar

from heartrate import trace
from PIL import Image, ImageTk
from pyttsx4 import Engine

__version__ = "*Spinner 1.1+24w01a"
tk = Tk()
eng = Engine()

class EditWindow(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.title("Spinner")
        self.transient(top)
        self.place_widgets()
        self.geometry(f"+{top.winfo_x()}+{top.winfo_y()}")
    
    def place_widgets(self):
        nb = Notebook(self)
        for txt, dat, fn in [["系统设置", SYSCNF, "syscnf.json"], ["贴图设置", COMBINES, "combines.json"], ["数字数据", NUMDAT, "numdat.json"], ["姓名学号", NAMEDICT, "namedict.json"], ["系统工具", TOOLS, "tools.json"]]:
            f = Frame(self)
            st = ScrolledText(f)
            st.insert(INSERT, repr(dat).replace(",", ",\n "))
            st.pack(fill=BOTH, expand=1, **PAD)
            Button(f, text="保存（一定要保存！！！）", command=lambda fn=fn, st=st:self.save(fn, st)).pack(fill=X, **PAD)
            nb.add(f, text=txt)
        nb.pack(fill=BOTH, expand=1, **PAD)
    
    def save(self, fn, st: ScrolledText):
        cont = st.get("0.0", END).replace("\n", "").strip()
        dat = dumps(eval(cont))
        with open(join("config", fn), "w") as f:
            f.write(dat)

def loadjson(fn: str) -> dict:
    with open(join("config", f"{fn}.json")) as f:
        return loads(f.read())

SYSCNF = loadjson("syscnf")
NUMDAT = loadjson("numdat")
COMBINES = loadjson("combines")
NAMEDICT = loadjson("namedict")
TOOLS = loadjson("tools")

SCALE = SYSCNF["scale"]
MEMBERS = list(range(SYSCNF["min"], SYSCNF["max"] + 1))
MEMBERS.extend(SYSCNF["blackNames"] * SYSCNF["blackWeight"])
shuffle(MEMBERS)
for x in SYSCNF["whiteNames"]:
    MEMBERS.remove(x)
PAD = SYSCNF["pad"]
W, H = int(256 * SCALE), int(208 * SCALE)
SW, SH = tk.winfo_screenwidth(), tk.winfo_screenheight()
ALPHA = SYSCNF["alpha"]
eng.setProperty("volume", 1.0)

IMGS = {}
files = listdir("assets")
pbv = IntVar()
Progressbar(tk, maximum=len(files), variable=pbv).pack(fill=BOTH)
tk.geometry(f"300x64+{int(SW/2 - 300)}+{int(SH/2 - 64)}")
for ind, fn in enumerate(files):
    if fn.endswith(".png"):
        IMGS[splitext(fn)[0]] = ImageTk.PhotoImage(Image.open(join("assets", fn)).crop((0, 0, 16, 16)).resize((int(16 * SCALE), int(16 * SCALE))))
        tk.update()
        print("load",fn)
    pbv.set(pbv.get() + 1)

tk.geometry("+10000+10000")
#tk.overrideredirect(1)
top = Toplevel(tk)
top.title(__version__)
top.transient(tk)
cvs = Canvas(top, highlightthickness=0)
cvs.place(relx=0, rely=0, relwidth=1, relheight=1)

now_geo = StringVar()
old_geo = StringVar()
nextone = IntVar(value=-1)

def read(msg):
    start_new_thread(_read, (msg, ))

def _read(msg):
    try:
        eng.endLoop()
    except Exception:pass
    eng.say(msg)
    eng.runAndWait()

def set_top_geometry(geo, hidding=False):
    old_geo.set(now_geo.get()) if not hidding else old_geo.set("hidden")
    now_geo.set(geo)
    top.geometry(geo)

set_top_geometry(f"{W}x{H}+{int(SW/2 - W/2)}+{int(SH/2 - H/2)}")

current = StringVar(value=SYSCNF["defaultTexture"])
define = Variable()

def getimgs():
    if current.get() != "__define__":
        on, off = COMBINES[current.get()]
    else:
        on, off = define.get()
    return IMGS[on], IMGS[off]

def randtexture(*e):
    define.set(choices(list(IMGS.keys()), k=2))
    init()

def winclose():
    if now_geo.get() == "hidden": #hidden
        set_top_geometry(old_geo.get())
        top.attributes("-alpha", 1)

    else:
        set_top_geometry(f"{W}x{H}-{SW-30}+{top.winfo_y()}")
        now_geo.set("hidden")
        top.attributes("-alpha", ALPHA)

top.protocol("WM_DELETE_WINDOW", winclose)

def shownum(x: int):
    a, b = ("0" + str(x))[-2:]
    on, off = getimgs()
    left = NUMDAT[a]
    right = NUMDAT[b]

    for id in range(0, 45):
        if id in left:
            cvs.itemconfig(f"l{id}", image=on)
        else:
            cvs.itemconfig(f"l{id}", image=off)
        
        if id in right:
            cvs.itemconfig(f"r{id}", image=on)
        else:
            cvs.itemconfig(f"r{id}", image=off)
    cvs.update()
    cvs.update_idletasks()

def init():
    cvs.delete("all")
    on, off = getimgs()
    for y in range(0, 13):
        for x in range(0, 16):
            cvs.create_image(x * 16 * SCALE, y * 16 * SCALE, image=off, anchor="nw", tag=f"{x},{y}")
    id_x = 0
    id_y = 0
    for y in range(2, 11):
        for x in range(2, 7):
            cvs.delete(f"{x},{y}")
            cvs.create_image(x * 16 * SCALE, y * 16 * SCALE, image=on, anchor="nw", tag=f"l{id_x}")
            id_x += 1
        for x in range(9, 14):
            cvs.delete(f"{x},{y}")
            cvs.create_image(x * 16 * SCALE, y * 16 * SCALE, image=on, anchor="nw", tag=f"r{id_y}")
            id_y += 1
    cvs.update()

def update(event):
    for t in range(SYSCNF["repeatTimes"]):
        shownum(choice(MEMBERS))
    n = nextone.get()
    print(n)
    if n != -1:
        shownum(n)
        read(SYSCNF["voicePrompt"].format(num=n, name=NAMEDICT.get(str(n), "")))
        nextone.set(-1)
    else:
        x = choice(MEMBERS)
        shownum(x)
        read(SYSCNF["voicePrompt"].format(num=x, name=NAMEDICT.get(str(x), "")))

def focus():
    top.after(1000, focus)
    #top.focus_set()
    if now_geo.get() != "hidden":
        windll.user32.SetForegroundWindow(top.winfo_id())
    else:
        top.focus_set()

def see_trace():
    trace(browser=True)

def start_tool(t):
    start_new_thread(system, (t,))

menubar = Menu(top)
comb = Menu(menubar, tearoff=0)
for k in COMBINES.keys():
    comb.add_radiobutton(label=k, value=k, command=init, variable=current)
comb.add_separator()
comb.add_radiobutton(label="从素材库中随机...", value="__define__", command=randtexture, variable=current)
menubar.add_cascade(label="贴图", menu=comb)

def add_trick_items(menu: Menu, labl, content:list):
    subm = Menu(menu, tearoff=0)
    for c in content:
        subm.add_command(label=str(c), command=lambda who=c:nextone.set(who))
    menu.add_cascade(label=labl, menu=subm)

def restart():
    execl(executable, executable)#abspath(SYSCNF["restarter"]), abspath(SYSCNF["restarter"])
    system()
    exit()

def show_log():
    """==Spinner 1.1+24w01a 更新==
    1. 增加了更新日志
    2. 修复了长贴图读取bug和进度条走不到终点bug
    3. 新增恶搞功能和相关禁用项
    4. 新增系统工具栏
    5. 现在窗口隐藏到左侧时为半透明
    6. 新增后台监视器（程序打包后变得不可用）
    7. 将不断使窗口获得焦点（Toplevel.focus_set）改为不断将窗口调到前台（User32.dll -> SetForegroundWindow），降低死机率
    8. 贴图组合实现汉化
    9. 内置了配置文件编辑器"""
    showinfo("Spinner", show_log.__doc__, parent=top)

tric = Menu(menubar, tearoff=0)
subs = {}
mems = sorted(list(set(MEMBERS)))
for x in range(0, max(mems), 10):
    subs[f"{x}-{x+10}"] = sorted([m for m in mems if m<=x+10 and m >=x])
for labl, content in subs.items():
    if content:
        add_trick_items(tric, labl, content)
tric.add_separator()
tric.add_command(label="获取输入...", command=lambda: nextone.set(askinteger("Spinner", "输入一个正整数", parent=top)))

if SYSCNF["doTricks"]:
    menubar.add_cascade(label=f"恶搞", menu=tric)
else:
    menubar.add_cascade(label=f"恶搞（已禁用）", menu=Menu(menubar, tearoff=0))

edit = Menu(menubar, tearoff=0)
edit.add_command(label="打开编辑器", command=EditWindow)
edit.add_command(label="重新启动", command=restart)
edit.add_command(label="后台监视器", command=see_trace)
menubar.add_cascade(label="配置", menu=edit)

too = Menu(menubar, tearoff=0)
for k, v in TOOLS.items():
    too.add_command(label=k, command=lambda v=v: start_tool(v))
too.add_separator()
too.add_command(label="更新日志", command=show_log)
menubar.add_cascade(label="工具", menu=too)

top.config(menu=menubar)

init()
cvs.bind("<1>", update)
top.after(0, focus)
top.attributes("-topmost", 1)
top.resizable(0, 0)
windll.user32.SetFocus(top.winfo_id())
tk.wait_window(top)
