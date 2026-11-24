# Fase A: assets base del sistema de movimiento (UML 5a) en Blueprints.
import unreal, json, os, traceback
P = unreal.Paths.project_dir()
out = {"log": []}
def log(*a): out["log"].append(" ".join(str(x) for x in a))
AT = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
BEL = unreal.BlueprintEditorLibrary

def get_or_create(name, path, cls, factory):
    full = f"{path}/{name}"
    if EAL.does_asset_exist(full):
        return unreal.load_asset(full)
    a = AT.create_asset(name, path, cls, factory)
    log("creado", full, a is not None)
    return a

try:
    R = "/Game/Stagger"
    for d in ["Core/Types", "Core/Config", "Core/Input", "Player", "Player/Movement", "Player/Animation"]:
        EAL.make_directory(f"{R}/{d}")

    # Enums (las entradas se rellenan desde el editor)
    for n, p in [("E_LegSide", "Core/Types"), ("E_SurfaceType", "Core/Types"), ("E_LegState", "Player/Movement")]:
        get_or_create(n, f"{R}/{p}", unreal.UserDefinedEnum, unreal.EnumFactory())

    # Input Actions
    IP = f"{R}/Core/Input"
    ias = {}
    for n, axis in [("IA_LeftLeg", False), ("IA_RightLeg", False), ("IA_StepDirection", True),
                    ("IA_Look", True), ("IA_ContextAction", False), ("IA_Pause", False)]:
        a = get_or_create(n, IP, unreal.InputAction, unreal.InputAction_Factory())
        a.set_editor_property("value_type", unreal.InputActionValueType.AXIS2D if axis else unreal.InputActionValueType.BOOLEAN)
        ias[n] = a
    def key(k):
        kk = unreal.Key(); kk.import_text(k); return kk
    def mapping(imc, action, k, mods=()):
        m = imc.map_key(action, key(k))
        if mods:
            arr = list(imc.get_editor_property("mappings"))
            idx = None
            for i, mm in enumerate(arr):
                if mm.get_editor_property("action") == action and str(mm.get_editor_property("key").get_editor_property("key_name")) == k:
                    idx = i
            if idx is not None:
                mm = arr[idx]
                objs = []
                for cls, props in mods:
                    o = unreal.new_object(cls, outer=imc)
                    for pk, pv in props.items():
                        o.set_editor_property(pk, pv)
                    objs.append(o)
                mm.set_editor_property("modifiers", objs)
                arr[idx] = mm
                imc.set_editor_property("mappings", arr)
    SW = (unreal.InputModifierSwizzleAxis, {})
    NG = (unreal.InputModifierNegate, {})
    for n in ["IMC_Keyboard", "IMC_Gamepad"]:
        imc = get_or_create(n, IP, unreal.InputMappingContext, unreal.InputMappingContext_Factory())
        imc.unmap_all()
        if n == "IMC_Keyboard":
            for k in ["Q", "LeftMouseButton"]: mapping(imc, ias["IA_LeftLeg"], k)
            for k in ["E", "RightMouseButton"]: mapping(imc, ias["IA_RightLeg"], k)
            mapping(imc, ias["IA_StepDirection"], "W", [SW])
            mapping(imc, ias["IA_StepDirection"], "S", [SW, NG])
            mapping(imc, ias["IA_StepDirection"], "A", [NG])
            mapping(imc, ias["IA_StepDirection"], "D")
            mapping(imc, ias["IA_Look"], "Mouse2D")
            mapping(imc, ias["IA_ContextAction"], "F")
            mapping(imc, ias["IA_Pause"], "P")
        else:
            mapping(imc, ias["IA_LeftLeg"], "Gamepad_LeftTrigger")
            mapping(imc, ias["IA_RightLeg"], "Gamepad_RightTrigger")
            mapping(imc, ias["IA_StepDirection"], "Gamepad_Left2D")
            mapping(imc, ias["IA_Look"], "Gamepad_Right2D",
                    [(unreal.InputModifierScaleByDeltaTime, {}), (unreal.InputModifierScalar, {"scalar": unreal.Vector(60, 60, 1)})])
            mapping(imc, ias["IA_ContextAction"], "Gamepad_FaceButton_Bottom")
            mapping(imc, ias["IA_Pause"], "Gamepad_Special_Right")
        log(n, "mappings", len(imc.get_editor_property("mappings")),
            [len(m.get_editor_property("modifiers")) for m in imc.get_editor_property("mappings")])

    # Interfaces vacías (las firmas se pegan después)
    for n, p in [("BPI_PlayerInput", "Core/Input"), ("BPI_PlayerTeleport", "Player"),
                 ("BPI_MovementLock", "Player/Movement"), ("BPI_SurfaceProvider", "Player/Movement"),
                 ("BPI_GroundProbe", "Player/Movement"), ("BPI_FootIK", "Player/Movement"),
                 ("BPI_PlayerAnimator", "Player/Animation")]:
        bpi = get_or_create(n, f"{R}/{p}", unreal.Blueprint, unreal.BlueprintInterfaceFactory())
        try:
            BEL.remove_function_graph(bpi, "NewFunction")
        except Exception as e:
            log("rm NewFunction", n, e)

    # Data asset de configuración del paso (StepConfig, P-22)
    f = unreal.BlueprintFactory(); f.set_editor_property("parent_class", unreal.PrimaryDataAsset)
    pda = get_or_create("PDA_StepConfig", f"{R}/Core/Config", unreal.Blueprint, f)
    real = BEL.get_basic_type_by_name("real")
    cfg = [("MaxStepLength", 55.0), ("LiftHeight", 18.0), ("FootMoveSpeed", 110.0), ("LiftSpeed", 140.0),
           ("PelvisFollowSpeed", 5.0), ("WeightShift", 0.55), ("StandHeightRatio", 0.96), ("BodyTurnSpeed", 160.0),
           ("MaxStepUp", 22.0), ("MinFootSeparation", 14.0), ("FootRadius", 6.0), ("EdgeDropHeight", 8.0),
           ("SlideFrictionThreshold", 0.35), ("SlideDeceleration", 4.0)]
    for n, v in cfg:
        BEL.add_member_variable(pda, n, real)
        BEL.set_blueprint_variable_instance_editable(pda, n, True)
    BEL.compile_blueprint(pda)
    cdo = unreal.get_default_object(pda.generated_class())
    for n, v in cfg:
        cdo.set_editor_property(n, v)
    EAL.save_loaded_asset(pda)
    df = unreal.DataAssetFactory(); df.set_editor_property("data_asset_class", pda.generated_class())
    da = get_or_create("DA_StepConfig", f"{R}/Core/Config", unreal.PrimaryDataAsset, df)
    log("DA", da, da.get_class().get_name() if da else None)

    for p in EAL.list_assets(R, recursive=True):
        if "/_Tmp/" not in p:
            EAL.save_asset(p, only_if_is_dirty=False)
    out["assets"] = [p for p in EAL.list_assets(R, recursive=True)]
except Exception:
    out["err"] = traceback.format_exc()
open(os.path.join(P, "Tools", "run_out.json"), "w").write(json.dumps(out, indent=1, default=str))
