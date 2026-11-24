import unreal, os, json, time
P = unreal.Paths.project_dir()
subs = list(unreal.ObjectIterator(unreal.EnhancedInputLocalPlayerSubsystem))
sub = subs[-1]
IP = "/Game/Stagger/Core/Input"
left = unreal.load_asset(f"{IP}/IA_LeftLeg"); step = unreal.load_asset(f"{IP}/IA_StepDirection")
right = unreal.load_asset(f"{IP}/IA_RightLeg")
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
ch = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)[0]
t0 = time.time(); log = {"start": str(ch.get_actor_location()), "samples": []}
# Secuencia: pierna izq + adelante 0.8s, soltar 0.4s, pierna dcha + adelante 0.8s, soltar 0.4s (x2)
plan = []
for i in range(2):
    plan += [(left, 0.8), (None, 0.4), (right, 0.8), (None, 0.4)]
ends = []; acc = 0
for a, d in plan:
    acc += d; ends.append((acc, a))
state = {"h": None}
def tick(dt):
    el = time.time() - t0
    cur = None; done = True
    for e, a in ends:
        if el < e: cur = a; done = False; break
    if done:
        unreal.unregister_slate_post_tick_callback(state["h"])
        log["end"] = str(ch.get_actor_location())
        open(os.path.join(P, "Tools", "out_inj5.json"), "w").write(json.dumps(log, indent=1))
        return
    if cur is not None:
        sub.inject_input_vector_for_action(cur, unreal.Vector(1, 0, 0), [], [])
        sub.inject_input_vector_for_action(step, unreal.Vector(0, 1, 0), [], [])
    if int(el * 4) != len(log["samples"]):
        log["samples"].append(str(ch.get_actor_location()))
state["h"] = unreal.register_slate_post_tick_callback(tick)
