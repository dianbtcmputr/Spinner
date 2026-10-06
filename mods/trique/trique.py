from ttkbootstrap import Frame, Toplevel, Button, IntVar
from tkinter import Listbox
from tkinter.simpledialog import askinteger

def main(api):
    tric = api.get_var("tric")
    PAD = api.get_var("PAD")
    NAMEDICT = api.get_var("NAMEDICT")
    nextone: IntVar = api.get_var("nextone")

    trique = []

    def open_dlg():
        win = api.create_window()

        lb = Listbox(win, selectmode="single", height=5)

        def insert(id, pos="end"):
            name = NAMEDICT.TryQueryValue(str(id), "")
            if name:
                con = f"{id} {name}"
            else:
                con = f"{id}"
            lb.insert(pos, con)
        
        for x in trique:
            insert(x)

        lb.pack(fill="both", **PAD)


        def add():
            new = askinteger("Spinner", "输入学号：", parent=win)
            if new is None:
                return
            insert(new, "end")
            flush_lb()

        def del_():
            sel = lb.curselection()
            for ind in sel:
                lb.delete(ind)
                break
            flush_lb()

        def flush_lb():
            lb.update()
            trique.clear()
            for x in lb.get(0, "end"):
                trique.append(int(x.strip().split(" ")[0]))

        bbox = Frame(win)
        Button(bbox, text="添加", command=add ).pack(side="left", fill="x", expand=1, **PAD)
        Button(bbox, text="删除", command=del_).pack(side="left", fill="x", expand=1, **PAD)
        bbox.pack(fill="x")
    
    tric.delete("end")
    tric.add_command(label="恶搞列表...", command=open_dlg)

    def n_o_read(*a):
        if trique:
            nextone.set(trique.pop(0))

    nextone.trace_add("read", n_o_read)