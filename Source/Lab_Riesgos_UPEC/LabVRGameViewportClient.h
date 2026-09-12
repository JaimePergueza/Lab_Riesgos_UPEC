#pragma once

#include "CoreMinimal.h"
#include "Engine/GameViewportClient.h"
#include "LabVRGameViewportClient.generated.h"

class SOverlay;
class SWidget;

/**
 * Keeps the simulator's existing UMG instances intact.  With an OpenXR headset
 * active, viewport widgets are hosted in a Slate overlay that the VR runtime
 * displays and points at; without a headset Unreal's normal desktop viewport
 * path is unchanged.
 */
UCLASS(Transient)
class LAB_RIESGOS_UPEC_API ULabVRGameViewportClient : public UGameViewportClient
{
	GENERATED_BODY()

public:
	virtual void AddViewportWidgetContent(TSharedRef<SWidget> ViewportContent, int32 ZOrder = 0) override;
	virtual void RemoveViewportWidgetContent(TSharedRef<SWidget> ViewportContent) override;
	virtual void AddViewportWidgetForPlayer(ULocalPlayer* Player, TSharedRef<SWidget> ViewportContent, int32 ZOrder) override;
	virtual void RemoveViewportWidgetForPlayer(ULocalPlayer* Player, TSharedRef<SWidget> ViewportContent) override;

	TSharedRef<SWidget> GetVRWidgetRoot();
	void RefreshVRRouting();
	bool HasVRWidgets();
	bool HasInteractiveVRWidgets();

private:
	struct FVRWidgetEntry
	{
		TSharedPtr<SWidget> Widget;
		TWeakObjectPtr<ULocalPlayer> Player;
		int32 ZOrder = 0;
	};

	bool ShouldRouteToVR() const;
	void EnsureVRRoot();
	void EnsureLifetimeMarker();
	void AddToVR(TSharedRef<SWidget> Widget, int32 ZOrder, ULocalPlayer* Player);
	bool RemoveFromVR(TSharedRef<SWidget> Widget);
	void ResetVRWidgets();

	TSharedPtr<SOverlay> VRRoot;
	TArray<FVRWidgetEntry> VRWidgets;
	TWeakPtr<SWidget> ViewportLifetimeMarker;
	bool bLifetimeMarkerInstalled = false;
};
