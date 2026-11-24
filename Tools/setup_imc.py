import unreal, json, os, traceback
P = unreal.Paths.project_dir(); out = {"log": []}
IP = "/Game/Stagger/Core/Input"
try:
    ia = {n: unreal.load_asset(f"{IP}/{n}") for n in ["IA_LeftLeg","IA_RightLeg","IA_StepDirection","IA_Look","IA_ContextAction","IA_Pause"]}
    def key(name):
        k = unreal.Key(); k.set_editor_property("key_name", name); return k
    def build(imc, rows):
        maps = []
        for action, kname, mods in rows:
            m = unreal.EnhancedActionKeyMapping()
            m.set_editor_property("action", ia[action])
            m.set_editor_property("key", key(kname))
            objs = []
            for cls, props in mods:
                o = unreal.new_object(cls, outer=imc)
                for pk, pv in props.items(): o.set_editor_property(pk, pv)
                objs.append(o)
            m.set_editor_property("modifiers", objs)
            maps.append(m)
        dkm = imc.get_editor_property("default_key_mappings")
        dkm.set_editor_property("mappings", maps)
        imc.set_editor_property("default_key_mappings", dkm)
        res = imc.get_editor_property("default_key_mappings").get_editor_property("mappings")
        out["log"].append([imc.get_name(), [(m.get_editor_property("action").get_name(), m.get_editor_property("key").export_text(), len(m.get_editor_property("modifiers"))) for m in res]])
        unreal.EditorAssetLibrary.save_loaded_asset(imc)
    SW = (unreal.InputModifierSwizzleAxis, {}); NG = (unreal.InputModifierNegate, {})
    build(unreal.load_asset(f"{IP}/IMC_Keyboard"), [
        ("IA_LeftLeg", "Q", []), ("IA_LeftLeg", "LeftMouseButton", []),
        ("IA_RightLeg", "E", []), ("IA_RightLeg", "RightMouseButton", []),
        ("IA_StepDirection", "W", [SW]), ("IA_StepDirection", "S", [SW, NG]),
        ("IA_StepDirection", "A", [NG]), ("IA_StepDirection", "D", []),
        ("IA_Look", "Mouse2D", []), ("IA_ContextAction", "F", []), ("IA_Pause", "P", [])])
    build(unreal.load_asset(f"{IP}/IMC_Gamepad"), [
        ("IA_LeftLeg", "Gamepad_LeftTrigger", []), ("IA_RightLeg", "Gamepad_RightTrigger", []),
        ("IA_StepDirection", "Gamepad_Left2D", []),
        ("IA_Look", "Gamepad_Right2D", [(unreal.InputModifierScaleByDeltaTime, {}), (unreal.InputModifierScalar, {"scalar": unreal.Vector(60, 60, 1)})]),
        ("IA_ContextAction", "Gamepad_FaceButton_Bottom", []), ("IA_Pause", "Gamepad_Special_Right", [])])
except Exception: out["err"] = traceback.format_exc()
open(os.path.join(P, "Tools", "run_out.json"), "w").write(json.dumps(out, indent=1, default=str))
