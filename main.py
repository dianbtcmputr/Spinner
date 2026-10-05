from _thread import start_new_thread
from ctypes import windll
from io import BytesIO
from os import execl, startfile, system
from os.path import splitext
from pprint import pformat
from random import choice, choices, shuffle
from sys import executable, getdefaultencoding
from time import sleep
from tkinter import (BOTH, DISABLED, END, EW, HORIZONTAL, LEFT, NS, NSEW, NW, RIGHT,
                     VERTICAL, W, BooleanVar, Canvas, DoubleVar, E, Event, IntVar,
                     Label, Menu, StringVar, Tk, Toplevel, Variable, X)
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import askokcancel, showerror, showinfo
from tkinter.scrolledtext import ScrolledText
from tkinter.simpledialog import askinteger
from tkinter.ttk import (Button, Checkbutton, Entry, Frame, Radiobutton,
                         Scrollbar, Spinbox, Treeview)
from types import NoneType
from webbrowser import open_new
from agdat import AgDir, CopyObj, Join, LoadAgFileName, SaveAgFileName, SplitBy
from PIL import Image, ImageTk
from pyttsx4 import Engine
#from windnd import hook_dropfiles

TYPENAMES = {"str": "字符串", "int": "整数", "float": "小数", "bool": "真/假", "NoneType": "空值"}

VERSION = "Spinner 1.3"
tk = Tk()
tk.title(VERSION)
eng = Engine()

