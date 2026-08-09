#include "BlueprintCommentToolsLibrary.h"

#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphNode.h"
#include "EdGraphNode_Comment.h"
#include "EditorAssetLibrary.h"
#include "Engine/Blueprint.h"
#include "WidgetBlueprint.h"
#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Widget.h"
#include "Editor.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "ScopedTransaction.h"

namespace BlueprintCommentTools::Private
{
    static bool IsSupportedBlueprintPath(const FString& BlueprintAssetPath, FString& OutMessage)
    {
        if (BlueprintAssetPath.IsEmpty() || !BlueprintAssetPath.StartsWith(TEXT("/Game/")))
        {
            OutMessage = TEXT("BlueprintAssetPath debe ser una ruta de objeto /Game/... exacta.");
            return false;
        }

        if (BlueprintAssetPath.Contains(TEXT("/ExternalActors/"), ESearchCase::IgnoreCase))
        {
            OutMessage = TEXT("No se permiten ExternalActors.");
            return false;
        }

        return true;
    }

    static UBlueprint* LoadBlueprintStrict(const FString& BlueprintAssetPath, FString& OutMessage)
    {
        if (!IsSupportedBlueprintPath(BlueprintAssetPath, OutMessage))
        {
            return nullptr;
        }

        UObject* LoadedObject = UEditorAssetLibrary::LoadAsset(BlueprintAssetPath);
        UBlueprint* Blueprint = Cast<UBlueprint>(LoadedObject);
        if (!Blueprint)
        {
            OutMessage = FString::Printf(TEXT("El asset no es un UBlueprint cargable: %s"), *BlueprintAssetPath);
            return nullptr;
        }

        if (!Blueprint->GetPathName().Equals(BlueprintAssetPath, ESearchCase::CaseSensitive))
        {
            OutMessage = FString::Printf(TEXT("La ruta cargada no coincide exactamente. Esperada: %s; cargada: %s"), *BlueprintAssetPath, *Blueprint->GetPathName());
            return nullptr;
        }

        return Blueprint;
    }

    static UEdGraph* FindBlueprintGraph(UBlueprint* Blueprint, const FString& GraphName)
    {
        if (!Blueprint || GraphName.IsEmpty())
        {
            return nullptr;
        }

        TArray<UEdGraph*> Graphs;
        Blueprint->GetAllGraphs(Graphs);
        UEdGraph* const* FoundGraph = Graphs.FindByPredicate([&GraphName](const UEdGraph* Graph)
        {
            return Graph && Graph->GetName().Equals(GraphName, ESearchCase::CaseSensitive);
        });
        return FoundGraph ? *FoundGraph : nullptr;
    }

    static bool ValidateCommentSpec(const FBlueprintCommentBoxSpec& Spec, FString& OutMessage)
    {
        if (Spec.CommentText.TrimStartAndEnd().IsEmpty())
        {
            OutMessage = TEXT("CommentText no puede estar vacío.");
            return false;
        }

        if (Spec.Width <= 0 || Spec.Height <= 0)
        {
            OutMessage = TEXT("Width y Height deben ser mayores que cero.");
            return false;
        }

        if (Spec.FontSize < 1 || Spec.FontSize > 1000)
        {
            OutMessage = TEXT("FontSize debe estar entre 1 y 1000.");
            return false;
        }

        return true;
    }

    static void AssociateSpecifiedNodes(UEdGraphNode_Comment* CommentNode, UEdGraph* Graph, const FBlueprintCommentBoxSpec& Spec)
    {
        if (!Spec.bAssociateNodes || !CommentNode || !Graph)
        {
            return;
        }

        CommentNode->MoveMode = ECommentBoxMode::GroupMovement;
        for (const FGuid& NodeGuid : Spec.NodeGuids)
        {
            for (UEdGraphNode* Candidate : Graph->Nodes)
            {
                if (Candidate && Candidate != CommentNode && Candidate->NodeGuid == NodeGuid)
                {
                    CommentNode->AddNodeUnderComment(Candidate);
                    break;
                }
            }
        }
    }

