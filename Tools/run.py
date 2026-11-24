import unreal, json, os, traceback
P = unreal.Paths.project_dir()
out = {}
try:
    at = unreal.AssetToolsHelpers.get_asset_tools()
    path = "/Game/Stagger/_Tmp"
    bpi = unreal.load_asset(path + "/BPI_FormatSample")
    if not bpi:
        f = unreal.BlueprintInterfaceFactory()
        bpi = at.create_asset("BPI_FormatSample", path, unreal.Blueprint, f)
    out["bpi"] = str(bpi)
    unreal.EditorAssetLibrary.save_loaded_asset(bpi)
    unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([bpi])
    out["bp_props"] = [n for n in dir(unreal.Blueprint) if "interface" in n.lower() or "implement" in n.lower()]
except Exception:
    out["err"] = traceback.format_exc()
open(os.path.join(P, "Tools", "run_out.json"), "w").write(json.dumps(out, indent=1))
