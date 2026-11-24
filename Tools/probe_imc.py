import unreal, json, os, traceback
P = unreal.Paths.project_dir(); out = {}
try:
    imc = unreal.load_asset("/Game/Stagger/Core/Input/IMC_Keyboard")
    d = imc.get_editor_property("default_key_mappings")
    out["dkm_type"] = str(type(d))
    out["dkm_dir"] = [n for n in dir(d) if not n.startswith("_")]
    try:
        m = d.get_editor_property("mappings"); out["dkm_mappings"] = len(m)
        if len(m): out["m0"] = [n for n in dir(m[0]) if not n.startswith("_")]; out["m0_key"] = str(m[0].get_editor_property("key"))
    except Exception as e: out["dkm_err"] = str(e)
    out["map_key_doc"] = imc.map_key.__doc__
except Exception: out["err"] = traceback.format_exc()
open(os.path.join(P, "Tools", "run_out.json"), "w").write(json.dumps(out, indent=1, default=str))
