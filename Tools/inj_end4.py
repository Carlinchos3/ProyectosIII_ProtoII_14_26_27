import os, unreal
P = unreal.Paths.project_dir()
open(os.path.join(P, "Tools", "inj_mode.txt"), "w").write("stop")
exec(open(os.path.join(P, "Tools", "inj4.py")).read())
