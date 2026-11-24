import unreal, json, os, traceback
P = unreal.Paths.project_dir()
out = {"log": []}
def log(*a): out["log"].append(" ".join(str(x) for x in a))
try:
    AES = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    for a in AES.get_all_edited_assets():
        AES.close_all_editors_for_asset(a)
    BEL = unreal.BlueprintEditorLibrary
    R = "/Game/Stagger"
    for p in ["Core/Input/BPI_PlayerInput", "Player/BPI_PlayerTeleport", "Player/Movement/BPI_MovementLock",
              "Player/Movement/BPI_SurfaceProvider", "Player/Movement/BPI_GroundProbe", "Player/Movement/BPI_FootIK",
              "Player/Animation/BPI_PlayerAnimator"]:
        bp = unreal.load_asset(f"{R}/{p}")
        g = BEL.find_graph(bp, "NewFunction")
        log(p, "found", g is not None)
        if g:
            BEL.remove_graph(bp, g)
            log(p, "after", BEL.find_graph(bp, "NewFunction") is not None)
        BEL.compile_blueprint(bp)
        unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
except Exception:
    log(traceback.format_exc())
open(os.path.join(P, "Tools", "out_tidy2.json"), "w").write(json.dumps(out, indent=1))
