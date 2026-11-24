import ctypes, os, unreal
from ctypes import wintypes
u = ctypes.windll.user32; k = ctypes.windll.kernel32
u.GetClipboardData.restype = ctypes.c_void_p
k.GlobalLock.restype = ctypes.c_void_p
k.GlobalLock.argtypes = [ctypes.c_void_p]
k.GlobalUnlock.argtypes = [ctypes.c_void_p]
u.OpenClipboard(0)
h = u.GetClipboardData(13)
p = k.GlobalLock(h)
txt = ctypes.wstring_at(p)
k.GlobalUnlock(h)
u.CloseClipboard()
open(os.path.join(unreal.Paths.project_dir(), "Tools", "out_clip.txt"), "w", encoding="utf-8").write(txt)
