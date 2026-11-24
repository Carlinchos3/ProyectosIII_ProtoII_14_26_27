import unreal, json, os, traceback
P = unreal.Paths.project_dir()
out = {"log": []}
def log(*a): out["log"].append(" ".join(str(x) for x in a))
try:
    EAL = unreal.EditorAssetLibrary
    gm = unreal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode")
    cdo = unreal.get_default_object(gm.generated_class())
    log("before", cdo.get_editor_property("default_pawn_class"), cdo.get_editor_property("player_controller_class"))
    pawn = unreal.load_asset("/Game/Stagger/Player/BP_PlayerCharacter").generated_class()
    pc = unreal.load_asset("/Game/Stagger/Core/Input/BP_StaggerPlayerController").generated_class()
    cdo.set_editor_property("default_pawn_class", pawn)
    cdo.set_editor_property("player_controller_class", pc)
    unreal.BlueprintEditorLibrary.compile_blueprint(gm)
    cdo = unreal.get_default_object(gm.generated_class())
    log("after", cdo.get_editor_property("default_pawn_class"), cdo.get_editor_property("player_controller_class"))
    log("save", EAL.save_loaded_asset(gm, False))
    for p in ["/Game/Stagger/_Tmp/BP_FormatSample", "/Game/Stagger/_Tmp/BPI_FormatSample"]:
        a = unreal.load_asset(p)
        try: unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(a)
        except Exception as e: log("close", e)
        log("del", p, EAL.delete_asset(p))
    log("deldir", EAL.delete_directory("/Game/Stagger/_Tmp"))
except Exception:
    log(traceback.format_exc())
open(os.path.join(P, "Tools", "out_gm.json"), "w").write(json.dumps(out, indent=1))
