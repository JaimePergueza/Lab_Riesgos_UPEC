using UnrealBuildTool;

public class BlueprintCommentToolsEditor : ModuleRules
{
    public BlueprintCommentToolsEditor(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "SlateCore"
        });

        PrivateDependencyModuleNames.AddRange(new[]
        {
            "UnrealEd",
            "BlueprintGraph",
            "EditorScriptingUtilities",
            "Slate",
            "UMG",
            "UMGEditor"
        });
    }
}
