import unreal, json, os, sys
P = unreal.Paths.project_dir(); out = {}
mode = os.environ.get("X", "")
try:
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    lp = pc.get_local_player() if hasattr(pc, "get_local_player") else None
    sub = unreal.SubsystemBlueprintLibrary.get_local_player_subsystem(pc, unreal.EnhancedInputLocalPlayerSubsystem)
    out["sub"] = str(sub)
    out["methods"] = [m for m in dir(sub) if "inject" in m.lower()]
    IP = "/Game/Stagger/Core/Input"
    left = unreal.load_asset(f"{IP}/IA_LeftLeg"); step = unreal.load_asset(f"{IP}/IA_StepDirection")
    act = open(os.path.join(P, "Tools", "inj_mode.txt")).read().strip()
    out["act"] = act
    if act == "start":
        sub.start_continuous_input_injection_for_action(left, unreal.Vector(1, 0, 0), [], [])
        sub.start_continuous_input_injection_for_action(step, unreal.Vector(0, 1, 0), [], [])
    else:
        sub.stop_continuous_input_injection_for_action(left)
        sub.stop_continuous_input_injection_for_action(step)
    a = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)[0]
    out["loc"] = str(a.get_actor_location())
except Exception:
    import traceback; out["err"] = traceback.format_exc()
open(os.path.join(P, "Tools", "out_inj.json"), "w").write(json.dumps(out, indent=1))
