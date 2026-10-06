from ttkbootstrap import StringVar, Toplevel, Menu

def main(api):
    top: Toplevel = api.get_var("top")
    style = top.style
    style.theme_use(api.query_config("usingTheme"))

    menuapi = api.get_mod_obj("menuapi").module
    editm: Menu = menuapi.get_menu("配置")

    theme_m = Menu(editm, tearoff=0)

    def on_change(*a):
        style.theme_use(var.get())
        api.set_config("usingTheme", var.get())

    var = StringVar(value=style.theme_use())
    var.trace_add("write", on_change)

    for x in style.theme_names():
        theme_m.add_radiobutton(label=x, value=x, variable=var)

    editm.insert_separator(3)
    editm.insert_cascade(4, menu=theme_m, label="窗口主题")

def init(api):
    top: Toplevel = api.get_var("top")
    return {"usingTheme": top.style.theme_use()}

def integrate(api):
    if api.has_mod("jehelps"):
        jehelps = api.get_mod_obj("jehelps").module
        jehelps.add_help(r"HKEY_SPINDLE\modConfigs\themes\usingTheme", "str 所使用的主题")