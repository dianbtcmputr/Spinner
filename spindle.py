# Spinner mod loader
from io import BytesIO
from json import loads
from os import listdir, rename
from tkinter import NSEW, NW
from types import ModuleType
from zipfile import ZipFile
from os.path import exists, isfile, join, sep
from weakref import ref
from PIL import Image, ImageTk, ImageDraw
from ttkbootstrap import BooleanVar, Checkbutton, Frame, Label, Toplevel
from aglib import AgDir, SaveAgFileName

var_getter = None
var_setter = None

def load_module(code_str: str, name: str):
    module = ModuleType(name)

    module.__builtins__ = __builtins__
    module.__name__ = name
    module.__file__ = f"<spindle.mod.{name}>"

    compiled_code = compile(code_str, filename=module.__file__, mode='exec')
    exec(compiled_code, module.__dict__)
    
    return module

"""模组结构：
zip文件 or 文件夹
    spindle.json
    icon.png
    xxx 其他内容

spindle.json:
    {
    "displayName": str,
    "modId": str,
    "dependencies": list[str] = [], # 元素为 modId
    "version": str,
    "mainFile": str,
    "mainEntry": str, # mainFile中的主函数名。
    "description": str = "",
    "mainInit": str = "", # mainFile中的初始化函数名。先于主函数运行，且仅在首次加载mod时触发
    "mainIntegrate": str = "" # mainFile中的联动函数名，在所有mod都加载并运行主函数后，按模组加载顺序运行
    }"""

class SpindleAPI:
    def __init__(self, mod: "ModObj"):
        self._mod = ref(mod)
        self._currid = -1

    def _nextid(self):
        self._currid += 1
        return f"file_{self._currid}"

    def load_submodule(self, path: str, subname=None):
        return load_module(self._mod().readstr(path), f"{self._mod().name}.{subname or self._nextid()}")

    def get_var(self, name):
        return var_getter(name)

    def set_var(self, name, val):
        var_setter(name, val)

    def query_config(self, path):
        return var_getter("SPINDLE").QueryValue(f"modConfigs\\{self._mod().modid}\\{path}")

    def set_config(self, path, val):
        lib = var_getter("cnflib")
        lib.SetValue(f"HKEY_SPINDLE\\modConfigs\\{self._mod().modid}\\{path}", val)
        SaveAgFileName(lib, "config.aglib")

    def load_file(self, path):
        return self._mod().readbytes(path)

    def has_mod(self, modid):
        for mod in ALL_MODS:
            if mod.modid == modid:
                return True
        return False

    def get_mod_obj(self, modid):
        for mod in ALL_MODS:
            if mod.modid == modid:
                return mod

    def create_window(self, existing_win: Toplevel | None = None):
        par: Toplevel = var_getter("top")
        top = existing_win or Toplevel(par)
        top.title(self._mod().name)
        top.geometry(f"+{par.winfo_x()}+{par.winfo_y()}")
        top.transient(par)
        top.focus_set()
        return top

mod_has_made_cnf = False

