# Fase B: clases Blueprint de 5a con variables y componentes (la lógica se pega después).
import unreal, json, os, traceback
P = unreal.Paths.project_dir(); out = {"log": []}
def log(*a): out["log"].append(" ".join(str(x) for x in a))
AT = unreal.AssetToolsHelpers.get_asset_tools(); EAL = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary
R = "/Game/Stagger"
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); SDL = unreal.SubobjectDataBlueprintFunctionLibrary

def make_bp(name, path, parent):
    full = f"{path}/{name}"
    if EAL.does_asset_exist(full):
        return unreal.load_asset(full)
    f = unreal.BlueprintFactory(); f.set_editor_property("parent_class", parent)
    bp = AT.create_asset(name, path, unreal.Blueprint, f); log("creado", full); return bp

REAL = BEL.get_basic_type_by_name("real"); BOOL = BEL.get_basic_type_by_name("bool"); NAME = BEL.get_basic_type_by_name("name")
VEC = BEL.get_struct_type(unreal.Vector.static_struct()); ROT = BEL.get_struct_type(unreal.Rotator.static_struct())
XF = BEL.get_struct_type(unreal.Transform.static_struct())
def OBJ(cls): return BEL.get_object_reference_type(cls)

def add_vars(bp, specs, editable=()):
    for n, t in specs:
        BEL.add_member_variable(bp, n, t)
        if n in editable: BEL.set_blueprint_variable_instance_editable(bp, n, True)

def defaults(bp, vals):
    BEL.compile_blueprint(bp)
    cdo = unreal.get_default_object(bp.generated_class())
    for k, v in vals.items():
        try: cdo.set_editor_property(k, v)
        except Exception as e: log("default", bp.get_name(), k, e)