    static UEdGraphNode_Comment* CreateCommentNode(UEdGraph* Graph, const FBlueprintCommentBoxSpec& Spec)
    {
        Graph->Modify();

        UEdGraphNode_Comment* CommentNode = NewObject<UEdGraphNode_Comment>(Graph, NAME_None, RF_Transactional);
        if (!CommentNode)
        {
            return nullptr;
        }

        CommentNode->Modify();
        CommentNode->CreateNewGuid();
        CommentNode->PostPlacedNewNode();
        CommentNode->NodeComment = Spec.CommentText;
        CommentNode->NodePosX = Spec.X;
        CommentNode->NodePosY = Spec.Y;
        CommentNode->NodeWidth = Spec.Width;
        CommentNode->NodeHeight = Spec.Height;
        CommentNode->CommentColor = Spec.Color;
        CommentNode->FontSize = Spec.FontSize;
        CommentNode->bCommentBubbleVisible_InDetailsPanel = false;
        CommentNode->bColorCommentBubble = false;
        CommentNode->MoveMode = ECommentBoxMode::NoGroupMovement;
        CommentNode->AllocateDefaultPins();

        Graph->AddNode(CommentNode, true, false);
        AssociateSpecifiedNodes(CommentNode, Graph, Spec);
        Graph->NotifyGraphChanged();
        return CommentNode;
    }

    static UEdGraphNode_Comment* FindCommentNodeByText(UEdGraph* Graph, const FString& CommentText, FString& OutMessage)
    {
        UEdGraphNode_Comment* Match = nullptr;
        for (UEdGraphNode* Node : Graph->Nodes)
        {
            UEdGraphNode_Comment* Candidate = Cast<UEdGraphNode_Comment>(Node);
            if (!Candidate || !Candidate->NodeComment.Equals(CommentText, ESearchCase::CaseSensitive))
            {
                continue;
            }

            if (Match)
            {
                OutMessage = FString::Printf(TEXT("Hay varias cajas de comentario con el texto exacto '%s'."), *CommentText);
                return nullptr;
            }

            Match = Candidate;
        }

        if (!Match)
        {
            OutMessage = FString::Printf(TEXT("No existe una caja de comentario con el texto exacto '%s'."), *CommentText);
        }

        return Match;
    }

    static void UpdateCommentNode(UEdGraphNode_Comment* CommentNode, UEdGraph* Graph, const FBlueprintCommentBoxSpec& Spec)
    {
        CommentNode->Modify();
        CommentNode->NodePosX = Spec.X;
        CommentNode->NodePosY = Spec.Y;
        CommentNode->NodeWidth = Spec.Width;
        CommentNode->NodeHeight = Spec.Height;
        CommentNode->CommentColor = Spec.Color;
        CommentNode->FontSize = Spec.FontSize;

        if (Spec.bAssociateNodes)
        {
            AssociateSpecifiedNodes(CommentNode, Graph, Spec);
        }
        else
        {
            CommentNode->MoveMode = ECommentBoxMode::NoGroupMovement;
        }
    }

    static bool IsFiniteVector(const FVector2D& Value)
    {
        return FMath::IsFinite(Value.X) && FMath::IsFinite(Value.Y);
    }

    static bool IsFiniteMargin(const FMargin& Value)
    {
        return FMath::IsFinite(Value.Left)
            && FMath::IsFinite(Value.Top)
            && FMath::IsFinite(Value.Right)
            && FMath::IsFinite(Value.Bottom);
    }

    static bool ValidateCanvasSlotLayoutSpec(const FWidgetCanvasSlotLayoutSpec& Spec, FString& OutMessage)
    {
        if (Spec.WidgetName.TrimStartAndEnd().IsEmpty())
        {
            OutMessage = TEXT("WidgetName no puede estar vacio.");
            return false;
        }

        if (Spec.WidgetName != Spec.WidgetName.TrimStartAndEnd())
        {
            OutMessage = FString::Printf(
                TEXT("WidgetName '%s' contiene espacios al inicio o al final."),
                *Spec.WidgetName);
            return false;
        }

        if (!IsFiniteVector(Spec.AnchorMinimum)
            || !IsFiniteVector(Spec.AnchorMaximum)
            || !IsFiniteVector(Spec.Alignment)
            || !IsFiniteMargin(Spec.Offsets))
        {
            OutMessage = FString::Printf(TEXT("El layout de '%s' contiene valores no finitos."), *Spec.WidgetName);
            return false;
        }

        const auto IsNormalized = [](const float Value)
        {
            return Value >= 0.0f && Value <= 1.0f;
        };

        if (!IsNormalized(Spec.AnchorMinimum.X)
            || !IsNormalized(Spec.AnchorMinimum.Y)
            || !IsNormalized(Spec.AnchorMaximum.X)
            || !IsNormalized(Spec.AnchorMaximum.Y)
            || Spec.AnchorMinimum.X > Spec.AnchorMaximum.X
            || Spec.AnchorMinimum.Y > Spec.AnchorMaximum.Y)
        {
            OutMessage = FString::Printf(TEXT("Los anchors de '%s' deben estar entre 0 y 1 y Min no puede superar Max."), *Spec.WidgetName);
            return false;
        }

        if (!IsNormalized(Spec.Alignment.X) || !IsNormalized(Spec.Alignment.Y))
        {
            OutMessage = FString::Printf(TEXT("Alignment de '%s' debe estar entre 0 y 1."), *Spec.WidgetName);
            return false;
        }

        if (Spec.ZOrder < -10000 || Spec.ZOrder > 10000)
        {
            OutMessage = FString::Printf(TEXT("ZOrder de '%s' debe estar entre -10000 y 10000."), *Spec.WidgetName);
            return false;
        }

        return true;
    }
}

