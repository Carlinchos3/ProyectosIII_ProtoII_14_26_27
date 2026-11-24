import unreal, json, os
P = unreal.Paths.project_dir()
EAL = unreal.EditorAssetLibrary
out = {}
ar = unreal.AssetRegistryHelpers.get_asset_registry()
allp = [str(a.package_name) for a in ar.get_assets_by_path("/Game", True)]
out["game"] = [p for p in allp if not p.startswith("/Game/Stagger") and not p.startswith("/Game/LevelPrototyping") and "Mannequin" not in p and "Characters" not in p][:200]
for n in ["BP_ThirdPersonGameMode", "BP_ThirdPersonCharacter", "BP_ThirdPersonPlayerController", "IA_Move", "IA_Jump", "IA_Look", "IA_MouseLook", "IMC_Default", "IMC_MouseLook", "BP_FormatSample", "BPI_FormatSample", "Lvl_ThirdPerson"]:
    hits = [p for p in allp if p.split("/")[-1] == n]
    out[n] = {h: [str(r) for r in EAL.find_package_referencers_for_asset(h, False)] for h in hits}
open(os.path.join(P, "Tools", "out_q2.json"), "w").write(json.dumps(out, indent=1))
