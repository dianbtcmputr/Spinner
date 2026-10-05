from _thread import start_new_thread
from ctypes import windll
from io import BytesIO
from os import execl, system
from os.path import splitext
from random import choice, choices, shuffle
from sys import executable
from time import sleep
from tkinter import (BOTH, END, LEFT, NW, X, BooleanVar, Canvas, IntVar, Label, Menu, StringVar,
                     Tk, Toplevel, Variable)
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText
from tkinter.simpledialog import askinteger
from tkinter.ttk import Button, Entry, Frame

from aglib import AgDir, LoadAgFileName, SaveAgFileName
from PIL import Image, ImageTk
from pyttsx4 import Engine

VERSION = "Spinner 1.2+24w02a"
tk = Tk()
tk.title(VERSION)
eng = Engine()

class EditWindow(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.title("Spinner")
        self.transient(top)
        self.txt = ScrolledText(self, font=EDITORFONT)
        self.txt.pack(fill=BOTH, expand=1, **PAD)
        self.cmdf = Frame(self)
        self.ety = Entry(self.cmdf, font=EDITORFONT)
        self.ety.bind("<Return>", lambda _:self.go())
        self.ety.pack(side=LEFT, fill=X, **PAD)
        Button(self.cmdf, text="Go", command=self.go).pack(side=LEFT, **PAD)
        Button(self.cmdf, text="保存", command=self.save).pack(side=LEFT, **PAD)
        self.cmdf.pack(fill=X)
        self.geometry(f"{EDITORW}x{EDITORH}+{top.winfo_x()}+{top.winfo_y()}")
    def save(self):
        SaveAgFileName(cnflib, "config2.aglib")
    
    def go(self):
        cmd = self.ety.get()
        self.ety.delete(0, END)
        try:
            res = repr(eval(cmd))
        except Exception as e:
            res = f"{type(e).__name__}: {str(e)}"
        self.txt.insert(END, f">>> {cmd}\n{res}\n")

def prettydat(dat: dict) -> str:
    res = []
    for k, v in dat.items():
        res.append(f"{repr(k)}: {repr(v)}")
    return "{ " + (",\n  ".join(res)) + "}"

cnflib = LoadAgFileName("config.aglib")
assetslib = LoadAgFileName("assets.aglib")
texlib = assetslib.GetSubDirCopy("textures")
iconlib = assetslib.GetSubDirCopy("icons")

def loadpimg(lib: AgDir, name, size: int):
    return ImageTk.PhotoImage(Image.open(BytesIO(lib.QueryValue(name))).crop((0, 0, 16, 16)).resize((size, size)))

SYSCNF = cnflib.GetSubDirCopy("HKEY_SYSTEM")
NUMDAT = cnflib.GetSubDirCopy("HKEY_NUM_DATA")
COMBINES = cnflib.GetSubDirCopy("HKEY_COMBINES")
NAMEDICT = cnflib.GetSubDirCopy("HKEY_NAMES")
TOOLS = cnflib.GetSubDirCopy("HKEY_TOOLS")
VOICETIP = cnflib.GetSubDirCopy("HKEY_VOICE_TIP")

SCALE = SYSCNF.QueryValue("scale")
MEMBERS = list(range(SYSCNF.QueryValue("min"), SYSCNF.QueryValue("max") + 1))
MEMBERS.extend(SYSCNF.QueryValue("blackNames") * SYSCNF.QueryValue("blackWeight"))

for x in SYSCNF.QueryValue("whiteNames"):
    MEMBERS.remove(x)
for x in range(10):
    shuffle(MEMBERS)

PAD = SYSCNF.QueryValue("pad")
W, H = int(256 * SCALE), int(208 * SCALE)
SW, SH = tk.winfo_screenwidth(), tk.winfo_screenheight()
REPEATTIMES = SYSCNF.QueryValue("repeatTimes")
ALPHA = SYSCNF.QueryValue("alpha")
DEFAULTTEXTURE = SYSCNF.QueryValue("defaultTexture")
EDITORFONT = SYSCNF.QueryValue("editorFont")
DELTAY = SYSCNF.QueryValue("deltaY")
VOICEPROMPT = SYSCNF.QueryValue("voicePrompt")
DOTRICKS = SYSCNF.QueryValue("doTricks")
EDITORW, EDITORH = SYSCNF.QueryValue("editorWH")
VOICETIPMARK = SYSCNF.QueryValue("voiceTipMark")
LOADWINSIZE = SYSCNF.QueryValue("loadWinSize")

eng.setProperty("volume", SYSCNF.QueryValue("aiVolume"))
eng.setProperty("rate", SYSCNF.QueryValue("aiRate"))
IMGS = {}

files = texlib.EnumFiles()
fcount = len(files)
tk.geometry(f"{LOADWINSIZE}x{LOADWINSIZE}+{int(SW/2 - LOADWINSIZE/2)}+{int(SH/2 - LOADWINSIZE/2)}")
tk.overrideredirect(1)
c = Canvas(tk, highlightthickness=0)
c.place(x=0, y=0, relwidth=1, relheight=1)
rd, rdo = loadpimg(iconlib, "redstone_lamp.png", LOADWINSIZE), loadpimg(iconlib, "redstone_lamp_on.png", LOADWINSIZE)
c.create_image(0, 0, image=rd, anchor=NW)
l = Label(tk, anchor=NW, image=rdo, width=0, highlightthickness=0)
w = c.create_window(-2, -2, anchor=NW, window=l)
for ind, fn in enumerate(files):
    if fn.endswith(".png"):
        IMGS[splitext(fn)[0]] = loadpimg(texlib, fn, int(16*SCALE))
        tk.update()
    l.config(width=ind/fcount*150)
for x in range(100):
    tk.attributes("-alpha", tk.attributes("-alpha") - 0.01)
    tk.update()
    sleep(0.005)

tk.geometry("+10000+10000")
tk.overrideredirect(1)
del c, l, w
top = Toplevel(tk)
top.title(VERSION)
top.transient(tk)
top.iconphoto(1, rd)
cvs = Canvas(top, highlightthickness=0)
cvs.place(relx=0, rely=0, relwidth=1, relheight=1)

now_geo = StringVar()
old_geo = StringVar()
nextone = IntVar(value=-1)

def read(msg):
    start_new_thread(_read, (msg,))

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

set_top_geometry(f"{W}x{H}+{int(SW/2 - W/2)}+{int(SH/2 - H/2)+DELTAY}")
top.attributes("-alpha", 0)

current = StringVar(value=DEFAULTTEXTURE)
define = Variable()

def getimgs():
    if current.get() != "__define__":
        on, off = COMBINES.QueryValue(current.get())
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
    left = NUMDAT.QueryValue(a)
    right = NUMDAT.QueryValue(b)

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

rolling = BooleanVar(value=False)
def update(_):
    if now_geo.get() == "hidden":
        winclose()
    if rolling.get() == True:
        rolling.set(False)
        return
    t = 0
    rolling.set(True)
    top.iconphoto(1, rdo)
    while True:
        t += 1
        shownum(choice(MEMBERS))
        if t == REPEATTIMES or rolling.get() == False:
            break
    top.iconphoto(1, rd)
    n = nextone.get()
    print(n)
    if n != -1:
        shownum(n)
        read(VOICEPROMPT.format(num=n, name=VOICETIP.TryQueryValue(str(n), "") or NAMEDICT.TryQueryValue(str(n), "")))
        nextone.set(-1)
    else:
        x = choice(MEMBERS)
        shownum(x)
        read(VOICEPROMPT.format(num=x, name=VOICETIP.TryQueryValue(str(x), "") or NAMEDICT.TryQueryValue(str(x), "")))

def focus():
    top.after(1000, focus)
    #top.focus_set()
    if now_geo.get() != "hidden":
        windll.user32.SetForegroundWindow(top.winfo_id())
    else:
        top.focus_set()

def start_tool(t):
    start_new_thread(system, (t,))

menubar = Menu(top)
comb = Menu(menubar, tearoff=0)
for k in COMBINES.EnumFiles():
    comb.add_radiobutton(label=k, value=k, command=init, variable=current)
comb.add_separator()
comb.add_radiobutton(label="从素材库中随机...", value="__define__", command=randtexture, variable=current)
menubar.add_cascade(label="贴图", menu=comb)

def add_trick_items(menu: Menu, labl, content:list):
    subm = Menu(menu, tearoff=0)
    for c in content:
        number = str(c) + (VOICETIPMARK if str(c) in VOICETIP.EnumFiles() else "")
        subm.add_command(label=number, command=lambda who=c:nextone.set(who), accelerator=NAMEDICT.QueryValue(str(c)))
    menu.add_cascade(label=labl, menu=subm)

def restart():
    execl(executable, executable, __file__)

def show_log():
    """==Spinner 1.2+24w02a 更新==
    1. 更改了加载封面
    2. 将贴图和设置都整合为AgLib文件
    3. 有了窗口图标
    4. 解决了某些平台上的抖窗闪窗问题
    5. 为了安全性考虑，保存设置会生成新的config2.aglib，需手动重命名"""
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

if DOTRICKS:
    menubar.add_cascade(label=f"恶搞", menu=tric)
else:
    menubar.add_cascade(label=f"恶搞（已禁用）", menu=Menu(menubar, tearoff=0))

edit = Menu(menubar, tearoff=0)
edit.add_command(label="打开编辑器", command=EditWindow)
edit.add_command(label="重新启动", command=restart)
menubar.add_cascade(label="配置", menu=edit)

too = Menu(menubar, tearoff=0)
for k in TOOLS.EnumFiles():
    too.add_command(label=k, command=lambda v=TOOLS.QueryValue(k): start_tool(v))
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
for t in range(100):
    top.attributes("-alpha", top.attributes("-alpha")+0.01)
    sleep(0.002)
    top.update()
tk.wait_window(top)