bool UBlueprintCommentToolsLibrary::AddCommentBoxToBlueprint(
    const FString& BlueprintAssetPath,
    const FString& GraphName,
    const FString& CommentText,
    const int32 X,
    const int32 Y,
    const int32 Width,
    const int32 Height,
    const FLinearColor Color,
    const int32 FontSize,
    const bool bSaveAsset,
    FString& OutMessage)
{
    FBlueprintCommentBoxSpec Spec;
    Spec.CommentText = CommentText;
    Spec.X = X;
    Spec.Y = Y;
    Spec.Width = Width;
    Spec.Height = Height;
    Spec.Color = Color;
    Spec.FontSize = FontSize;

    return AddCommentBoxesToBlueprint(BlueprintAssetPath, GraphName, { Spec }, bSaveAsset, OutMessage);
}

bool UBlueprintCommentToolsLibrary::AddCommentBoxesToBlueprint(
    const FString& BlueprintAssetPath,
    const FString& GraphName,
    const TArray<FBlueprintCommentBoxSpec>& CommentBoxes,
    const bool bSaveAsset,
    FString& OutMessage)
{
    OutMessage.Reset();

    if (CommentBoxes.IsEmpty())
    {
        OutMessage = TEXT("No se recibieron cajas de comentario.");
        return false;
    }

    for (const FBlueprintCommentBoxSpec& Spec : CommentBoxes)
    {
        if (!BlueprintCommentTools::Private::ValidateCommentSpec(Spec, OutMessage))
        {
            return false;
        }
    }

    UBlueprint* Blueprint = BlueprintCommentTools::Private::LoadBlueprintStrict(BlueprintAssetPath, OutMessage);
    if (!Blueprint)
    {
        return false;
    }

    UEdGraph* Graph = BlueprintCommentTools::Private::FindBlueprintGraph(Blueprint, GraphName);
    if (!Graph)
    {
        OutMessage = FString::Printf(TEXT("No existe el graph '%s' en %s."), *GraphName, *BlueprintAssetPath);
        return false;
    }

    Blueprint->Modify();
    for (const FBlueprintCommentBoxSpec& Spec : CommentBoxes)
    {
        if (!BlueprintCommentTools::Private::CreateCommentNode(Graph, Spec))
        {
            OutMessage = TEXT("No se pudo crear una caja de comentario. No se guardó el Blueprint.");
            return false;
        }
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    if (bSaveAsset && !UEditorAssetLibrary::SaveLoadedAsset(Blueprint, false))
    {
        OutMessage = FString::Printf(TEXT("Se crearon %d comentarios, pero no se pudo guardar solo el Blueprint indicado."), CommentBoxes.Num());
        return false;
    }

    OutMessage = FString::Printf(TEXT("Se crearon %d cajas de comentario en %s:%s."), CommentBoxes.Num(), *BlueprintAssetPath, *GraphName);
    return true;
}

bool UBlueprintCommentToolsLibrary::UpdateCommentBoxesInBlueprint(
    const FString& BlueprintAssetPath,
    const FString& GraphName,
    const TArray<FBlueprintCommentBoxSpec>& CommentBoxes,
    const bool bSaveAsset,
    FString& OutMessage)
{
    OutMessage.Reset();

    if (CommentBoxes.IsEmpty())
    {
        OutMessage = TEXT("No se recibieron cajas de comentario para actualizar.");
        return false;
    }

    TSet<FString> SeenCommentTexts;
    for (const FBlueprintCommentBoxSpec& Spec : CommentBoxes)
    {
        if (!BlueprintCommentTools::Private::ValidateCommentSpec(Spec, OutMessage))
        {
            return false;
        }

        if (SeenCommentTexts.Contains(Spec.CommentText))
        {
            OutMessage = FString::Printf(TEXT("El texto de comentario '%s' está repetido en la solicitud."), *Spec.CommentText);
            return false;
        }

        SeenCommentTexts.Add(Spec.CommentText);
    }

    UBlueprint* Blueprint = BlueprintCommentTools::Private::LoadBlueprintStrict(BlueprintAssetPath, OutMessage);
    if (!Blueprint)
    {
        return false;
    }

    UEdGraph* Graph = BlueprintCommentTools::Private::FindBlueprintGraph(Blueprint, GraphName);
    if (!Graph)
    {
        OutMessage = FString::Printf(TEXT("No existe el graph '%s' en %s."), *GraphName, *BlueprintAssetPath);
        return false;
    }

    TArray<UEdGraphNode_Comment*> ExistingComments;
    ExistingComments.Reserve(CommentBoxes.Num());
    for (const FBlueprintCommentBoxSpec& Spec : CommentBoxes)
    {
        UEdGraphNode_Comment* ExistingComment = BlueprintCommentTools::Private::FindCommentNodeByText(Graph, Spec.CommentText, OutMessage);
        if (!ExistingComment)
        {
            return false;
        }

        ExistingComments.Add(ExistingComment);
    }

    Blueprint->Modify();
    Graph->Modify();
    for (int32 Index = 0; Index < CommentBoxes.Num(); ++Index)
    {
        BlueprintCommentTools::Private::UpdateCommentNode(ExistingComments[Index], Graph, CommentBoxes[Index]);
    }

    Graph->NotifyGraphChanged();
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    if (bSaveAsset && !UEditorAssetLibrary::SaveLoadedAsset(Blueprint, false))
    {
        OutMessage = FString::Printf(TEXT("Se actualizaron %d comentarios, pero no se pudo guardar solo el Blueprint indicado."), CommentBoxes.Num());
        return false;
    }

    OutMessage = FString::Printf(TEXT("Se actualizaron %d cajas de comentario en %s:%s."), CommentBoxes.Num(), *BlueprintAssetPath, *GraphName);
    return true;
}

bool UBlueprintCommentToolsLibrary::ListBlueprintGraphNodes(
    const FString& BlueprintAssetPath,
    const FString& GraphName,
    TArray<FBlueprintGraphNodeInfo>& OutNodes,
    FString& OutMessage)
{
    OutNodes.Reset();
    OutMessage.Reset();

    UBlueprint* Blueprint = BlueprintCommentTools::Private::LoadBlueprintStrict(BlueprintAssetPath, OutMessage);
    if (!Blueprint)
    {
        return false;
    }

    UEdGraph* Graph = BlueprintCommentTools::Private::FindBlueprintGraph(Blueprint, GraphName);
    if (!Graph)
    {
        OutMessage = FString::Printf(TEXT("No existe el graph '%s' en %s."), *GraphName, *BlueprintAssetPath);
        return false;
    }

    for (UEdGraphNode* Node : Graph->Nodes)
    {
        if (!Node)
        {
            continue;
        }

        FBlueprintGraphNodeInfo& Info = OutNodes.AddDefaulted_GetRef();
        Info.NodeGuid = Node->NodeGuid;
        Info.NodeTitle = Node->GetNodeTitle(ENodeTitleType::FullTitle).ToString();
        Info.NodeClass = Node->GetClass()->GetName();
        Info.NodePosX = Node->NodePosX;
        Info.NodePosY = Node->NodePosY;
        Info.NodeWidth = Node->NodeWidth;
        Info.NodeHeight = Node->NodeHeight;
        Info.bIsComment = Node->IsA<UEdGraphNode_Comment>();
    }

    OutMessage = FString::Printf(TEXT("Se listaron %d nodos de %s:%s sin modificar el asset."), OutNodes.Num(), *BlueprintAssetPath, *GraphName);
    return true;
}

bool UBlueprintCommentToolsLibrary::SetWidgetCanvasSlotLayout(
    const FString& WidgetBlueprintAssetPath,
    const FWidgetCanvasSlotLayoutSpec& Layout,
    const bool bSaveAsset,
    FString& OutMessage)
{
    return SetWidgetCanvasSlotLayouts(WidgetBlueprintAssetPath, { Layout }, bSaveAsset, OutMessage);
}

bool UBlueprintCommentToolsLibrary::SetWidgetCanvasSlotLayouts(
    const FString& WidgetBlueprintAssetPath,
    const TArray<FWidgetCanvasSlotLayoutSpec>& Layouts,
    const bool bSaveAsset,
    FString& OutMessage)
{
    OutMessage.Reset();

    if (GEditor && GEditor->PlayWorld)
    {
        OutMessage = TEXT("No se permite cambiar el layout de widgets durante PIE o SIE.");
        return false;
    }

    if (Layouts.IsEmpty())
    {
        OutMessage = TEXT("No se recibieron layouts de CanvasPanelSlot.");
        return false;
    }

    TSet<FName> SeenWidgetNames;
    for (const FWidgetCanvasSlotLayoutSpec& Layout : Layouts)
    {
        if (!BlueprintCommentTools::Private::ValidateCanvasSlotLayoutSpec(Layout, OutMessage))
        {
            return false;
        }

        const FName WidgetFName(*Layout.WidgetName);
        if (SeenWidgetNames.Contains(WidgetFName))
        {
            OutMessage = FString::Printf(TEXT("WidgetName '%s' esta repetido en la solicitud."), *Layout.WidgetName);
            return false;
        }

        SeenWidgetNames.Add(WidgetFName);
    }

    UBlueprint* Blueprint = BlueprintCommentTools::Private::LoadBlueprintStrict(WidgetBlueprintAssetPath, OutMessage);
    if (!Blueprint)
    {
        return false;
    }

    UWidgetBlueprint* WidgetBlueprint = Cast<UWidgetBlueprint>(Blueprint);
    if (!WidgetBlueprint)
    {
        OutMessage = FString::Printf(TEXT("El asset no es un Widget Blueprint: %s"), *WidgetBlueprintAssetPath);
        return false;
    }

    if (!WidgetBlueprint->WidgetTree)
    {
        OutMessage = FString::Printf(TEXT("El Widget Blueprint no tiene WidgetTree: %s"), *WidgetBlueprintAssetPath);
        return false;
    }

    TArray<UCanvasPanelSlot*> CanvasSlots;
    CanvasSlots.Reserve(Layouts.Num());
    for (const FWidgetCanvasSlotLayoutSpec& Layout : Layouts)
    {
        UWidget* Widget = WidgetBlueprint->WidgetTree->FindWidget(FName(*Layout.WidgetName));
        if (!Widget)
        {
            OutMessage = FString::Printf(TEXT("No existe el widget exacto '%s' en %s."), *Layout.WidgetName, *WidgetBlueprintAssetPath);
            return false;
        }

        UCanvasPanelSlot* CanvasSlot = Cast<UCanvasPanelSlot>(Widget->Slot);
        if (!CanvasSlot)
        {
            OutMessage = FString::Printf(TEXT("El widget '%s' no pertenece directamente a un CanvasPanel."), *Layout.WidgetName);
            return false;
        }

        CanvasSlots.Add(CanvasSlot);
    }

    const FScopedTransaction Transaction(
        NSLOCTEXT("BlueprintCommentTools", "SetWidgetCanvasSlotLayouts", "Set Widget Canvas Slot Layouts"));

    WidgetBlueprint->Modify();
    WidgetBlueprint->WidgetTree->Modify();
    for (int32 Index = 0; Index < Layouts.Num(); ++Index)
    {
        const FWidgetCanvasSlotLayoutSpec& Layout = Layouts[Index];
        UCanvasPanelSlot* CanvasSlot = CanvasSlots[Index];

        CanvasSlot->Modify();
        CanvasSlot->SetAnchors(FAnchors(
            Layout.AnchorMinimum.X,
            Layout.AnchorMinimum.Y,
            Layout.AnchorMaximum.X,
            Layout.AnchorMaximum.Y));
        CanvasSlot->SetOffsets(Layout.Offsets);
        CanvasSlot->SetAlignment(Layout.Alignment);
        CanvasSlot->SetZOrder(Layout.ZOrder);
        CanvasSlot->SetAutoSize(Layout.bAutoSize);
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(WidgetBlueprint);

    if (bSaveAsset && !UEditorAssetLibrary::SaveLoadedAsset(WidgetBlueprint, false))
    {
        OutMessage = FString::Printf(
            TEXT("Se actualizaron %d CanvasPanelSlots, pero no se pudo guardar solo el Widget Blueprint indicado."),
            Layouts.Num());
        return false;
    }

    OutMessage = FString::Printf(
        TEXT("Se actualizaron %d CanvasPanelSlots en %s."),
        Layouts.Num(),
        *WidgetBlueprintAssetPath);
    return true;
}
