import sys
from ttkbootstrap import Toplevel, Button, Text
from tkinter import END

class Outputer:
    top = None

    def __init__(self, api):
        self.window = None
        self.text = None
        self.api = api

    def write(self, msg):
        sys.__stdout__.write(msg)
        if self.window is None or not self.window.winfo_exists():
            self.window = self.api.create_window()
            self.window.update()
            self.window.update_idletasks()
            self.window.focus_set()

            self.text = Text(self.window, wrap='word', height=15, width=75)
            self.text.pack(fill='both', expand=True)

            btn = Button(self.window, text="关闭", command=self.close_window)
            btn.pack(pady=5)

            self.window.protocol("WM_DELETE_WINDOW", self.close_window)

            self.text.insert(END, "错误信息捕获：\n\n")

        self.text.insert(END, msg)
        self.text.see("0.0")

    def close_window(self):
        if self.window:
            self.window.destroy()
            self.window = None
            self.text = None

    def flush(self):
        sys.__stdout__.flush()

def main(api):
    Outputer.top = api.get_var("top")
    sys.stderr = Outputer(api)
