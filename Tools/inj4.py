import unreal, json, os, sys
P = unreal.Paths.project_dir(); out = {}
mode = os.environ.get("X", "")
try:
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    lp = pc.get_local_player() if hasattr(pc, "get_local_player") else None
    subs = list(unreal.ObjectIterator(unreal.EnhancedInputLocalPlayerSubsystem))
    out["subs"] = [s.get_path_name() for s in subs]
    sub = subs[-1]
    out["sub"] = str(sub)
    out["methods"] = [m for m in dir(sub) if "inject" in m.lower()]
    IP = "/Game/Stagger/Core/Input"
    left = unreal.load_asset(f"{IP}/IA_LeftLeg"); step = unreal.load_asset(f"{IP}/IA_StepDirection")
    act = open(os.path.join(P, "Tools", "inj_mode.txt")).read().strip()
    out["act"] = act
    out["sig"] = str(sub.start_continuous_input_injection_for_action.__doc__)[:600]
    if act == "start":
        EIL = unreal.EnhancedInputLibrary
        def V(x,y,t):
            try: return EIL.make_input_action_value_of_type(x, y, 0.0, t)
            except Exception: return EIL.make_input_action_value(unreal.Vector(x,y,0))
        sub.start_continuous_input_injection_for_action(left, V(1.0,0.0,unreal.InputActionValueType.BOOLEAN), [], [])
        sub.start_continuous_input_injection_for_action(step, V(0.0,1.0,unreal.InputActionValueType.AXIS2D), [], [])
    else:
        sub.stop_continuous_input_injection_for_action(left)
        sub.stop_continuous_input_injection_for_action(step)
    a = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)[0]
    out["loc"] = str(a.get_actor_location())
except Exception:
    import traceback; out["err"] = traceback.format_exc()
act = locals().get("act","x")
open(os.path.join(P, "Tools", "out_inj_"+act+".json"), "w").write(json.dumps(out, indent=1))
