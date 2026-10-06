from ttkbootstrap import StringVar
from tkinter import Label

helpdict = {
    r"HKEY_SYSTEM": "dir 存储有关系统设置的设置",
    r"HKEY_SYSTEM\aiRate": "int 语音合成的语速",
    r"HKEY_SYSTEM\aiVolume": "float 0~1，语音合成的音量",
    r"HKEY_SYSTEM\alpha": "float 0~1，控制窗口隐藏时的透明度",
    r"HKEY_SYSTEM\blackNames": "list 包含黑名单学号（整数）的列表",
    r"HKEY_SYSTEM\blackWeight": "int 黑名单权重",
    r"HKEY_SYSTEM\defaultTexture": "str 默认采用的贴图，必须为 HKEY_COMBINES 的数据名称之一",
    r"HKEY_SYSTEM\deltaY": "int 窗口纵向偏移（向下为正）",
    r"HKEY_SYSTEM\doTricks": "bool 控制是否启用恶搞功能",
    r"HKEY_SYSTEM\loadWinSize": "int 加载窗口的大小",
    r"HKEY_SYSTEM\max": "int 学号区间最大值",
    r"HKEY_SYSTEM\min": "int 学号区间最小值",
    r"HKEY_SYSTEM\pad": "int 窗口布局控件内边距",
    r"HKEY_SYSTEM\repeatTimes": "int 当其为 -1 时，必须手动点击窗口才能停止号码滚动；\n　　否则，号码滚动 repeatTimes 次后将自动停止",
    r"HKEY_SYSTEM\scale": "int 窗口缩放比例",
    r"HKEY_SYSTEM\voiceTipMark": "str 作为显示在有读音纠正的名字后面的标注",
    r"HKEY_SYSTEM\voicePrompt": "str 语音合成器朗读模版",
    r"HKEY_SYSTEM\whiteNames": "list 包含白名单学号（整数）的列表",

    r"HKEY_EDITOR": "dir 存储有关配置编辑器的设置",
    r"HKEY_EDITOR\editorWH": "list 编辑器窗口的宽度和高度，格式为 [width, height]",
    r"HKEY_EDITOR\dialogWH": "list 数值编辑对话框的宽度和高度",
    r"HKEY_EDITOR\defaultStr": "str 新建字符串时的默认值",
    r"HKEY_EDITOR\defaultInt": "int 新建整数时的默认值",
    r"HKEY_EDITOR\defaultFloat": "float 新建浮点数时的默认值",
    r"HKEY_EDITOR\defaultBool": "bool 新建布尔值时的默认值",
    r"HKEY_EDITOR\defaultOthr": "other 新建其他类型时的默认值",
    r"HKEY_EDITOR\editorFont": "str 编辑器使用的字体名称",
    r"HKEY_EDITOR\intIncrement": "int 整数输入框的步长",
    r"HKEY_EDITOR\floatIncrement": "float 浮点数输入框的步长",
    r"HKEY_EDITOR\spacing": "int 树形列表的行间距（像素）",
    r"HKEY_EDITOR\valueMin": "int 数值输入框的最小值",
    r"HKEY_EDITOR\valueMax": "int 数值输入框的最大值",
    r"HKEY_EDITOR\treeColorOdd": "str 树形列表奇数行的背景颜色（颜色代码）",
    r"HKEY_EDITOR\treeColorEven": "str 树形列表偶数行的背景颜色（颜色代码）",

    r"HKEY_SPINDLE": "dir 存储有关 Spindle Loader 以及模组的设置",
    r"HKEY_SPINDLE\iconSize": "int 菜单栏中 Mod 图标显示大小（像素）",
    r"HKEY_SPINDLE\iconRadius": "int 菜单栏中 Mod 图标圆角半径（像素）",
    r"HKEY_SPINDLE\descIconSize": "int 描述窗口中 Mod 图标大小（像素）",
    r"HKEY_SPINDLE\descWrapLen": "int Mod 描述文本的换行宽度（像素）",
    r"HKEY_SPINDLE\modConfigs": "dir 各个 Mod 的配置",

    r"HKEY_ASSETS": "dir 存储资源文件",
    r"HKEY_ASSETS\textures": "dir 贴图文件",
    r"HKEY_ASSETS\icons": "dir 窗口图标文件",
    r"HKEY_ASSETS\icons\loading_on.png": "bytes 加载窗口进度条亮起图层",
    r"HKEY_ASSETS\icons\loading_off.png": "bytes 加载窗口进度条熄灭图层",
    r"HKEY_ASSETS\icons\win_icon.png": "bytes 原版 Spinner 窗口图标",
    r"HKEY_ASSETS\icons\win_icon_modded.png": "bytes 有 Spindle Loader 加载模组的窗口图标",
    r"HKEY_ASSETS\icons\type_NoneType.png": "bytes 编辑器空值的图标",
    r"HKEY_ASSETS\icons\type_bool.png": "bytes 编辑器真/假类型的图标",
    r"HKEY_ASSETS\icons\type_bytes.png": "bytes 编辑器字节码类型的图标",
    r"HKEY_ASSETS\icons\type_dir.png": "bytes 编辑器数据夹的图标",
    r"HKEY_ASSETS\icons\type_float.png": "bytes 编辑器小数类型的图标",
    r"HKEY_ASSETS\icons\type_int.png": "bytes 编辑器整数类型的图标",
    r"HKEY_ASSETS\icons\type_list.png": "bytes 编辑器列表类型的图标",
    r"HKEY_ASSETS\icons\type_other.png": "bytes 编辑器其他类型的图标",
    r"HKEY_ASSETS\icons\type_str.png": "bytes 编辑器字符串类型的图标",

    r"HKEY_NUM_DATA": "dir 控制主窗口数字的显示方式",

    r"HKEY_COMBINES": "dir 存储贴图组合",

    r"HKEY_NAMES": "dir 存储学号与对应的名字",

    r"HKEY_VOICE_TIP": "dir 存储语音合成器读音错误的名字对应学号与正确读音"
}