class EditWindow(Toplevel):
    def __init__(self, lib: AgDir):
        self.lib = CopyObj(lib)
        Toplevel.__init__(self)
        self.title("Spinner")
        self.transient(top)
        self.geometry(f"{EDITORW}x{EDITORH}+{top.winfo_x()}+{top.winfo_y()}")
        self.pathf = Frame(self)
        Button(self.pathf, text="<", command=self.return_).pack(side=LEFT, **PAD)
        self.ety = Entry(self.pathf, font=EDITORFONT)
        self.ety.bind("<Return>", self.gobyety)
        self.ety.pack(side=LEFT, expand=1, fill=X, **PAD)
        Button(self.pathf, text="->", command=self.gobyety).pack(side=LEFT, **PAD)
        self.pathf.pack(fill=X)
        self.tvf = Frame(self)
        self.tv = Treeview(self.tvf, show="headings", selectmode="browse", columns=(0, 1, 2), )
        self.tv.heading(0, text="名称")
        self.tv.heading(1, text="类型")
        self.tv.heading(2, text="值")
        self.tv.tag_configure("oushu", background=TREECOLOREVEN, font=EDITORFONT)
        self.tv.tag_configure("jishu", background=TREECOLORODD, font=EDITORFONT)
        self.tv.bind("<1>", lambda e: self.tv.selection_set(self.tv.identify_row(e.y)))
        self.tv.bind("<3>", self.right)
        self.tv.bind("<Double-1>", self.open)
        self.tv.grid(row=0, column=0, sticky=NSEW)
        self.vbar = Scrollbar(self.tvf, command=self.tv.yview, orient=VERTICAL)
        self.vbar.grid(row=0, column=1, sticky=NS)
        self.hbar = Scrollbar(self.tvf, command=self.tv.xview, orient=HORIZONTAL)
        self.hbar.grid(row=1, column=0, sticky=EW)
        self.tv.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.tvf.grid_columnconfigure(0, weight=1)
        self.tvf.grid_rowconfigure(0, weight=1)
        self.tvf.pack(fill=BOTH, expand=1, **PAD)
        #hook_dropfiles(self.tv, func=self.dropfile)
        Button(self, text="保存", command=self.save).pack(anchor=E, **PAD)
        self.goto("")
    """
    def dropfile(self, files):
        fs = [f.decode(getdefaultencoding()) for f in files]
        #print(fs)
        for fn in fs:
            with open(fn, "rb") as f:
                self.lib.SetValue(Join(self.curr, fn), f.read())"""

    def goto(self, path):
        i = 0
        self.tv.delete(*self.tv.get_children())
        for x in sorted(self.lib.EnumDirs(path)):
            self.tv.insert("", END, values=(x, "数据夹", "-"), iid=Join(path, x), tags=("jishu" if (i // 2)*2 !=i else "oushu"))
            i += 1
        for x in sorted(self.lib.EnumFiles(path)):
            val = self.lib.QueryValue(Join(path, x))
            self.tv.insert("", END, values=(x, gettypename(val), repr(val)), iid=Join(path, x), tags=("jishu" if (i // 2)*2 !=i else "oushu"))
            i += 1
        self.ety.delete(0, END)
        self.ety.insert(0, path)
        self.curr = path
        self.update()
    
    def gobyety(self, *e):
        self.goto(self.ety.get())
    
    def return_(self):
        self.goto(SplitBy(self.curr, -1)[0])
    
    def refresh_tv(self):
        self.goto(self.curr)
        #tree_color(self.tv)
        #self.tv.update()

    def selecting(self):
        return self.tv.selection()[0]
    
    def save(self):
        SaveAgFileName(self.lib, "config.aglib")
    
    def open(self, *e):
        "打开/编辑"
        sel = self.selecting()
        if self.lib.IsDir(sel):
            self.goto(sel)
            return
        #res = askstring("Spinner", "新值：", initialvalue=repr(self.lib.QueryValue(sel)), parent=self)
        flag, res = ValueDialog.askvalue(self, self.lib.QueryValue(sel))
        if flag:
            self.lib.SetValue(sel, res)
            self.refresh_tv()
    
    def rename(self):
        "重命名"
        sel = self.selecting()
        x, y, w, h = self.tv.bbox(sel, 0)
        e = Entry(self.tv, font=EDITORFONT)
        e.insert(0, SplitBy(sel, -1)[-1])
        e.select_range(0, END)
        e.focus_set()
        flag = BooleanVar(value=False)
        def rename_confirm(event):
            res = e.get()
            e.destroy()
            if res:
                self.lib.Rename(sel, res)
                self.refresh_tv()
            flag.set(True)

        e.bind("<FocusOut>", rename_confirm)
        e.bind("<Return>", rename_confirm)
        e.place(x=x, y=y, width=w, height=h)
        #res = askstring("Spinner", "新名称：", parent=self, initialvalue=SplitBy(sel, -1)[-1])
        self.wait_variable(flag)
    def remove(self):
        "删除"
        sel = self.selecting()
        if askokcancel("Spinner", "是否删除？", parent=self):
            self.lib.Remove(sel)
            self.refresh_tv()
    
    def import_(self):
        "从另一库中导入"
        sel = self.selecting()
        fn = askopenfilename(parent=self)
        if fn:
            try:
                lib2 = LoadAgFileName(fn)
                self.lib.Remove(sel)
                self.lib.Attach(lib2.GetSubDirCopy(sel), sel)
                self.refresh_tv()
            except:
                showerror("Spinner", "所选库不含等位数据夹")

    def cleardir(self):
        "清空所选数据夹"
        sel = self.selecting()
        if askokcancel("Spinner", "是否清空？", parent=self):
            for i in self.lib.EnumAll(sel):
                self.lib.Remove(Join(sel, i))
            self.refresh_tv()

    def newdir(self):
        "新建数据夹"
        self.lib.MkDir(self.genpath(self.curr, "新数据夹"))
        self.refresh_tv()

    def newfile(self):
        "新建数据"
        self.lib.SetValue(self.genpath(self.curr, "新数据"), None)
        self.refresh_tv()
    
    def genpath(self, env, base):
        names = self.lib.EnumAll(env)
        if base not in names:
            return Join(env, base)
        else:
            id = 1
            while True:
                new = f"{base} {id}"
                if new not in names:
                    return Join(env, new)
                id += 1
    
    def right(self, e: Event):
        self.tv.selection_set(self.tv.identify_row(e.y))
        try:
            sel = self.selecting()
            items = [self.open, self.rename, self.newdir, self.newfile, self.remove]
            if self.lib.IsDir(sel):
                items.extend([self.import_, self.cleardir])
        except:
            items = [self.newdir, self.newfile]
        menu = Menu(self, tearoff=0)
        for i in items:
            menu.add_command(label=i.__doc__, command=i)
        menu.post(e.x_root, e.y_root)

def gettypename(dat) -> str:
    return TYPENAMES.get(type(dat).__name__, "其他")

def name2type(name):
    for k, v in TYPENAMES.items():
        if name == v:
            return eval(k)
    else:
        return None
class ValueDialog(Toplevel):
    def __init__(self, parent: Toplevel, val):
        Toplevel.__init__(self, parent)
        self.parent = parent
        self.transient(parent)
        self.geometry(f"{DIALOGW}x{DIALOGH}+{parent.winfo_x()}+{parent.winfo_y()}")
        self.title("Spinner")
        self.focus_set()
        self.typv = StringVar(value=gettypename(val))
        valf = Frame(self)
        for i, t in enumerate(["str", 0, 0.0, True, None, ()]):
            Radiobutton(valf, text=gettypename(t), variable=self.typv, value=gettypename(t)).grid(row=i, column=0, sticky=W, **PAD)
        
        self.strtxt = ScrolledText(valf, height=5, font=EDITORFONT)
        self.strtxt.insert(0.0, DEFAULTSTR)
        self.strtxt.grid(row=0, column=1, sticky=NSEW, **PAD)

        self.intv = IntVar(value=DEFAULTINT)
        Spinbox(valf, textvariable=self.intv, increment=INTINCREMENT, from_=VALUEMIN, to=VALUEMAX, font=EDITORFONT).grid(row=1, column=1, sticky=EW, **PAD)

        self.floatv = DoubleVar(value=DEFAULTFLOAT)
        Spinbox(valf, textvariable=self.floatv, increment=FLOATINCREMENT, from_=VALUEMIN, to=VALUEMAX, font=EDITORFONT).grid(row=2, column=1, sticky=EW, **PAD)

        self.boolv = BooleanVar(value=DEFAULTBOOL)
        Checkbutton(valf, variable=self.boolv, onvalue=True).grid(row=3, column=1, sticky=EW, **PAD)

        self.othrtxt = ScrolledText(valf, height=5, font=EDITORFONT)
        self.othrtxt.insert(0.0, pformat(DEFAULTOTHR))
        self.othrtxt.grid(row=5, column=1, sticky=NSEW, **PAD)
        
        valf.grid_columnconfigure(1, weight=1)
        valf.grid_rowconfigure(0, weight=1)
        valf.grid_rowconfigure(5, weight=1)
        valf.pack(fill=BOTH, expand=1)
        btnbox = Frame(self)
        Button(btnbox, text="确定", command=self.ok).pack(side=RIGHT, **PAD)
        Button(btnbox, text="取消", command=self.cancel).pack(side=RIGHT, **PAD)
        btnbox.pack(fill=X)
        self.setv(val)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def ok(self):
        self.val = self.getval()
        self.flag = True
        self.destroy()
    
    def cancel(self):
        self.val = self.getval()
        self.flag = False
        self.destroy()
    
    def wait(self):
        self.parent.wait_window(self)
        return self.flag, self.val
    
    def getval(self):
        t = name2type(self.typv.get())
        if t == str:
            return self.strtxt.get(0.0, END).strip("\n")
        elif t == int:
            return self.intv.get()
        elif t == float:
            return self.floatv.get()
        elif t == bool:
            return self.boolv.get()
        elif t == NoneType:
            return None
        else:
            return eval(self.othrtxt.get(0.0, END).strip("\n"))
    
    @classmethod
    def askvalue(cls, parent, val):
        dlg = ValueDialog(parent, val)
        return dlg.wait()
    
    def setv(self, val):
        t = type(val)
        self.typv.set(gettypename(val))
        if t == str:
            self.strtxt.delete(0.0, END)
            self.strtxt.insert(0.0, val)
        elif t == int:
            self.intv.set(val)
        elif t == float:
            self.floatv.set(val)
        elif t == bool:
            self.boolv.set(val)
        elif t == NoneType:
            pass
        else:
            self.othrtxt.delete(0.0, END)
            self.othrtxt.insert(0.0, pformat(val))

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
EDTRLIB = cnflib.GetSubDirCopy("HKEY_EDITOR")

SCALE = SYSCNF.QueryValue("scale")
MEMBERS = list(range(SYSCNF.QueryValue("min"), SYSCNF.QueryValue("max") + 1))
MEMBERS.extend(SYSCNF.QueryValue("blackNames") * SYSCNF.QueryValue("blackWeight"))

for x in SYSCNF.QueryValue("whiteNames"):
    MEMBERS.remove(x)
for x in range(10):
    shuffle(MEMBERS)

PAD = SYSCNF.QueryValue("pad")
WW, WH = int(256 * SCALE), int(208 * SCALE)
SW, SH = tk.winfo_screenwidth(), tk.winfo_screenheight()

REPEATTIMES = SYSCNF.QueryValue("repeatTimes")
ALPHA = SYSCNF.QueryValue("alpha")
DEFAULTTEXTURE = SYSCNF.QueryValue("defaultTexture")
DELTAY = SYSCNF.QueryValue("deltaY")
VOICEPROMPT = SYSCNF.QueryValue("voicePrompt")
DOTRICKS = SYSCNF.QueryValue("doTricks")
VOICETIPMARK = SYSCNF.QueryValue("voiceTipMark")
LOADWINSIZE = SYSCNF.QueryValue("loadWinSize")

EDITORW, EDITORH = EDTRLIB.QueryValue("editorWH")
DIALOGW, DIALOGH = EDTRLIB.QueryValue("dialogWH")
DEFAULTSTR = EDTRLIB.QueryValue("defaultStr")
DEFAULTINT = EDTRLIB.QueryValue("defaultInt")
DEFAULTFLOAT = EDTRLIB.QueryValue("defaultFloat")
DEFAULTBOOL = EDTRLIB.QueryValue("defaultBool")
DEFAULTOTHR = EDTRLIB.QueryValue("defaultOthr")
EDITORFONT = EDTRLIB.QueryValue("editorFont")
INTINCREMENT = EDTRLIB.QueryValue("intIncrement")
FLOATINCREMENT = EDTRLIB.QueryValue("floatIncrement")
VALUEMIN = EDTRLIB.QueryValue("valueMin")
VALUEMAX = EDTRLIB.QueryValue("valueMax")
TREECOLORODD = EDTRLIB.QueryValue("treeColorOdd")
TREECOLOREVEN = EDTRLIB.QueryValue("treeColorEven")

eng.setProperty("volume", SYSCNF.QueryValue("aiVolume"))
eng.setProperty("rate", SYSCNF.QueryValue("aiRate"))
IMGS = {}

files = texlib.EnumFiles()
fcount = len(files)
tk.title(VERSION)
tk.geometry(f"{LOADWINSIZE}x{LOADWINSIZE}+{int(SW/2 - LOADWINSIZE/2)}+{int(SH/2 - LOADWINSIZE/2)}")
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
    l.config(width=ind/fcount*LOADWINSIZE)
for x in range(100):
    tk.attributes("-alpha", tk.attributes("-alpha") - 0.01)
    tk.update()
    sleep(0.005)
tk.overrideredirect(1)
current = StringVar(value=DEFAULTTEXTURE)
define = Variable()

def getimgs():
    if current.get() != "__define__":
        on, off = COMBINES.QueryValue(current.get())
    else:
        on, off = define.get()
    return IMGS[on], IMGS[off]

tk.geometry("+10000+10000")
del c, l, w
top = Toplevel(tk)
top.title(VERSION)
top.transient(tk)
#tk.iconphoto(1, getimgs()[1])
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

set_top_geometry(f"{WW}x{WH}+{int(SW/2 - WW/2)}+{int(SH/2 - WH/2)+DELTAY}")
top.attributes("-alpha", 0)

def randtexture(*e):
    define.set(choices(list(IMGS.keys()), k=2))
    init()

def winclose():
    if now_geo.get() == "hidden": #hidden
        set_top_geometry(old_geo.get())
        top.attributes("-alpha", 1)

    else:
        set_top_geometry(f"{WW}x{WH}-{SW-30}+{top.winfo_y()}")
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
    #tk.iconphoto(1, off)

rolling = BooleanVar(value=False)
def update(_):
    on, off = getimgs()
    if now_geo.get() == "hidden":
        winclose()
    if rolling.get() == True:
        rolling.set(False)
        return
    t = 0
    rolling.set(True)
    #tk.iconphoto(1, on)
    while True:
        t += 1
        shownum(choice(MEMBERS))
        if t == REPEATTIMES or rolling.get() == False:
            break
    #tk.iconphoto(1, off)
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

def start_systm(t):
    start_new_thread(system, (t,))

def start_exe(t):
    start_new_thread(startfile, (t,))

def start_py(t):
    start_new_thread(exec, (t,))

def start_url(t):
    start_new_thread(open_new, (t,))

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
        subm.add_command(label=number, command=lambda who=c:nextone.set(who), accelerator=NAMEDICT.TryQueryValue(str(c)))
    menu.add_cascade(label=labl, menu=subm)

def restart():
    execl(executable, executable, __file__)

def show_log():
    """==Spinner 1.3 更新==
    1. 修复了编辑器字体设置无效bug
    2. 配置编辑器隔行变色奇偶色现在都可设
    3. 添加了退出按钮
    4. 更新了工具栏相关设置"""
    showinfo("Spinner", show_log.__doc__, parent=top)

def contributors():
    """李喆祎（糖衣2023级老5班新1班电表）"""
    showinfo("Spinner", contributors.__doc__, parent=top)

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
edit.add_command(label="打开编辑器", command=lambda:EditWindow(cnflib))
edit.add_command(label="重新启动", command=restart)
edit.add_command(label="退出", command=tk.destroy)
edit.add_separator()
edit.add_command(label="更新日志", command=show_log)
edit.add_command(label="制作者名单", command=contributors)
menubar.add_cascade(label="配置", menu=edit)

too = Menu(menubar, tearoff=0)
def genmenu(pmenu: Menu, path: str):
    lb = TOOLS.TryQueryValue(Join(path, "label"), SplitBy(path, -1)[-1])
    cmd = TOOLS.TryQueryValue(Join(path, "command"), int)
    cmd_t = TOOLS.TryQueryValue(Join(path, "commandType"), None)
    if not cmd_t:
        pmenu.add_command(label=lb, state=DISABLED)
    elif cmd_t == "subCommands":
        m = Menu(pmenu, tearoff=0)
        for x in sorted(TOOLS.EnumDirs(path)):
            genmenu(m, Join(path, x))
        pmenu.add_cascade(menu=m, label=lb)
    elif cmd_t == "system":
        pmenu.add_command(label=lb, command=lambda cmd=cmd:start_systm(cmd))
    elif cmd_t == "startFile":
        pmenu.add_command(label=lb, command=lambda cmd=cmd:start_exe(cmd))
    elif cmd_t == "pyExec":
        pmenu.add_command(label=lb, command=lambda cmd=cmd:start_py(cmd))
    elif cmd_t == "openUrl":
        pmenu.add_command(label=lb, command=lambda cmd=cmd:start_url(cmd))
for x in sorted(TOOLS.EnumDirs()):
    genmenu(too, x)
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