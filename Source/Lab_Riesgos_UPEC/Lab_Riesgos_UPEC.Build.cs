using UnrealBuildTool;

public class Lab_Riesgos_UPEC : ModuleRules
{
	public Lab_Riesgos_UPEC(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PrivateDependencyModuleNames.Add("Core");
		PrivateDependencyModuleNames.Add("CoreUObject");
		PrivateDependencyModuleNames.Add("Engine");
		PrivateDependencyModuleNames.AddRange(new string[] { "InputCore", "EnhancedInput", "HeadMountedDisplay", "XRBase", "UMG", "Slate", "SlateCore" });
	}
}
