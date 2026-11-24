import sys, unreal
a = unreal.load_asset(sys.argv[1])
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([a])
