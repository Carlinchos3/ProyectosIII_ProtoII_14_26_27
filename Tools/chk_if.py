import unreal, json, os
P = unreal.Paths.project_dir()
R = "/Game/Stagger"
pairs = [("Player/Movement/BPC_RaycastGroundProbe", "Player/Movement/BPI_GroundProbe"),
         ("Player/Movement/BPC_FootIKSolver", "Player/Movement/BPI_FootIK"),
         ("Player/Movement/BPC_LegController", "Player/Movement/BPI_MovementLock"),
         ("Player/Animation/BPC_PlayerAnimatorBridge", "Player/Animation/BPI_PlayerAnimator"),
         ("Core/Input/BP_StaggerPlayerController", "Core/Input/BPI_PlayerInput"),
         ("Player/BP_PlayerCharacter", "Player/BPI_PlayerTeleport")]
out = {}
for b, i in pairs:
    try:
        bc = unreal.load_asset(f"{R}/{b}").generated_class()
        ic = unreal.load_asset(f"{R}/{i}").generated_class()
        out[b] = unreal.SystemLibrary.does_implement_interface(unreal.get_default_object(bc), ic)
    except Exception as e:
        out[b] = str(e)
import time
out["t"] = time.time()
open(os.path.join(P, "Tools", "out_chk_if.json"), "w").write(json.dumps(out, indent=1))
