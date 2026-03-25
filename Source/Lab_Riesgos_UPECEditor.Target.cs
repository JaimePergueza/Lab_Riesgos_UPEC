using UnrealBuildTool;

public class Lab_Riesgos_UPECEditorTarget : TargetRules
{
	public Lab_Riesgos_UPECEditorTarget(TargetInfo Target) : base(Target)
	{
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		Type = TargetType.Editor;
		ExtraModuleNames.Add("Lab_Riesgos_UPEC");
	}
}
