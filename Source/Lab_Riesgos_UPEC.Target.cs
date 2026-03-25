using UnrealBuildTool;

public class Lab_Riesgos_UPECTarget : TargetRules
{
	public Lab_Riesgos_UPECTarget(TargetInfo Target) : base(Target)
	{
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		Type = TargetType.Game;
		ExtraModuleNames.Add("Lab_Riesgos_UPEC");
	}
}
