import unreal, json, os
P = unreal.Paths.project_dir()
L = json.load(open(os.path.join(P, "Tools", "funcs.json")))
bad = []
for c, f in L:
    o = unreal.find_object(None, f"{c}:{f}")
    if o is None:
        try:
            unreal.load_object(None, c)
            o = unreal.find_object(None, f"{c}:{f}")
        except Exception: pass
    if o is None: bad.append([c, f])
open(os.path.join(P, "Tools", "out_chkfn.json"), "w").write(json.dumps({"n": len(L), "bad": bad}, indent=1))
