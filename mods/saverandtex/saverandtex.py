from tkinter.messagebox import showinfo
from tkinter.simpledialog import askstring
from ttkbootstrap import Menu

from aglib import SaveAgFileName

def main(api):
    menuapi = api.get_mod_obj("menuapi").module

    comb: Menu = menuapi.get_menu("贴图")
    
    current = api.get_var("current")
    define = api.get_var("define")
    top = api.get_var("top")

    def save_tex():
        if current.get() == "__define__":
            on, off = define.get()
            name = askstring("Spinner - Save Random Texture", "输入名称：", parent=top)
            if name:
                max_n = -float("inf")
                for com in api.get_var("cnflib").EnumFiles("HKEY_COMBINES"):
                    max_n = max(max_n, int(com.split(" ")[0]))

                api.get_var("cnflib").SetValue(f"HKEY_COMBINES\\{max_n + 1} {name}", [on, off])
                SaveAgFileName(api.get_var("cnflib"), "config.aglib")
                showinfo("Spinner - Save Random Texture", "添加成功", parent=top)
        else:
            showinfo("Spinner - Save Random Texture", "当前贴图为库中已有", parent=top)

    comb.add_command(label="保存此贴图", command=save_tex)