def main(api):
    EdWinCls = api.get_var("EditWindow")
    TYPENAMES = api.get_var("TYPENAMES").copy()
    TYPENAMES["dir"] = "数据夹"
    TYPENAMES["other"] = "非特殊类型"

    class HelpedEditWindow(EdWinCls):
        def __init__(self, lib):
            EdWinCls.__init__(self, lib)
            self.tip_var = StringVar()
            PAD = api.get_var("PAD")
            self.lab = Label(
                self.tv,
                textvariable=self.tip_var,
                font=api.get_var("EDITORFONT"),
                **PAD
            )
            self.lab.bind("<Map>", self._map_lab)

            self.tv.bind("<Motion>", self.tip_ud)
            self.lab.bind("<Motion>", self.on_lab_mot)
            self.tv["yscrollcommand"] = lambda *a, **kw: (self.vbar.set(*a, **kw), self.tip_ud(None))
            self.vbar["command"] = lambda *a, **kw: (self.tv.yview(*a, **kw), self.hide_tip())
            self.tv.bind("<Leave>", self.on_leave)
            self._prev_evt = None

        def on_leave(self, evt):
            if (
                evt.x < 0 or evt.x > self.tv.winfo_width() or \
                evt.y < 0 or evt.y > self.tv.winfo_height()
            ):
                self.hide_tip(evt)

        def on_lab_mot(self, evt):
            class A: pass
            e2 = A()
            e2.x = self.lab_topleft_x - self.tv.winfo_x()
            e2.y = self.lab_topleft_y - self.tv.winfo_y()
            self.tip_ud(e2)

        def _map_lab(self, evt=None):
            self.lab.config(
                background="#fff58b",
                borderwidth=1,
                relief="groove",
                justify="left")

        def goto(self, path):
            EdWinCls.goto(self, path)
            if hasattr(self, "lab"):
                self.tip_ud(None)
        
        def gethelp(self, y):
            path = self.tv.identify_row(y)
            if path:
                for k, v in helpdict.items():
                    if k == path:
                        typ, tip = v.split(" ", 1)
                        return f"（{TYPENAMES[typ]}）{path}:\n　　{tip}"
                else:
                    return "无可用帮助"
            else:
                return ""

        def tip_ud(self, evt):
            self._prev_evt = evt = (evt or self._prev_evt)
            if evt is None:
                return
            hp = self.gethelp(evt.y)
            if hp:
                self.tip_var.set(hp)
                rw, rh = self.lab.winfo_reqwidth(), self.lab.winfo_reqheight()
                mw = self.tv.winfo_width()
                x, y = evt.x, evt.y
                y_offset = -5

                vert_anch = "s"

                if x + rw > mw:
                    x = mw - rw
                if y - rh < 0:
                    vert_anch = "n"
                    y_offset *= -1
                    self.lab_topleft_y = y + y_offset - rh
                else:
                    self.lab_topleft_y = y + y_offset

                self.lab_topleft_x = x
                self.lab.place(x=x, y=y + y_offset, anchor=f"{vert_anch}w")
            else:
                self.hide_tip()

        def hide_tip(self, evt=None):
            self.lab.place_forget()
            
    api.set_var("EditWindow", HelpedEditWindow)

# For other mods
def add_help(key, value):
    helpdict[key] = value

def integrate(api):
    for modobj in api.get_var("ALL_MODS"):
        add_help(f"HKEY_SPINDLE\\modConfigs\\{modobj.modid}", f"dir {modobj.name} 模组的配置")