import unreal, json, os
P = unreal.Paths.project_dir()
out = {}
try:
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    out["world"] = str(w)
    acts = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)
    for a in acts:
        d = {"class": a.get_class().get_name(), "loc": str(a.get_actor_location())}
        for c in a.get_components_by_class(unreal.ActorComponent):
            n = c.get_name(); cd = {}
            for prop in ["LeftLeg","RightLeg","InputSource","GroundProbe","FootIK","Pelvis","bReady","CenterOfMass","FacingYaw","ThighLength","CalfLength","AnkleHeight","Mesh","Lockers"]:
                try: cd[prop] = str(c.get_editor_property(prop))
                except Exception: pass
            for leg in ["LeftLeg","RightLeg"]:
                try:
                    L = c.get_editor_property(leg)
                    if L:
                        cd[leg+"_d"] = {k: str(L.get_editor_property(k)) for k in ["FootPosition","State","bGroundHit","HipPosition","KneePosition","AnklePosition","Side"]}
                except Exception as e: cd[leg+"_err"] = str(e)
            if cd: d[n] = cd
        d["controller"] = str(a.get_controller())
        out[a.get_name()] = d
except Exception as e:
    import traceback; out["err"] = traceback.format_exc()
open(os.path.join(P, "Tools", "out_pie1.json"), "w").write(json.dumps(out, indent=1))
