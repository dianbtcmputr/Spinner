from io import BytesIO
from aglib import AgDir, LoadAgFileName
from PIL import ImageTk, Image

TYPENAMES = {
    "str": "字符串",
    "int": "整数",
    "float": "小数",
    "bool": "真/假",
    "NoneType": "空值",
    "list": "列表",
    "bytes": "字节码"}

def gettypename(dat) -> str:
    return TYPENAMES.get(type(dat).__name__, "其他")

cnflib = LoadAgFileName("config.aglib")

assetslib = cnflib.GetSubDirCopy("HKEY_ASSETS")
texlib = assetslib.GetSubDirCopy("textures")
iconlib = assetslib.GetSubDirCopy("icons")

def loadpimg(lib: AgDir, name, size: int):
    return ImageTk.PhotoImage(
        Image.open(BytesIO(lib.QueryValue(name)))\
        .crop((0, 0, 16, 16)).resize((size, size), resample=Image.Resampling.NEAREST)
        )

SYSCNF = cnflib.GetSubDirCopy("HKEY_SYSTEM")
NUMDAT = cnflib.GetSubDirCopy("HKEY_NUM_DATA")
COMBINES = cnflib.GetSubDirCopy("HKEY_COMBINES")
NAMEDICT = cnflib.GetSubDirCopy("HKEY_NAMES")
VOICETIP = cnflib.GetSubDirCopy("HKEY_VOICE_TIP")
EDTRLIB = cnflib.GetSubDirCopy("HKEY_EDITOR")
SPINDLE = cnflib.GetSubDirCopy("HKEY_SPINDLE")

SCALE = SYSCNF.QueryValue("scale")
MEMBERS = list(range(SYSCNF.QueryValue("min"), SYSCNF.QueryValue("max") + 1))
MEMBERS.extend(SYSCNF.QueryValue("blackNames") * SYSCNF.QueryValue("blackWeight"))

for x in SYSCNF.QueryValue("whiteNames"):
    MEMBERS.remove(x)

PAD = SYSCNF.QueryValue("pad")
WW, WH = int(256 * SCALE), int(208 * SCALE)

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
SPACING = EDTRLIB.QueryValue("spacing")
VALUEMIN = EDTRLIB.QueryValue("valueMin")
VALUEMAX = EDTRLIB.QueryValue("valueMax")
TREECOLORODD = EDTRLIB.QueryValue("treeColorOdd")
TREECOLOREVEN = EDTRLIB.QueryValue("treeColorEven")

MODICONSIZE = SPINDLE.QueryValue("iconSize")
MODICONRADIUS = SPINDLE.QueryValue("iconRadius")
MODDESCICONSIZE = SPINDLE.QueryValue("descIconSize")
MODDESCWRAPLEN = SPINDLE.QueryValue("descWrapLen")

NARRDISAPPEAR = 3
NARRDELTAY = 50
NARRMAX = 4

"""class Narration(Toplevel):
    def __init__(self, info:str):
        Toplevel.__init__(self, top)
        self.transient(top)
        self.overrideredirect(1)
        self.birth = time()
        self.info=info
        self.config(bg="black")
        lb = Label(self, text=info, background="black", foreground="white")
        lb.pack()
        self.geometry("+10000+10000")
        self.width, self.height = lb.winfo_reqwidth(), lb.winfo_reqheight()

narrations = []
def narrupdate():
    if len(narrations) == 0:
        tk.after(10, narrupdate)
        return
    thew = max([n.width for n in narrations])
    theh = NARRDELTAY
    for nar in narrations[:]:
        alpha = 1 - (time() - nar.birth) / NARRDISAPPEAR
        if alpha < 0.001:
            narrations.remove(nar)
            nar.destroy()
        else:
            nar.attributes("-alpha", alpha)
    for nar in narrations:
        nar.geometry(f"{thew}x{nar.height}-0-{theh}")
        theh += nar.height
    tk.after(10, narrupdate)

def narradd(info: str):
    nar = Narration(info)
    #while nar in narrations:
    #    narrations.remove(nar)
    narrations.insert(0, nar)
    #if len(narrations) >= NARRMAX:
    #    narrations.pop(-1).destroy()
    """
