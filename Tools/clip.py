# Copia Tools/clips/<nombre>.txt al portapapeles de Windows.  Uso: py ".../Tools/clip.py" nombre
import sys, os, ctypes, unreal
name = sys.argv[1] if len(sys.argv) > 1 else "clip"
path = os.path.join(unreal.Paths.project_dir(), "Tools", "clips", name + ".txt")
text = open(path, "r", encoding="utf-8", newline="").read()
u, k = ctypes.windll.user32, ctypes.windll.kernel32
k.GlobalAlloc.restype = ctypes.c_void_p; k.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
k.GlobalLock.restype = ctypes.c_void_p; k.GlobalLock.argtypes = [ctypes.c_void_p]
k.GlobalUnlock.argtypes = [ctypes.c_void_p]
u.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]; u.SetClipboardData.restype = ctypes.c_void_p
data = text.encode("utf-16-le") + b"\0\0"
h = k.GlobalAlloc(0x0002, len(data)); p = k.GlobalLock(h); ctypes.memmove(p, data, len(data)); k.GlobalUnlock(h)
u.OpenClipboard(0); u.EmptyClipboard(); u.SetClipboardData(13, h); u.CloseClipboard()
print("CLIP", name, len(text))