try:
    MV = f"{R}/Player/Movement"; AN = f"{R}/Player/Animation"
    leg = make_bp("BP_Leg", MV, unreal.Object)
    add_vars(leg, [("FootPosition", VEC), ("bGroundHit", BOOL), ("GroundPoint", VEC), ("GroundNormal", VEC),
                   ("GroundFriction", REAL), ("GroundProvider", OBJ(unreal.Object.static_class())), ("HipPosition", VEC),
                   ("KneePosition", VEC), ("AnklePosition", VEC), ("Velocity", VEC), ("LastPlantPosition", VEC)])
    defaults(leg, {"GroundNormal": unreal.Vector(0, 0, 1), "GroundFriction": 1.0})
    leg_cls = leg.generated_class()

    pel = make_bp("BPC_PelvisMover", MV, unreal.ActorComponent)
    add_vars(pel, [("ThighLength", REAL), ("CalfLength", REAL), ("AnkleHeight", REAL), ("HipOffsetLeft", VEC), ("HipOffsetRight", VEC),
                   ("CenterOfMass", VEC), ("FacingYaw", REAL), ("TargetYaw", REAL)])
    defaults(pel, {"ThighLength": 45.0, "CalfLength": 45.0, "AnkleHeight": 9.0,
                   "HipOffsetLeft": unreal.Vector(0, -10, -3), "HipOffsetRight": unreal.Vector(0, 10, -3)})

    prb = make_bp("BPC_RaycastGroundProbe", MV, unreal.ActorComponent)
    add_vars(prb, [("TraceUp", REAL), ("TraceDown", REAL)], editable=("TraceUp", "TraceDown"))
    defaults(prb, {"TraceUp": 50.0, "TraceDown": 200.0})

    iks = make_bp("BPC_FootIKSolver", MV, unreal.ActorComponent)
    add_vars(iks, [("ThighLength", REAL), ("CalfLength", REAL), ("AnkleHeight", REAL), ("KneeOutward", REAL)], editable=("KneeOutward",))
    defaults(iks, {"ThighLength": 45.0, "CalfLength": 45.0, "AnkleHeight": 9.0, "KneeOutward": 0.15})

    cfg = unreal.load_asset(f"{R}/Core/Config/PDA_StepConfig"); da = unreal.load_asset(f"{R}/Core/Config/DA_StepConfig")
    lc = make_bp("BPC_LegController", MV, unreal.ActorComponent)
    add_vars(lc, [("LeftLeg", OBJ(leg_cls)), ("RightLeg", OBJ(leg_cls)), ("InputSource", OBJ(unreal.Object.static_class())),
                  ("GroundProbe", OBJ(unreal.Object.static_class())), ("FootIK", OBJ(unreal.Object.static_class())),
                  ("Pelvis", OBJ(pel.generated_class())), ("StepConfig", OBJ(cfg.generated_class())),
                  ("Lockers", BEL.get_array_type(OBJ(unreal.Object.static_class()))), ("bDrawDebug", BOOL)],
             editable=("StepConfig", "bDrawDebug"))
    defaults(lc, {"StepConfig": da})

    an = make_bp("BPC_PlayerAnimatorBridge", AN, unreal.ActorComponent)
    names = [("PelvisBone", "pelvis"), ("ThighL", "thigh_l"), ("CalfL", "calf_l"), ("FootL", "foot_l"),
             ("ThighR", "thigh_r"), ("CalfR", "calf_r"), ("FootR", "foot_r")]
    add_vars(an, [("Mesh", OBJ(unreal.PoseableMeshComponent.static_class()))] + [(n, NAME) for n, _ in names] +
             [("RefFootRotL", ROT), ("RefFootRotR", ROT), ("bReady", BOOL)], editable=tuple(n for n, _ in names))
    defaults(an, {n: v for n, v in names})

    pc = make_bp("BP_StaggerPlayerController", f"{R}/Core/Input", unreal.PlayerController)

    ch = make_bp("BP_PlayerCharacter", f"{R}/Player", unreal.Character)
    add_vars(ch, [("SpawnPose", XF)])
    handles = SDS.k2_gather_subobject_data_for_blueprint(ch)
    def find(var):
        for h in handles:
            d = SDL.get_data(h)
            if str(SDL.get_variable_name(d)) == var: return h
    existing = [str(SDL.get_variable_name(SDL.get_data(h))) for h in handles]
    log("subobjetos", existing)
    cap_h = find("CapsuleComponent")
    def add(name, cls, parent_h):
        if name in existing: return find(name)
        h, fail = SDS.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=parent_h, new_class=cls, blueprint_context=ch))
        SDS.rename_subobject(h, unreal.Text(name)); return h
    def obj(h): return SDL.get_object(SDL.get_data(h))
    body = obj(add("Body", unreal.PoseableMeshComponent, cap_h))
    mesh = unreal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple")
    try: body.set_editor_property("skinned_asset", mesh)
    except Exception as e:
        log("skinned_asset", e)
        try: body.set_skinned_asset_and_update(mesh)
        except Exception as e2: log("set_skinned_asset_and_update", e2)
    body.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0))
    body.set_collision_profile_name("NoCollision")
    boom_h = add("CameraBoom", unreal.SpringArmComponent, cap_h); boom = obj(boom_h)
    boom.set_editor_property("target_arm_length", 380.0); boom.set_editor_property("socket_offset", unreal.Vector(0, 0, 40))
    boom.set_editor_property("use_pawn_control_rotation", True); boom.set_editor_property("enable_camera_lag", True)
    boom.set_editor_property("camera_lag_speed", 6.0)
    add("FollowCamera", unreal.CameraComponent, boom_h)
    for n, bp_ in [("Legs", lc), ("Pelvis", pel), ("GroundProbe", prb), ("FootIK", iks), ("Animator", an)]:
        add(n, bp_.generated_class(), cap_h)
    cap = obj(cap_h)
    cap.set_editor_property("capsule_half_height", 40.0); cap.set_editor_property("capsule_radius", 22.0)
    BEL.compile_blueprint(ch)
    cdo = unreal.get_default_object(ch.generated_class())
    cdo.set_editor_property("use_controller_rotation_yaw", False)
    out["char_subobjects"] = [str(SDL.get_variable_name(SDL.get_data(h))) for h in SDS.k2_gather_subobject_data_for_blueprint(ch)]

    for bp_ in [leg, pel, prb, iks, lc, an, pc, ch]:
        try: BEL.remove_unused_nodes(bp_)
        except Exception as e: log("remove_unused_nodes", bp_.get_name(), e)
        BEL.compile_blueprint(bp_)
        EAL.save_loaded_asset(bp_)
except Exception: out["err"] = traceback.format_exc()
open(os.path.join(P, "Tools", "run_out.json"), "w").write(json.dumps(out, indent=1, default=str))