class ModObj:
    def __init__(self, modname: str):
        self.modfn = modname
        if isfile(join("mods", modname)):
            self.typ = 0
            self.zip = ZipFile(join("mods", modname))
        else:
            self.typ = 1
        self.fp = join("mods", modname)

        self.jsdata: dict = loads(self.readstr("spindle.json"))

        self.name: str = self.jsdata["displayName"]
        self.modid: str = self.jsdata["modId"]

        self.iimg = self.load_icon()
        self.icon = ImageTk.PhotoImage(self.iimg)

        self.api = SpindleAPI(self)

        self.mainfile = self.readstr(self.jsdata["mainFile"])
        self.mainety: str = self.jsdata["mainEntry"]
        self.version: str = self.jsdata["version"]

        self.dependencies: list[str] = self.jsdata.get("dependencies", [])
        self.desc: str = self.jsdata.get("description", "")
        self.initfunc: str = self.jsdata.get("mainInit", "")
        self.integfunc: str = self.jsdata.get("mainIntegrate", "")
        self.module = None

        self.checkbtn = int

    def load_icon(self):
        icon_size = var_getter("MODICONSIZE")
        radius = var_getter("MODICONRADIUS")
    
        self.orig_icon = img = Image.open(BytesIO(self.readbytes("icon.png")))
        w, h = img.size
        if w >= h:
            new_w = icon_size
            new_h = int(h * (icon_size / w))
        else:
            new_h = icon_size
            new_w = int(w * (icon_size / h))
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
        if img_resized.mode != 'RGBA':
            img_resized = img_resized.convert('RGBA')
    
        if radius > 0:
            mask = Image.new("L", (new_w, new_h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, new_w, new_h), radius=radius, fill=255)
            img_resized.putalpha(mask)
    
        canvas = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
        x_offset = (icon_size - new_w) // 2
        y_offset = (icon_size - new_h) // 2
        canvas.paste(img_resized, (x_offset, y_offset), img_resized)
    
        return canvas

    def readstr(self, fn: str):
        if self.typ:
            with open(join(self.fp, fn.replace("/", sep)), "r", encoding="utf-8") as f:
                return f.read()
        else:
            return self.zip.read(fn).decode("utf-8")

    def readbytes(self, fn: str):
        if self.typ:
            with open(join(self.fp, fn.replace("/", sep)), "rb") as f:
                return f.read()
        else:
            return self.zip.read(fn)

    def load(self):
        """Load, ignoring dependencies."""
        global mod_has_made_cnf
        self.module = load_module(self.mainfile, self.modid)

        if self.initfunc:
            lib: AgDir = var_getter("cnflib")
            dirn = f"HKEY_SPINDLE\\modConfigs\\{self.modid}"
            if lib.IsDir(dirn):
                pass
            else:
                lib.MkDir(dirn)
                subdir: dict = getattr(self.module, self.initfunc)(self.api)
                for k ,v in subdir.items():
                    lib.SetValue(f"{dirn}\\{k}", v)
                mod_has_made_cnf = True

        getattr(self.module, self.mainety)(self.api)

        if self.initfunc:
            lib: AgDir = var_getter("cnflib")
            dirn = f"HKEY_SPINDLE\\modConfigs\\{self.modid}"
            if lib.IsDir(dirn):
                pass
            else:
                lib.MkDir(dirn)
                subdir: dict = getattr(self.module, self.initfunc)(self.api)
                for k ,v in subdir.items():
                    lib.SetValue(f"{dirn}\\{k}", v)
                mod_has_made_cnf = True

    def is_depen_ok(self, mods: "list[ModObj]"):
        dep = self.dependencies.copy()
        for m in mods:
            if m.module is not None and m.modid in dep:
                dep.remove(m.modid)
        return len(dep) == 0

    def get_status(self):
        """Enable: True"""
        return exists(self.fp.removesuffix(".disabled"))

    def status_toggle(self):
        old_status = self.get_status()
        base = self.fp.removesuffix(".disabled")
        if old_status:
            rename(base, base + ".disabled")
            self.disable_bedepens()
        else:
            rename(base + ".disabled", base)
            self.enable_depens()

        if self.checkbtn():
            self.checkbtn().refresh()

    def disable_bedepens(self):
        for modobj in INCLUSIVE_ALL_MODS:
            if self.modid in modobj.dependencies:
                if modobj.get_status():
                    modobj.status_toggle()

    def enable_depens(self):
        for modobj in INCLUSIVE_ALL_MODS:
            if modobj.modid in self.dependencies:
                if not modobj.get_status():
                    modobj.status_toggle()

