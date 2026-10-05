from _thread import start_new_thread
from ctypes import windll
from json import dumps, loads
from os import execl, listdir, system
from os.path import join, splitext
from random import choice, choices, shuffle
from sys import executable
from time import sleep
from tkinter import (BOTH, END, INSERT, BooleanVar, Canvas, IntVar, Label, Menu, StringVar, Tk,
                     Toplevel, Variable, X)
from tkinter.messagebox import showerror, showinfo
from tkinter.scrolledtext import ScrolledText
from tkinter.simpledialog import askinteger
from tkinter.ttk import Button, Frame, Notebook, Progressbar

from PIL import Image, ImageTk
from pyttsx4 import Engine

VERSION = "Spinner 1.2"
tk = Tk()
tk.title(VERSION)
eng = Engine()

class EditWindow(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.title("Spinner")
        self.transient(top)
        self.place_widgets()
        self.geometry(f"{EDITORW}x{EDITORH}+{top.winfo_x()}+{top.winfo_y()}")
    
    def place_widgets(self):
        nb = Notebook(self)
        for txt, dat, fn in [["系统设置", SYSCNF, "syscnf.json"],
                             ["贴图设置", COMBINES, "combines.json"],
                             ["数字数据", NUMDAT, "numdat.json"],
                             ["学号姓名", NAMEDICT, "namedict.json"],
                             ["系统工具", TOOLS, "tools.json"],
                             ["读音提示", VOICETIP, "voicetip.json"]]:
            f = Frame(self)
            st = ScrolledText(f, font=EDITORFONT)
            st.insert(INSERT, prettydat(dat))
            st.pack(fill=BOTH, expand=1, **PAD)
            Button(f, text="保存（一定要保存！！！）", command=lambda fn=fn, st=st:self.save(fn, st)).pack(fill=X, **PAD)
            nb.add(f, text=txt)
        nb.pack(fill=BOTH, expand=1, **PAD)
    
    def save(self, fn, st: ScrolledText):
        cont = st.get("0.0", END).replace("\n", "").strip()
        try:    
            dat = dumps(eval(cont))
            with open(join("config", fn), "w") as f:
                f.write(dat)
            showinfo("Spinner", "保存成功", parent=self)
        except Exception as e:
            showerror("Spinner", f"引发{type(e).__name__}错误，保存失败: \n{e}", parent=self)

def loadjson(fn: str) -> dict:
    with open(join("config", f"{fn}.json")) as f:
        return loads(f.read())

def prettydat(dat: dict) -> str:
    res = []
    for k, v in dat.items():
        res.append(f"{repr(k)}: {repr(v)}")
    return "{ " + (",\n  ".join(res)) + "}"

SYSCNF = loadjson("syscnf")
NUMDAT = loadjson("numdat")
COMBINES = loadjson("combines")
NAMEDICT = loadjson("namedict")
TOOLS = loadjson("tools")
VOICETIP = loadjson("voicetip")

SCALE = SYSCNF["scale"]
MEMBERS = list(range(SYSCNF["min"], SYSCNF["max"] + 1))
MEMBERS.extend(SYSCNF["blackNames"] * SYSCNF["blackWeight"])

for x in SYSCNF["whiteNames"]:
    MEMBERS.remove(x)
for x in range(10):
    shuffle(MEMBERS)

PAD = SYSCNF["pad"]
W, H = int(256 * SCALE), int(208 * SCALE)
SW, SH = tk.winfo_screenwidth(), tk.winfo_screenheight()
REPEATTIMES = SYSCNF["repeatTimes"]
ALPHA = SYSCNF["alpha"]
DEFAULTTEXTURE = SYSCNF["defaultTexture"]
EDITORFONT = SYSCNF["editorFont"]
DELTAY = SYSCNF["deltaY"]
LOADBG = SYSCNF["loadBG"]
LOADFG = SYSCNF["loadFG"]
VOICEPROMPT = SYSCNF["voicePrompt"]
DOTRICKS = SYSCNF["doTricks"]
EDITORW, EDITORH = SYSCNF["editorWH"]
VOICETIPMARK = SYSCNF["voiceTipMark"]

eng.setProperty("volume", SYSCNF["aiVolume"])
eng.setProperty("rate", SYSCNF["aiRate"])

IMGS = {}
files = listdir("assets")
tk.config(bg=LOADBG)
textv = StringVar(value="Loading Images")
Label(tk, text="Spinner", font="Consolas 60", fg=LOADFG, bg=LOADBG).pack(fill=X, **PAD)
Label(tk, text="Version 1.2", fg=LOADFG, bg=LOADBG, font="Consolas 30").pack(fill=X, **PAD)
Label(tk, textvariable=textv, fg=LOADFG, bg=LOADBG, font="Consolas 15").pack(fill=X, **PAD)

pbv = IntVar()
Progressbar(tk, maximum=len(files)+100, variable=pbv).pack(fill=X, **PAD)
tk.geometry(f"600x250+{int(SW/2 - 300)}+{int(SH/2 - 125)+DELTAY}")

for ind, fn in enumerate(files):
    if fn.endswith(".png"):
        IMGS[splitext(fn)[0]] = ImageTk.PhotoImage(Image.open(join("assets", fn)).crop((0, 0, 16, 16)).resize((int(16 * SCALE), int(16 * SCALE))))
        tk.update()
    pbv.set(pbv.get() + 1)
for x in range(30):
    tk.update()
    sleep(0.02)
textv.set("Spinner Progress")
for x in range(100):
    pbv.set(pbv.get() + 1)
    tk.update()
    sleep(0.0005+x*0.0003)
for x in range(100):
    tk.attributes("-alpha", tk.attributes("-alpha") - 0.01)
    tk.update()
    sleep(0.005)

tk.geometry("+10000+10000")
tk.overrideredirect(1)
top = Toplevel(tk)
top.title(VERSION)
top.transient(tk)
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

current = StringVar(value=DEFAULTTEXTURE)
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
        shownum(choice(MEMBERS))
        if t == REPEATTIMES or rolling.get() == False:
            break

    n = nextone.get()
    print(n)
    if n != -1:
        shownum(n)
        read(VOICEPROMPT.format(num=n, name=VOICETIP.get(str(n), "") or NAMEDICT.get(str(n), "")))
        nextone.set(-1)
    else:
        x = choice(MEMBERS)
        shownum(x)
        read(VOICEPROMPT.format(num=x, name=VOICETIP.get(str(x), "") or NAMEDICT.get(str(x), "")))

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
for k in COMBINES.keys():
    comb.add_radiobutton(label=k, value=k, command=init, variable=current)
comb.add_separator()
comb.add_radiobutton(label="从素材库中随机...", value="__define__", command=randtexture, variable=current)
menubar.add_cascade(label="贴图", menu=comb)

def add_trick_items(menu: Menu, labl, content:list):
    subm = Menu(menu, tearoff=0)
    for c in content:
        number = str(c) + (VOICETIPMARK if str(c) in VOICETIP.keys() else "")
        subm.add_command(label=number, command=lambda who=c:nextone.set(who), accelerator=NAMEDICT[str(c)])
    menu.add_cascade(label=labl, menu=subm)

def restart():
    execl(executable, executable, __file__)

def show_log():
    """==Spinner 1.2 更新==
    1. 修复了重启bug
    2. 删除了后台监视器
    3. 添加编辑器的字体设置功能
    4. 添加AI音量、语速设置功能
    5. 现在恶搞栏的学号后面有了姓名
    6. 将“姓名学号”改为“学号姓名”
    7. 添加了读音提示配置文件，且在恶搞栏中，设置了读音提示的成员的学号后会有标记（默认为 *）
    8. 将点一下卷动几秒自动出下一个号，改为点一下之后开始不停卷动，再点一下或卷动次数达到最大值才出号
    9. 现在Spinner窗口不再能通过右击任务栏图标的途径关闭
    10. 添加了加载封面，前景背景颜色可设
    11. 现在如果用户在窗口隐藏时点击抽号，那么窗口将自动弹出来
    12. 增加了窗口垂直方向位置偏好设置
    13. 增加了编辑器窗口大小设置，以及保存成功或失败的提示"""
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