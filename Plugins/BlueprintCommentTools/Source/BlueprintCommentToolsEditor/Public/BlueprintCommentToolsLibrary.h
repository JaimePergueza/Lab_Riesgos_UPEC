#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Layout/Margin.h"

#include "BlueprintCommentToolsLibrary.generated.h"

/** Specification for one editor-only Blueprint graph comment box. */
USTRUCT(BlueprintType)
struct FBlueprintCommentBoxSpec
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blueprint Comment Tools")
    FString CommentText;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blueprint Comment Tools")
    int32 X = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blueprint Comment Tools")
    int32 Y = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blueprint Comment Tools", meta = (ClampMin = "1"))
    int32 Width = 600;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blueprint Comment Tools", meta = (ClampMin = "1"))
    int32 Height = 300;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blueprint Comment Tools")
    FLinearColor Color = FLinearColor(0.12f, 0.32f, 0.70f, 0.20f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blueprint Comment Tools", meta = (ClampMin = "1", ClampMax = "1000"))
    int32 FontSize = 18;

    /** When true, the listed nodes move with the comment box in the Blueprint editor. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blueprint Comment Tools")
    bool bAssociateNodes = false;

    /** Optional node GUIDs to associate with the comment box. No graph links are changed. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blueprint Comment Tools")
    TArray<FGuid> NodeGuids;
};

/** Read-only information about one Blueprint graph node. */
USTRUCT(BlueprintType)
struct FBlueprintGraphNodeInfo
{
    GENERATED_BODY()

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Blueprint Comment Tools")
    FGuid NodeGuid;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Blueprint Comment Tools")
    FString NodeTitle;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Blueprint Comment Tools")
    FString NodeClass;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Blueprint Comment Tools")
    int32 NodePosX = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Blueprint Comment Tools")
    int32 NodePosY = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Blueprint Comment Tools")
    int32 NodeWidth = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Blueprint Comment Tools")
    int32 NodeHeight = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Blueprint Comment Tools")
    bool bIsComment = false;
};

/** Editor-only layout specification for a widget whose parent slot is a CanvasPanelSlot. */
USTRUCT(BlueprintType)
struct FWidgetCanvasSlotLayoutSpec
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Widget Layout Tools")
    FString WidgetName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Widget Layout Tools")
    FVector2D AnchorMinimum = FVector2D::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Widget Layout Tools")
    FVector2D AnchorMaximum = FVector2D::ZeroVector;

    /**
     * Canvas offsets. With fixed anchors, Left/Top are position and Right/Bottom are size.
     * With stretched anchors, all four values are margins.
     */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Widget Layout Tools")
    FMargin Offsets = FMargin(0.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Widget Layout Tools")
    FVector2D Alignment = FVector2D::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Widget Layout Tools")
    int32 ZOrder = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Widget Layout Tools")
    bool bAutoSize = false;
};

/**
 * Editor-only reflection API for audit-safe Blueprint graph comment boxes.
 * It never creates functional Blueprint nodes or alters graph links.
 */
UCLASS()
class BLUEPRINTCOMMENTTOOLSEDITOR_API UBlueprintCommentToolsLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /** Adds one comment box to a graph. The Blueprint is saved only when bSaveAsset is true. */
    UFUNCTION(BlueprintCallable, Category = "Blueprint Comment Tools")
    static bool AddCommentBoxToBlueprint(
        const FString& BlueprintAssetPath,
        const FString& GraphName,
        const FString& CommentText,
        int32 X,
        int32 Y,
        int32 Width,
        int32 Height,
        FLinearColor Color,
        int32 FontSize,
        bool bSaveAsset,
        FString& OutMessage);

    /** Adds several comment boxes to one graph. The Blueprint is saved only when bSaveAsset is true. */
    UFUNCTION(BlueprintCallable, Category = "Blueprint Comment Tools")
    static bool AddCommentBoxesToBlueprint(
        const FString& BlueprintAssetPath,
        const FString& GraphName,
        const TArray<FBlueprintCommentBoxSpec>& CommentBoxes,
        bool bSaveAsset,
        FString& OutMessage);

    /** Repositions existing comment boxes matched by their exact text; it never creates or deletes graph nodes. */
    UFUNCTION(BlueprintCallable, Category = "Blueprint Comment Tools")
    static bool UpdateCommentBoxesInBlueprint(
        const FString& BlueprintAssetPath,
        const FString& GraphName,
        const TArray<FBlueprintCommentBoxSpec>& CommentBoxes,
        bool bSaveAsset,
        FString& OutMessage);

    /** Returns only graph metadata; it never modifies or saves the Blueprint. */
    UFUNCTION(BlueprintCallable, Category = "Blueprint Comment Tools")
    static bool ListBlueprintGraphNodes(
        const FString& BlueprintAssetPath,
        const FString& GraphName,
        TArray<FBlueprintGraphNodeInfo>& OutNodes,
        FString& OutMessage);

    /**
     * Updates one CanvasPanelSlot in an existing Widget Blueprint.
     * It never creates, deletes, reparents, or reorders widgets and saves only when bSaveAsset is true.
     */
    UFUNCTION(BlueprintCallable, Category = "Widget Layout Tools")
    static bool SetWidgetCanvasSlotLayout(
        const FString& WidgetBlueprintAssetPath,
        const FWidgetCanvasSlotLayoutSpec& Layout,
        bool bSaveAsset,
        FString& OutMessage);

    /**
     * Atomically validates and updates several CanvasPanelSlots in an existing Widget Blueprint.
     * It never creates, deletes, reparents, or reorders widgets and saves only when bSaveAsset is true.
     */
    UFUNCTION(BlueprintCallable, Category = "Widget Layout Tools")
    static bool SetWidgetCanvasSlotLayouts(
        const FString& WidgetBlueprintAssetPath,
        const TArray<FWidgetCanvasSlotLayoutSpec>& Layouts,
        bool bSaveAsset,
        FString& OutMessage);
};
