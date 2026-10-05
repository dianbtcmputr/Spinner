from json import loads
from os import listdir
from random import choice, choices, shuffle
from tkinter import Canvas, IntVar, Menu, StringVar, Tk, Toplevel, Variable
from os.path import join, splitext
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk

tk = Tk()
def loadjson(fn: str) -> dict:
    with open(join("config", f"{fn}.json")) as f:
        return loads(f.read())

SYSCNF = loadjson("syscnf")
NUMDAT = loadjson("numdat")
COMBINES = loadjson("combines")

SCALE = SYSCNF["scale"]
MEMBERS = list(range(SYSCNF["min"], SYSCNF["max"] + 1))
MEMBERS.extend(SYSCNF["blacknames"] * SYSCNF["blackweight"])
shuffle(MEMBERS)
for x in SYSCNF["whitenames"]:
    MEMBERS.remove(x)

W, H = int(256 * SCALE), int(208 * SCALE)
SW, SH = tk.winfo_screenwidth(), tk.winfo_screenheight()

IMGS = {}
files = listdir("assets")
pbv = IntVar()
Progressbar(tk, maximum=len(files), variable=pbv).pack(fill="both")
tk.geometry(f"300x64+{int(SW/2 - 300)}+{int(SH/2 - 64)}")
for ind, fn in enumerate(files):
    if fn.endswith(".png"):
        #sleep(0.01)
        IMGS[splitext(fn)[0]] = ImageTk.PhotoImage(Image.open(join("assets", fn)).resize((int(16 * SCALE), int(16 * SCALE))))
        pbv.set(pbv.get() + 1)
        tk.update()
        print("load",fn)

tk.geometry("+10000+10000")
top = Toplevel(tk)
top.title("Spinner 1.1")
top.transient(tk)
cvs = Canvas(top, highlightthickness=0)
cvs.place(relx=0, rely=0, relwidth=1, relheight=1)

now_geo = StringVar()
old_geo = StringVar()
def set_top_geometry(geo, hidding=False):
    old_geo.set(now_geo.get()) if not hidding else old_geo.set("hidden")
    now_geo.set(geo)
    top.geometry(geo)

set_top_geometry(f"{W}x{H}+{int(SW/2 - W/2)}+{int(SH/2 - H/2)}")

current = StringVar(value="Redstone Lamp")
define = Variable()

def getimgs():
    if current.get() != "__define__":
        on, off = COMBINES[current.get()]
    else:
        on, off = define.get()
    return IMGS[on], IMGS[off]

def define_texture():
    define.set(choices(list(IMGS.keys()), k=2))
    init()


def winclose():
    if now_geo.get() == "hidden": #hidden
        """print("a",old_geo.get())
        top.geometry(old_geo.get())
        old_geo.set("hidden")
        print("b",old_geo.get())"""
        set_top_geometry(old_geo.get())

    else:
        """
        old_geo.set(top.geometry())
        print("c", old_geo.get())
        top.geometry(f"-{SW-30}+{top.winfo_y()}")"""
        set_top_geometry(f"{W}x{H}-{SW-30}+{top.winfo_y()}")
        now_geo.set("hidden")

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
    for t in range(SYSCNF["repeattimes"]):
        shownum(choice(MEMBERS))

def focus():
    top.after(1000, focus)
    top.focus_set()

menubar = Menu(top)
comb = Menu(menubar)
for k in COMBINES.keys():
    comb.add_radiobutton(label=k, value=k, command=init, variable=current)
comb.add_separator()
comb.add_radiobutton(label="随机", value="__define__", command=define_texture, variable=current)

menubar.add_cascade(label="显示组合", menu=comb)
top.config(menu=menubar)

init()
cvs.bind("<1>", update)
top.after(0, focus)
top.attributes("-topmost", 1)
top.resizable(0, 0)
tk.wait_window(top)
#tk.destroy()