#include "LabVRGameViewportClient.h"

#include "Blueprint/UserWidget.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Button.h"
#include "Components/CheckBox.h"
#include "Components/ComboBoxString.h"
#include "Components/EditableText.h"
#include "Components/EditableTextBox.h"
#include "Components/Slider.h"
#include "Components/SpinBox.h"
#include "Components/Widget.h"
#include "HeadMountedDisplayFunctionLibrary.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UObject/UObjectIterator.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/SNullWidget.h"
#include "Widgets/SOverlay.h"

bool ULabVRGameViewportClient::ShouldRouteToVR() const
{
	return !FParse::Param(FCommandLine::Get(), TEXT("nohmd"))
		&& UHeadMountedDisplayFunctionLibrary::IsHeadMountedDisplayEnabled()
		&& UHeadMountedDisplayFunctionLibrary::IsHeadMountedDisplayConnected();
}

void ULabVRGameViewportClient::EnsureVRRoot()
{
	if (!VRRoot.IsValid())
	{
		SAssignNew(VRRoot, SOverlay);
	}
}

void ULabVRGameViewportClient::EnsureLifetimeMarker()
{
	if (bLifetimeMarkerInstalled && ViewportLifetimeMarker.IsValid())
	{
		return;
	}

	TSharedRef<SWidget> Marker = SNew(SBox).Visibility(EVisibility::Collapsed);
	ViewportLifetimeMarker = Marker;
	bLifetimeMarkerInstalled = true;
	Super::AddViewportWidgetContent(Marker, TNumericLimits<int32>::Lowest());
}

void ULabVRGameViewportClient::AddToVR(TSharedRef<SWidget> Widget, int32 ZOrder, ULocalPlayer* Player)
{
	EnsureVRRoot();
	EnsureLifetimeMarker();

	for (const FVRWidgetEntry& Entry : VRWidgets)
	{
		if (Entry.Widget == Widget)
		{
			return;
		}
	}

	VRRoot->AddSlot(ZOrder)[Widget];
	FVRWidgetEntry& Entry = VRWidgets.AddDefaulted_GetRef();
	Entry.Widget = Widget;
	Entry.Player = Player;
	Entry.ZOrder = ZOrder;
}

bool ULabVRGameViewportClient::RemoveFromVR(TSharedRef<SWidget> Widget)
{
	for (int32 Index = VRWidgets.Num() - 1; Index >= 0; --Index)
	{
		if (VRWidgets[Index].Widget == Widget)
		{
			if (VRRoot.IsValid())
			{
				VRRoot->RemoveSlot(Widget);
			}
			VRWidgets.RemoveAt(Index);
			return true;
		}
	}
	return false;
}

void ULabVRGameViewportClient::ResetVRWidgets()
{
	if (VRRoot.IsValid())
	{
		VRRoot->ClearChildren();
	}
	VRWidgets.Reset();
}

void ULabVRGameViewportClient::AddViewportWidgetContent(TSharedRef<SWidget> ViewportContent, int32 ZOrder)
{
	if (ShouldRouteToVR())
	{
		AddToVR(ViewportContent, ZOrder, nullptr);
		return;
	}
	Super::AddViewportWidgetContent(ViewportContent, ZOrder);
}

void ULabVRGameViewportClient::RemoveViewportWidgetContent(TSharedRef<SWidget> ViewportContent)
{
	if (!RemoveFromVR(ViewportContent))
	{
		Super::RemoveViewportWidgetContent(ViewportContent);
	}
}

void ULabVRGameViewportClient::AddViewportWidgetForPlayer(ULocalPlayer* Player, TSharedRef<SWidget> ViewportContent, int32 ZOrder)
{
	if (ShouldRouteToVR())
	{
		AddToVR(ViewportContent, ZOrder, Player);
		return;
	}
	Super::AddViewportWidgetForPlayer(Player, ViewportContent, ZOrder);
}

void ULabVRGameViewportClient::RemoveViewportWidgetForPlayer(ULocalPlayer* Player, TSharedRef<SWidget> ViewportContent)
{
	if (!RemoveFromVR(ViewportContent))
	{
		Super::RemoveViewportWidgetForPlayer(Player, ViewportContent);
	}
}

TSharedRef<SWidget> ULabVRGameViewportClient::GetVRWidgetRoot()
{
	EnsureVRRoot();
	return VRRoot.ToSharedRef();
}

void ULabVRGameViewportClient::RefreshVRRouting()
{
	// RemoveAllViewportWidgets is not virtual in UGameViewportClient.  The
	// collapsed marker is owned solely by the real viewport, so its expiry tells
	// us that Unreal cleared the viewport and the mirrored VR host must also clear.
	if (bLifetimeMarkerInstalled && !ViewportLifetimeMarker.IsValid())
	{
		ResetVRWidgets();
		bLifetimeMarkerInstalled = false;
	}
}

bool ULabVRGameViewportClient::HasVRWidgets()
{
	RefreshVRRouting();
	return VRWidgets.Num() > 0;
}

bool ULabVRGameViewportClient::HasInteractiveVRWidgets()
{
	RefreshVRRouting();
	if (VRWidgets.IsEmpty())
	{
		return false;
	}

	for (TObjectIterator<UUserWidget> It; It; ++It)
	{
		UUserWidget* UserWidget = *It;
		if (!IsValid(UserWidget) || UserWidget->GetWorld() != GetWorld()
			|| !UserWidget->IsInViewport() || !UserWidget->IsVisible()
			|| !UserWidget->WidgetTree)
		{
			continue;
		}

		bool bInteractive = false;
		UserWidget->WidgetTree->ForEachWidget([&bInteractive](UWidget* Widget)
		{
			if (bInteractive || !IsValid(Widget) || !Widget->IsVisible() || !Widget->GetIsEnabled())
			{
				return;
			}
			bInteractive = Widget->IsA<UButton>() || Widget->IsA<UCheckBox>()
				|| Widget->IsA<USlider>() || Widget->IsA<USpinBox>()
				|| Widget->IsA<UComboBoxString>() || Widget->IsA<UEditableText>()
				|| Widget->IsA<UEditableTextBox>();
		});

		if (bInteractive)
		{
			return true;
		}
	}
	return false;
}
