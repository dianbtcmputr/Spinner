from sorge import *
print("HELLO")

def show():
    w = spCreateWindow()
    w.transient(spGetGlobalVar("top"))


spAddCommand("示例模组", show)