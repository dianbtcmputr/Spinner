from json import loads
from os import listdir
from random import choice
from tkinter import Canvas, Menu, StringVar, Tk
from os.path import join, splitext
from PIL import Image, ImageTk

tk = Tk()
tk.title("Spinner - Copyright Arway (Grade 2023, Class 1)")
cvs = Canvas(tk, highlightthickness=0)
cvs.place(relx=0, rely=0, relwidth=1, relheight=1)

def loadjson(fn: str) -> dict:
    with open(join("config", f"{fn}.json")) as f:
        return loads(f.read())

SYSCNF = loadjson("syscnf")
NUMDAT = loadjson("numdat")
COMBINES = loadjson("combines")

SCALE = SYSCNF["scale"]
MEMBERS = list(range(SYSCNF["min"], SYSCNF["max"] + 1))
MEMBERS.extend(SYSCNF["blacknames"] * SYSCNF["blackweight"])
for x in SYSCNF["whitenames"]:
    MEMBERS.remove(x)

tk.geometry(f"{256 * SCALE}x{208 * SCALE}")

IMGS = {}
for fn in listdir("assets"):
    IMGS[splitext(fn)[0]] = ImageTk.PhotoImage(Image.open(join("assets", fn)).resize((16 * SCALE, 16 * SCALE)))

current = StringVar(value="Redstone Lamp")

def getimgs():
    on, off = COMBINES[current.get()]
    return IMGS[on], IMGS[off]

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
            cvs.create_image(x * 16 * SCALE, y * 16 * SCALE, image=off, anchor="nw")
    id_x = 0
    id_y = 0
    for y in range(2, 11):
        for x in range(2, 7):
            cvs.create_image(x * 16 * SCALE, y * 16 * SCALE, image=on, anchor="nw", tag=f"l{id_x}")
            id_x += 1
        for x in range(9, 14):
            cvs.create_image(x * 16 * SCALE, y * 16 * SCALE, image=on, anchor="nw", tag=f"r{id_y}")
            id_y += 1
    cvs.update()

def update(event):
    for t in range(SYSCNF["repeattimes"]):
        shownum(choice(MEMBERS))

def focus():
    tk.focus_set()
    tk.after(1000, focus)

menubar = Menu(tk)
comb = Menu(menubar)
for k in COMBINES.keys():
    comb.add_radiobutton(label=k, value=k, command=init, variable=current)
menubar.add_cascade(label="显示组合", menu=comb)
tk.config(menu=menubar)

init()
cvs.bind("<1>", update)
tk.after(0, focus)
tk.attributes("-topmost", 1)
tk.resizable(0, 0)
tk.mainloop()