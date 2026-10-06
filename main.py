from _thread import start_new_thread
from atexit import register
from io import BytesIO
from os import execl
from os.path import splitext
from pprint import pformat
from random import Random
from sys import executable
from time import sleep
from tkinter import Event, Label as TLabel
from ttkbootstrap import (
    BooleanVar, Canvas, DoubleVar, IntVar, Button, Menu, StringVar, Window, Toplevel,
    Variable, Checkbutton, Entry, Frame, Radiobutton, Scrollbar, Spinbox, Treeview)
from ttkbootstrap.constants import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askokcancel, showerror, showinfo
from tkinter.scrolledtext import ScrolledText
from tkinter.simpledialog import askinteger
from types import NoneType
from agdat import AgDir, Join, LoadAgFileName, SaveAgFileName, SplitBy, CopyObj
from PIL import Image, ImageTk
from pyttsx4 import Engine
from cnf_and_con import *
import spindle, sys

VERSION = "Spinner 1.5 - snapshot 1"
register(lambda: tk.destroy())

tk = Window()
tk.title(VERSION)
SW, SH = tk.winfo_screenwidth(), tk.winfo_screenheight()

eng = Engine()

flashrng = Random()
namesrng = Random()
textrrng = Random()

class EditWindow(Toplevel):
    def __init__(self, lib: AgDir):
        self.lib = CopyObj(lib)
        Toplevel.__init__(self)
        self.title("Spinner")
        self.transient(top)
        self.geometry(f"{EDITORW}x{EDITORH}+{top.winfo_x()}+{top.winfo_y()}")
        self.focus_set()
        self.pathf = Frame(self)
        Button(self.pathf, text="<", command=self.return_).pack(side=LEFT, **PAD)
        self.ety = Entry(self.pathf, font=EDITORFONT)
        self.ety.bind("<Return>", self.gobyety)
        self.ety.pack(side=LEFT, expand=1, fill=X, **PAD)
        Button(self.pathf, text="->", command=self.gobyety).pack(side=LEFT, **PAD)
        self.pathf.pack(fill=X)
        self.tvf = Frame(self)
        self.tv = Treeview(self.tvf, show="tree headings", selectmode="browse", columns=(0, 1))
        self.tv.heading("#0", text="名称")
        self.tv.heading(0, text="类型")
        self.tv.heading(1, text="值")
        self.tv.tag_configure("oushu", background=TREECOLORODD, font=EDITORFONT)
        self.tv.tag_configure("jishu", background=TREECOLOREVEN, font=EDITORFONT)

        sel_er = lambda e: self.tv.selection_set(self.tv.identify_row(e.y))
        self.tv.bind("<1>", sel_er)
        self.tv.bind("<3>", lambda e: (self.tv.focus_set(), self.right(e)))
        self.tv.bind("<Double-1>", lambda e: (sel_er(e), self.open(e)))

        self.tv.grid(row=0, column=0, sticky=NSEW)
        self.vbar = Scrollbar(self.tvf, command=self.tv.yview, orient=VERTICAL)
        self.vbar.grid(row=0, column=1, sticky=NS)
        self.tv.config(yscrollcommand=self.vbar.set)
        self.tvf.grid_columnconfigure(0, weight=1)
        self.tvf.grid_rowconfigure(0, weight=1)
        self.tvf.pack(fill=BOTH, expand=1, **PAD)
        Button(self, text="保存", command=self.save).pack(anchor=E, **PAD)
        self.goto("")
        self.already_saved = True
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        if self.already_saved:
            self.destroy()
        else:
            answ = askokcancel("Spinner", "有未保存的更改，确定要关闭吗？")
            if answ:
                self.destroy()

    def goto(self, path):
        i = 0
        self.tv.delete(*self.tv.get_children())
        for x in sorted(self.lib.EnumDirs(path)):
            self.tv.insert(
                "",
                END,
                text=x,
                values=("数据夹", "-"),
                iid=Join(path, x),
                tags=("jishu" if (i // 2) * 2 != i else "oushu"),
                image=TYPE_ICONS["dir"]
            )
            i += 1
        
        for x in sorted(self.lib.EnumFiles(path)):
            val = self.lib.QueryValue(Join(path, x))
            self.tv.insert(
                "",
                END,
                text=x,
                values=(gettypename(val), repr(val)),
                iid=Join(path, x),
                tags=("jishu" if (i // 2) * 2 != i else "oushu"),
                image=TYPE_ICONS.get(type(val).__name__, TYPE_ICONS["other"])
            )
            i += 1
        
        self.ety.delete(0, END)
        self.ety.insert(0, path)
        self.curr = path
        self.update()
    
    def gobyety(self, *e):
        self.goto(self.ety.get())
    
    def return_(self):
        self.goto(SplitBy(self.curr, -1)[0])
    
    def refresh_tv(self, see=None):
        self.goto(self.curr)
        if see:
            self.tv.selection_set(see)
            self.tv.see(see)

    def selecting(self):
        s = self.tv.selection()
        if s:
            return s[0]
        else:
            return None

    def flag_changed(self):
        self.already_saved = False
    
    def save(self):
        SaveAgFileName(self.lib, "config.aglib")
        self.already_saved = True
        showinfo("Spinner", "保存成功")
        global cnflib
        cnflib = CopyObj(self.lib)
    
    def open(self, *e):
        "打开/编辑"
        sel = self.selecting()
        if sel is None:
            return
        if self.lib.IsDir(sel):
            self.goto(sel)
            return
        flag, res = ValueDialog.askvalue(self, self.lib.QueryValue(sel))
        if flag:
            self.lib.SetValue(sel, res)
            self.flag_changed()
            self.refresh_tv(sel)
    
    def rename(self):
        "重命名"
        sel = self.selecting()
        if sel is None:
            return
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
                try:
                    self.lib.Rename(sel, res)
                    self.flag_changed()
                    self.refresh_tv(Join(SplitBy(sel, -1)[0], res))
                except:
                    pass
            flag.set(True)

        e.bind("<FocusOut>", rename_confirm)
        e.bind("<Return>", rename_confirm)
        e.place(x=x, y=y, width=w, height=h)
        #res = askstring("Spinner", "新名称：", parent=self, initialvalue=SplitBy(sel, -1)[-1])
        self.wait_variable(flag)

    def remove(self):
        "删除"
        sel = self.selecting()
        if sel is None:
            return
        if askokcancel("Spinner", "是否删除？", parent=self):
            self.lib.Remove(sel)
            self.flag_changed()
            self.refresh_tv()
    
    def import_(self):
        "从另一库中导入"
        sel = self.selecting()
        if sel is None:
            return
        fn = askopenfilename(parent=self)
        if fn:
            try:
                lib2 = LoadAgFileName(fn)
                self.lib.Remove(sel)
                self.lib.Attach(lib2.GetSubDirCopy(sel), sel)
                self.flag_changed()
                # self.refresh_tv()
            except:
                showerror("Spinner", "所选库不含等位数据夹")

    def cleardir(self):
        "清空所选数据夹"
        sel = self.selecting()
        if sel is None:
            return
        if askokcancel("Spinner", "是否清空？", parent=self):
            for i in self.lib.EnumAll(sel):
                self.lib.Remove(Join(sel, i))
            self.flag_changed()
            # self.refresh_tv()

    def newdir(self):
        "新建数据夹"
        newp = self.genpath(self.curr, "新数据夹")
        self.lib.MkDir(newp)
        self.flag_changed()
        self.refresh_tv(newp)
        self.rename()

    def newfile(self):
        "新建数据"
        newp = self.genpath(self.curr, "新数据")
        self.lib.SetValue(newp, None)
        self.flag_changed()
        self.refresh_tv(newp)
        self.rename()
    
    def importbytesfromfile(self):
        "导入文件"
        sel = self.selecting()
        if sel is None:
            return
        file = askopenfilename(parent=self)
        with open(file, "rb") as f:
            self.lib.SetValue(sel, f.read())
            self.flag_changed()
        self.refresh_tv()
    
    def exportbytes(self):
        "导出为"
        sel = self.selecting()
        if sel is None:
            return
        file = asksaveasfilename(parent=self)
        with open(file, "wb") as f:
            f.write(self.lib.QueryValue(sel))

    def showasimg(self):
        "作为图片查看"
        sel = self.selecting()
        if sel is None:
            return
        img = Image.open(BytesIO(self.lib.QueryValue(sel))).convert("RGB")
        start_new_thread(img.show, ())
    
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
            if sel is None:
                raise Exception
            items = [self.open, self.rename, self.newdir, self.newfile, self.remove]
            if self.lib.IsDir(sel):
                items.extend([self.import_, self.cleardir])
            elif isinstance(self.lib.QueryValue(sel), bytes):
                items.extend([self.showasimg, self.importbytesfromfile, self.exportbytes])
        except:
            items = [self.newdir, self.newfile]
        menu = Menu(self, tearoff=0)
        for i in items:
            menu.add_command(label=i.__doc__, command=i)
        menu.add_separator()
        menu.post(e.x_root, e.y_root)

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
        self.focus_set()
        self.title("Spinner")
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

eng.setProperty("volume", SYSCNF.QueryValue("aiVolume"))
eng.setProperty("rate", SYSCNF.QueryValue("aiRate"))

IMGS = {}
TYPE_ICONS = {}

def pre_load_assets():
    files = texlib.EnumFiles()
    fcount = len(files)

    tk.title(VERSION)
    tk.geometry(f"{LOADWINSIZE}x{LOADWINSIZE}+{int(SW/2 - LOADWINSIZE/2)}+{int(SH/2 - LOADWINSIZE/2)}")
    # tk.update()
    tk.style.map("Treeview", rowheight=[("!disabled", SPACING)])
    
    c = Canvas(tk)
    c.place(x=0, y=0, relwidth=1, relheight=1)
    rd_off, rd_on = loadpimg(iconlib, "loading_off.png", LOADWINSIZE), loadpimg(iconlib, "loading_on.png", LOADWINSIZE)
    c.create_image(0, 0, image=rd_off, anchor=NW)

    l = TLabel(c, anchor=NW, image=rd_on)
    l.config(width=1)

    c.create_window(-2, -2, anchor=NW, window=l)
    tk.update()
    tk.update_idletasks()

    eng.say("")
    eng.runAndWait()

    for ind, fn in enumerate(files):
        if fn.endswith(".png"):
            IMGS[splitext(fn)[0]] = loadpimg(texlib, fn, int(16*SCALE))
            tk.update()
            tk.update_idletasks()
        
        l.config(width=ind / fcount * LOADWINSIZE)

    for fn in iconlib.EnumFiles():
        if fn.startswith("type_"):
            if iconlib.QueryValue(fn): # TODO 图标补齐可删
                img = Image.open(BytesIO(iconlib.QueryValue(fn))).resize((SPACING, SPACING))
                TYPE_ICONS[fn.removeprefix("type_").removesuffix(".png")] = ImageTk.PhotoImage(img)

    for _ in range(100):
        tk.attributes("-alpha", tk.attributes("-alpha") - 0.01)
        tk.update()
        sleep(0.002)

    tk.overrideredirect(1)
    tk.geometry("+10000+10000")

pre_load_assets()

current = StringVar(value=DEFAULTTEXTURE)
define = Variable()

def getimgs():
    if current.get() != "__define__":
        on, off = COMBINES.TryQueryValue(current.get()) or COMBINES.TryQueryValue(COMBINES.EnumFiles()[0])
    else:
        on, off = define.get()
    return IMGS[on], IMGS[off]

def set_top_geometry(geo, hidding=False):
    old_geo.set(now_geo.get()) if not hidding else old_geo.set("hidden")
    now_geo.set(geo)
    top.geometry(geo)

now_geo = StringVar()
old_geo = StringVar()

top = Toplevel(tk)
top.title(VERSION)
set_top_geometry(f"{WW}x{WH}+{int(SW/2 - WW/2)}+{int(SH/2 - WH/2)+DELTAY}")
top.attributes("-alpha", 0)
top.transient(tk)

cvs = Canvas(top)
cvs.place(relx=0, rely=0, relwidth=1, relheight=1)

nextone = IntVar(value=-1)

def read(msg):
    start_new_thread(_read, (msg,))

def _read(msg):
    try:
        eng.endLoop()
    except Exception:
        pass
    eng.say(msg)
    eng.runAndWait()

def randtexture(*e):
    define.set(textrrng.choices(list(IMGS.keys()), k=2))
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
    if now_geo.get() == "hidden":
        winclose()
    if rolling.get() == True:
        rolling.set(False)
        return
    t = 0
    rolling.set(True)
    while True:
        t += 1
        shownum(flashrng.choice(MEMBERS))
        if t == REPEATTIMES or rolling.get() == False:
            break

    n = nextone.get()
    if n != -1:
        nextone.set(-1)
    else:
        n = namesrng.choice(MEMBERS)

    shownum(n)
    read(VOICEPROMPT.format(num=n, name=VOICETIP.TryQueryValue(str(n), "") or NAMEDICT.TryQueryValue(str(n), "")))

def focus():
    top.after(3050, focus)
    tk.attributes("-topmost", 1)

menubar = Menu(top)
comb = Menu(menubar, tearoff=0)

for k in sorted(COMBINES.EnumFiles(), key=lambda x: int(x.split(" ")[0])):
    comb.add_radiobutton(label=k.split(" ", 1)[1], value=k, command=init, variable=current)

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
    """== Spinner 1.5 - snapshot 1 更新 ==
    
    1. 采用新的窗口库
    2. 现在配置保存成功会弹窗提示
    3. 引入模组加载器“Spindle Loader”
    4. 去除了工具菜单，因为模组通常能更好地驱动这类外部功能
    5. 现在配置编辑器未保存而退出后，重新进入时不会保留之前的更改
    6. 现在程序加载时，语音合成器会朗读空字符串以进行预加载
    7. 修复了加载进度在某些系统上始终为满的漏洞
    8. 修复了配置编辑器连续双击同一位置时会报错的漏洞
    9. 修复了配置编辑器重命名不做任何更改时会报错的漏洞
    10. 现在贴图数据夹中的数据名称将以第一空格前的数字为排序依据，并且该数将不会显示
    11. 现在如果 defaultTexture 的值不在 HKEY_COMBINES 中，程序将使用所有贴图组合中的第一个，而不是报错退出
    12. 现在新建数据（夹）时，将自动打开重命名框"""
    showinfo("Spinner", show_log.__doc__, parent=top)

def contributors():
    """电表讲电脑 @ 抖音 Bilibili"""
    showinfo("Spinner", contributors.__doc__, parent=top)

tric = Menu(menubar, tearoff=0)
subs = {}
mems = sorted(list(set(MEMBERS)))

for x in range(0, max(mems), 10):
    subs[f"{x}-{x + 10}"] = sorted([m for m in mems if m <= x + 10 and m >= x])

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
edit.add_command(label="打开编辑器", command=lambda: EditWindow(cnflib))
edit.add_command(label="重新启动", command=restart)
edit.add_command(label="退出", command=top.destroy)
edit.add_separator()
edit.add_command(label="更新日志", command=show_log)
edit.add_command(label="制作者名单", command=contributors)
menubar.add_cascade(label="配置", menu=edit)

def var_getter(name):
    return globals()[name]

def var_setter(name, val):
    globals()[name] = val

modm = Menu(menubar, tearoff=0)
menubar.add_cascade(label="模组", menu=modm) # 必须在模组加载前添加

spindle.var_getter = var_getter
spindle.var_setter = var_setter
ALL_MODS = spindle.load_all_mods()
spindle.call_integrates()

if ALL_MODS:
    icon_pimg = ImageTk.PhotoImage(Image.open(BytesIO(iconlib.QueryValue("win_icon_modded.png"))))
    top.title(f"{VERSION} - Spindle Loader")
else:
    icon_pimg = ImageTk.PhotoImage(Image.open(BytesIO(iconlib.QueryValue("win_icon.png"))))

top.iconphoto(True, icon_pimg)

if spindle.mod_has_made_cnf:
    SaveAgFileName(cnflib, "config.aglib")

for modobj in ALL_MODS:
    modm.add_command(
        label=f"  {modobj.name}",
        command=lambda m=modobj: spindle.ModDescDlg(top, m),
        image=modobj.icon,
        compound=LEFT,
        accelerator=modobj.version
    )
modm.add_separator()

mod_ctrl = Menu(modm, tearoff=0)
mod_ctrl.add_command(label="禁用/启用 管理", command=lambda: spindle.DisableMgr())

modm.add_cascade(label=f"    {len(ALL_MODS)} 个 Mod 已加载", menu=mod_ctrl)

top.config(menu=menubar)

init()
cvs.bind("<1>", update)
top.after(0, focus)
top.attributes("-topmost", 1)
top.resizable(0, 0)
top.deiconify()
top.focus_force()

for t in range(100):
    top.attributes("-alpha", top.attributes("-alpha")+0.01)
    sleep(0.002)
    top.update()

tk.wait_window(top)