class ModDescDlg(Toplevel):
    def __init__(self, parent: Toplevel, modobj: ModObj):
        Toplevel.__init__(self, parent)
        self.modobj = modobj
        self.geometry(f"+{parent.winfo_x()}+{parent.winfo_y()}")
        self.transient(parent)
        self.title(f"Spindle Loader - {modobj.name}")
        self.focus_set()

        SIZE = var_getter("MODDESCICONSIZE")
        PAD = var_getter("PAD")
        self.resized_img = modobj.orig_icon.resize((SIZE, SIZE), resample=Image.Resampling.LANCZOS)
        self.pimg = ImageTk.PhotoImage(self.resized_img)

        infof = Frame(self)
        Label(infof, image=self.pimg).grid(row=0, column=0, rowspan=3, sticky=NSEW, **PAD)
        Label(infof, text=f"{modobj.name} - {modobj.version}").grid(row=0, column=1, sticky=NW, **PAD)
        infof.pack(anchor="w")
        
        deps = self.get_modlist(modobj.dependencies, 4)
        if deps:
            Label(infof, text=f"支持库：{deps}").grid(row=1, column=1, sticky=NW, pady=(0, PAD["pady"]), padx=PAD["padx"])
        else:
            Label(infof, text=f"（无支持库）").grid(row=1, column=1, sticky=NW, pady=(0, PAD["pady"]), padx=PAD["padx"])

        Frame(infof).grid(row=1, column=2, sticky=NSEW)
        infof.grid_rowconfigure(2, weight=1)

        Label(
            self, text=modobj.desc or "模组作者什么也没写...",
            justify="left", wraplength=var_getter("MODDESCWRAPLEN")
        ).pack(fill="both", expand=1, pady=(0, PAD["pady"]), padx=PAD["padx"])
        self.resizable(0, 0)

    def get_modlist(self, mlist, k):
        res = []
        for mid in mlist:
            for mod in ALL_MODS:
                if mod.modid == mid:
                    res.append(mod.name)
        return ("\n" + k * "　").join(res)

ALL_MODS: list[ModObj] = []
INCLUSIVE_ALL_MODS: list[ModObj] = [] # 不论是否加载

def load_all_mods():
    for modf in listdir("mods"):
        modobj = ModObj(modf)
        if modobj.modid in (x.modid for x in ALL_MODS):
            raise Exception(f"出现重复的 Mod ID: {modobj.modid}")
        else:
            if not modobj.modfn.endswith(".disabled"):
                ALL_MODS.append(modobj)
            INCLUSIVE_ALL_MODS.append(modobj)

    def _recurser(recurse: int = 0):
        for m in ALL_MODS:
            if m.module is None and m.is_depen_ok(ALL_MODS):
                m.load()

        if all((x.module is not None) for x in ALL_MODS):
            return
        elif recurse > len(ALL_MODS):
            raise Exception("模组存在循环依赖，或依赖库缺失")
        else:
            _recurser(recurse + 1)

    _recurser()
    return ALL_MODS

def call_integrates():
    for modobj in ALL_MODS:
        if modobj.integfunc:
            getattr(modobj.module, modobj.integfunc)(modobj.api)

class ModCheckBtn(Checkbutton):
    def __init__(self, parent, modobj: ModObj):
        self.modobj = modobj
        self.var = BooleanVar(value=self.get_status())
        Checkbutton.__init__(
            self, parent,
            text=modobj.name,
            compound="left",
            image=modobj.icon,
            variable=self.var,
            onvalue=True,
            offvalue=False,
            command=self.on_click
        )
        self.modobj.checkbtn = ref(self)

    def on_click(self, *a):
        self.modobj.status_toggle()

    def get_status(self):
        return self.modobj.get_status()

    def refresh(self):
        self.var.set(self.get_status())

class DisableMgr(Toplevel):
    def __init__(self):
        par: Toplevel = var_getter("top")
        Toplevel.__init__(self, par)
        self.geometry(f"+{par.winfo_x()}+{par.winfo_y()}")
        self.title("Spindle Loader")
        self.transient(par)
        self.focus_set()
        PAD = var_getter("PAD")
        Label(self, text="取消勾选以禁用模组").pack(**PAD)
        for modobj in INCLUSIVE_ALL_MODS:
            ModCheckBtn(self, modobj).pack(**PAD, anchor="w")
