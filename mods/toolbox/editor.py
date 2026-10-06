from ttkbootstrap import Toplevel
from aglib import AgDir

class Editor(Toplevel):
    def __init__(self, api, lib: AgDir):
        parent = api.get_var("top")
        Toplevel.__init__(self, parent)
        api.create_window(self)
        
        self.menuapi = api.get_mod_obj("menuapi").module
        ...