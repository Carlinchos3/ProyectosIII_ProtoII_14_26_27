import os, unreal
P = unreal.Paths.project_dir()
open(os.path.join(P, "Tools", "inj_mode.txt"), "w").write("start")
exec(open(os.path.join(P, "Tools", "inj.py")).read())
