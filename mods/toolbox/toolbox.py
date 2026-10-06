from ttkbootstrap import Menu
from aglib import LoadAgFileName, SaveAgFileName, CreateAg, AgDir
from os.path import isfile

def main(api):
    menuapi = api.get_mod_obj("menuapi").module

    if isfile("toolbox.aglib"):
        lib = LoadAgFileName("toolbox.aglib")
    else:
        lib = CreateAg()
        SaveAgFileName(lib, "toolbox.aglib")

    menuapi.add_menu("工具", parse_toollib(api, lib))

def parse_toollib(api, lib: AgDir):
    menuapi = api.get_mod_obj("menuapi").module
    editor = api.load_submodule("editor.py", "editor")

    ...

    menu = Menu(menuapi.get_menubar(), tearoff=0)
    menu.add_separator()
    menu.add_command(label="编辑", command=lambda: editor.Editor(api, lib))
    return menu
