import unreal, json, os
out = {}
P = unreal.Paths.project_dir()
def names(o, pref=""):
    return sorted([n for n in dir(o) if not n.startswith("_") and n.startswith(pref)])
out["bel"] = names(unreal.BlueprintEditorLibrary)
out["has"] = {k: hasattr(unreal, k) for k in ["BlueprintEditorLibrary","SubobjectDataSubsystem","InputAction","InputMappingContext","InputAction_Factory","InputMappingContext_Factory","BlueprintFactory","BlueprintInterfaceFactory","StructureFactory","EnumFactory","UserDefinedStruct","UserDefinedEnum","EnhancedActionKeyMapping","InputModifierNegate","InputModifierSwizzleAxis","PoseableMeshComponent","EnhancedPlayerInput","EnumEditorLibrary","StructEditorLibrary","UserDefinedEnumEditorLibrary","UserDefinedStructEditorLibrary"]}
try:
    out["imc_props"] = names(unreal.InputMappingContext)
except Exception as e: out["imc_err"] = str(e)
try:
    out["epi"] = names(unreal.EnhancedPlayerInput)
except Exception as e: out["epi_err"] = str(e)
# GameMode references
gm = unreal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode")
cdo = unreal.get_default_object(gm.generated_class())
out["gm_pawn"] = str(cdo.get_editor_property("default_pawn_class"))
out["gm_pc"] = str(cdo.get_editor_property("player_controller_class"))
ar = unreal.AssetRegistryHelpers.get_asset_registry()
refs = {}
for pkg in ["/Script/ProyectosIII_ProtoII"]:
    refs[pkg] = [str(x) for x in ar.get_referencers(pkg, unreal.AssetRegistryDependencyOptions())] if hasattr(ar,"get_referencers") else "n/a"
out["refs"] = refs
# what is in level referencing BP_ThirdPersonCharacter
lvl = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
out["actors"] = sorted(set(a.get_class().get_name() for a in actors))
ws = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_world_settings()
try: out["ws_gm"] = str(ws.get_editor_property("default_game_mode"))
except Exception as e: out["ws_gm"] = str(e)
open(os.path.join(P, "Tools", "probe_out.json"), "w").write(json.dumps(out, indent=1))
print("PROBE DONE")
