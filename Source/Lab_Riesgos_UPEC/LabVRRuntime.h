#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Subsystems/WorldSubsystem.h"
#include "LabVRRuntime.generated.h"

class UCameraComponent;
class UMotionControllerComponent;
class UWidgetComponent;
class UWidgetInteractionComponent;
class UStaticMeshComponent;
class UStereoLayerComponent;
class USoundBase;
class UAudioComponent;
class ACharacter;
struct FInputKeyEventArgs;
class FLabVRInputProcessor;

/** Adapts the existing simulator at runtime. No duplicate gameplay or widget instances. */
UCLASS()
class LAB_RIESGOS_UPEC_API ALabVRRuntime : public AActor
{
	GENERATED_BODY()
public:
	ALabVRRuntime();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
	bool HandleVRKey(const FKey& Key, bool bPressed, bool bRepeat);
	bool HandleVRAxis(const FKey& Key, float Value);
	bool IsVRRunning() const { return bVRRunning; }

private:
	void ActivateVR(APlayerController* PC);
	void ConfigurePawn(APlayerController* PC);
	void UpdateTracking(float DeltaSeconds, APlayerController* PC);
	void UpdateInterface(APlayerController* PC);
	void UpdatePackagedAudioFallback(APlayerController* PC);
	void SnapTurn(float Degrees);
	void SetAction(int32 Index, bool bPressed);
	void SendGameKey(FKey Key, bool bPressed);
	void ReleaseActions();

	UPROPERTY() TObjectPtr<USceneComponent> TrackingRoot;
	UPROPERTY() TObjectPtr<UCameraComponent> MenuCamera;
	UPROPERTY() TObjectPtr<UMotionControllerComponent> LeftAim;
	UPROPERTY() TObjectPtr<UMotionControllerComponent> RightAim;
	UPROPERTY() TObjectPtr<UWidgetInteractionComponent> LeftPointer;
	UPROPERTY() TObjectPtr<UWidgetInteractionComponent> RightPointer;
	UPROPERTY() TObjectPtr<UWidgetComponent> InterfacePanel;
	UPROPERTY() TObjectPtr<UStereoLayerComponent> InterfaceLayer;
	UPROPERTY() TObjectPtr<UStaticMeshComponent> LeftRay;
	UPROPERTY() TObjectPtr<UStaticMeshComponent> RightRay;
	UPROPERTY() TObjectPtr<UCameraComponent> ActiveCamera;
	UPROPERTY() TObjectPtr<USoundBase> PackagedApagarEstufaSound;
	UPROPERTY() TObjectPtr<USoundBase> PackagedLiquidoHirviendoSound;
	UPROPERTY() TObjectPtr<UAudioComponent> PackagedLiquidoLoop;
	TWeakObjectPtr<APawn> CurrentPawn;
	TWeakObjectPtr<APawn> AudioFallbackPawn;
	TSharedPtr<FLabVRInputProcessor> InputProcessor;
	FVector2D MoveAxis = FVector2D::ZeroVector;
	FVector TrackingOffset = FVector::ZeroVector;
	float TurnAxis = 0.f;
	float TrackingYaw = 0.f;
	float UIRefresh = 0.f;
	bool bVRRunning = false;
	bool bConfiguredPawn = false;
	bool bTurnReady = true;
	bool bModal = false;
	bool bWasModal = false;
	bool bLastEstufaAreaMediosApagada = false;
	bool bActions[4] = {false,false,false,false};
	bool bGameKeys[4] = {false,false,false,false};
	bool bPointerKeys[2] = {false,false};
};

UCLASS()
class LAB_RIESGOS_UPEC_API ULabVRWorldSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()
public:
	virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
	virtual void OnWorldBeginPlay(UWorld& InWorld) override;
};
