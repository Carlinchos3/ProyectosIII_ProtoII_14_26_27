import unreal, json, os
P = unreal.Paths.project_dir()
out = {}
try:
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    a = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)[0]
    loc = a.get_actor_location()
    hit = unreal.SystemLibrary.line_trace_single(w, loc, loc - unreal.Vector(0,0,5000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [a], unreal.DrawDebugTrace.NONE, True)
    out["trace"] = str(hit.to_tuple()) if hit else "none"
    hit2 = unreal.SystemLibrary.line_trace_single(w, loc+unreal.Vector(0,0,50), loc - unreal.Vector(0,0,200), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
    out["trace2"] = str(hit2.to_tuple()) if hit2 else "none"
    ps = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.PlayerStart)
    out["starts"] = [str(p.get_actor_location()) for p in ps]
    gp = [c for c in a.get_components_by_class(unreal.ActorComponent) if c.get_name() == "GroundProbe"][0]
    try:
        out["probe"] = str(gp.call_method("Probe", (loc,)))
    except Exception as e: out["probe_err"] = str(e)
    cm = a.get_component_by_class(unreal.CharacterMovementComponent)
    out["move_mode"] = str(cm.get_editor_property("movement_mode")) if cm else None
    out["gravity"] = str(cm.get_editor_property("gravity_scale")) if cm else None
except Exception:
    import traceback; out["err"] = traceback.format_exc()
open(os.path.join(P, "Tools", "out_pie3.json"), "w").write(json.dumps(out, indent=1))
