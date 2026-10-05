_glb = None

def spInitialized() -> bool:
    return _glb != None

def spGetGlobalVar(name: str):
    return _glb[name]

def spSetGlobalVar(name: str, val):
    _glb[name] = val

def spVersionStr() -> str:
    return spGetGlobalVar("VERSION")

def spVersionInt() -> int:
    return spGetGlobalVar("VER_ID")

def spRequireMain(*ver_id: int):
    assert spVersionInt() in ver_id or not ver_id, "模组不支持当前Spinner版本，需要" + " ".join(ver_id)

def spCreateWindow():
    return spGetGlobalVar("FocusToplevel")()

def spGetConfigObj():
    return spGetGlobalVar("cnflib")

def spQuit():
    spGetGlobalVar("tk").destroy()

def spRestart():
    spGetGlobalVar("restart")()

def SwitchWinCase():
    spGetGlobalVar("winclose")()

def spAddCommand(label: str, func):
    spGetGlobalVar("modmenu").add_command(label=label, command=func)

def spAddCascade(label: str, menu):
    spGetGlobalVar("modmenu").add_cascade(label=label, menu=menu)

def spRequireMod(name, *vers):
    mods = spGetGlobalVar("mods")
    while True:
        if name in mods.keys():
            if vers:
                if mods[name] in vers:
                    return
                else:
                    raise Exception(f"模组版本不匹配，需要{name} {' '.join(vers)}")
            elif "all_mods_loaded" in _glb.keys():
                raise Exception(f"模组不存在，需要{name} {' '.join(vers)}")