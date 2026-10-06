from ttkbootstrap import Menu

_api = None

def main(api):
    global _api
    _api = api

# For other Mods
def get_menubar() -> Menu:
    return _api.get_var("menubar")

def get_menu(index) -> Menu:
    menu = get_menubar().entrycget(index, "menu")
    if isinstance(menu, str):
        return _api.get_var("tk").nametowidget(menu)
    else:
        return menu

def index_menu(label) -> int:
    return get_menubar().index(label)

def add_menu(label, menu):
    get_menubar().add_cascade(label=label, menu=menu)

def insert_menu(index, label, menu):
    get_menubar().insert_cascade(index, label=label, menu=menu)