import unreal, json, os
P = unreal.Paths.project_dir()
out = {"bel": dir(unreal.BlueprintEditorLibrary)}
bp = unreal.load_asset("/Game/Stagger/Player/Movement/BPC_RaycastGroundProbe")
try:
    out["iface"] = str(bp.get_editor_property("implemented_interfaces"))
except Exception as e: out["iface_err"] = str(e)
out["bpprops"] = [m for m in dir(bp) if "interface" in m.lower()]
open(os.path.join(P, "Tools", "out_q1.json"), "w").write(json.dumps(out, indent=1))
