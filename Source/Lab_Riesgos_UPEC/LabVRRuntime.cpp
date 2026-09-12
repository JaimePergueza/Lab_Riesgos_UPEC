#include "LabVRRuntime.h"
#include "LabVRGameViewportClient.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/AudioComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/WidgetComponent.h"
#include "Components/WidgetInteractionComponent.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Engine/World.h"
#include "Framework/Application/IInputProcessor.h"
#include "Framework/Application/SlateApplication.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "HeadMountedDisplayFunctionLibrary.h"
#include "IXRTrackingSystem.h"
#include "InputKeyEventArgs.h"
#include "Kismet/GameplayStatics.h"
#include "MotionControllerComponent.h"
#include "Components/StereoLayerComponent.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Sound/SoundBase.h"
#include "UObject/ConstructorHelpers.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogLabVR, Log, All);

class FLabVRInputProcessor final : public IInputProcessor
{
public:
	explicit FLabVRInputProcessor(ALabVRRuntime* InOwner) : Owner(InOwner) {}
	virtual void Tick(float, FSlateApplication&, TSharedRef<ICursor>) override {}
	virtual bool HandleKeyDownEvent(FSlateApplication&, const FKeyEvent& Event) override
	{ return Owner.IsValid() && Owner->HandleVRKey(Event.GetKey(), true, Event.IsRepeat()); }
	virtual bool HandleKeyUpEvent(FSlateApplication&, const FKeyEvent& Event) override
	{ return Owner.IsValid() && Owner->HandleVRKey(Event.GetKey(), false, false); }
	virtual bool HandleAnalogInputEvent(FSlateApplication&, const FAnalogInputEvent& Event) override
	{ return Owner.IsValid() && Owner->HandleVRAxis(Event.GetKey(), Event.GetAnalogValue()); }
private:
	TWeakObjectPtr<ALabVRRuntime> Owner;
};

ALabVRRuntime::ALabVRRuntime()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bTickEvenWhenPaused = true;
	PrimaryActorTick.TickGroup = TG_PrePhysics;
	TrackingRoot = CreateDefaultSubobject<USceneComponent>(TEXT("VRTrackingOrigin"));
	SetRootComponent(TrackingRoot);
	MenuCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("VRMenuCamera"));
	MenuCamera->SetupAttachment(TrackingRoot);
	MenuCamera->bUsePawnControlRotation = false;
	MenuCamera->bLockToHmd = true;
	MenuCamera->SetAutoActivate(false);
	LeftAim = CreateDefaultSubobject<UMotionControllerComponent>(TEXT("VRLeftAim"));
	RightAim = CreateDefaultSubobject<UMotionControllerComponent>(TEXT("VRRightAim"));
	LeftAim->SetupAttachment(TrackingRoot);
	RightAim->SetupAttachment(TrackingRoot);
	LeftAim->SetTrackingMotionSource(TEXT("LeftAim"));
	RightAim->SetTrackingMotionSource(TEXT("RightAim"));
	LeftPointer = CreateDefaultSubobject<UWidgetInteractionComponent>(TEXT("VRLeftPointer"));
	RightPointer = CreateDefaultSubobject<UWidgetInteractionComponent>(TEXT("VRRightPointer"));
	LeftPointer->SetupAttachment(LeftAim);
	RightPointer->SetupAttachment(RightAim);
	LeftPointer->PointerIndex = 0;
	RightPointer->PointerIndex = 1;
	for (UWidgetInteractionComponent* Pointer : {LeftPointer.Get(), RightPointer.Get()})
	{
		Pointer->VirtualUserIndex = 0;
		Pointer->InteractionDistance = 500.f;
		Pointer->InteractionSource = EWidgetInteractionSource::World;
		Pointer->TraceChannel = ECC_GameTraceChannel1;
		Pointer->bShowDebug = false;
		Pointer->SetTickableWhenPaused(true);
		Pointer->SetAutoActivate(false);
	}
	InterfacePanel = CreateDefaultSubobject<UWidgetComponent>(TEXT("OriginalWidgetPanel"));
	InterfacePanel->SetupAttachment(TrackingRoot);
	InterfacePanel->SetWidgetSpace(EWidgetSpace::World);
	InterfacePanel->SetDrawSize(FVector2D(1920,1080));
	InterfacePanel->SetBlendMode(EWidgetBlendMode::Transparent);
	InterfacePanel->SetTwoSided(true);
	InterfacePanel->SetBackgroundColor(FLinearColor::Transparent);
	InterfacePanel->SetTickWhenOffscreen(true);
	InterfacePanel->SetTickableWhenPaused(true);
	InterfacePanel->SetWindowFocusable(true);
	InterfacePanel->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	InterfacePanel->SetCollisionResponseToAllChannels(ECR_Ignore);
	InterfacePanel->SetCollisionResponseToChannel(ECC_GameTraceChannel1,ECR_Block);
	InterfacePanel->SetVisibility(false);
	// Render the exact UMG panel through the compositor for clear text, also keep
	// its geometry for WidgetInteraction hit tests and the monitor spectator view.
	InterfaceLayer = CreateDefaultSubobject<UStereoLayerComponent>(TEXT("OriginalWidgetStereoLayer"));
	InterfaceLayer->SetupAttachment(TrackingRoot);
	InterfaceLayer->bLiveTexture = true;
	InterfaceLayer->bSupportsDepth = false;
	InterfaceLayer->bNoAlphaChannel = false;
	InterfaceLayer->SetVisibility(false);
	LeftRay = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VRLeftRay"));
	RightRay = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VRRightRay"));
	LeftRay->SetupAttachment(LeftAim);
	RightRay->SetupAttachment(RightAim);
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube"));
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> RayMaterial(TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	static ConstructorHelpers::FObjectFinder<USoundBase> ApagarEstufaSound(TEXT("/Game/FirstPerson/Textos/ApagarEstufa.ApagarEstufa"));
	static ConstructorHelpers::FObjectFinder<USoundBase> LiquidoHirviendoWave(TEXT("/Game/FirstPerson/Textos/LiquidoHirviendo.LiquidoHirviendo"));
	if (ApagarEstufaSound.Succeeded())
	{
		PackagedApagarEstufaSound = ApagarEstufaSound.Object;
	}
	if (LiquidoHirviendoWave.Succeeded())
	{
		PackagedLiquidoHirviendoSound = LiquidoHirviendoWave.Object;
	}
	for (UStaticMeshComponent* Ray : {LeftRay.Get(),RightRay.Get()})
	{
		Ray->SetStaticMesh(Cube.Object);
		Ray->SetMaterial(0,RayMaterial.Object);
		Ray->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Ray->SetCastShadow(false);
		Ray->SetVisibility(false);
		Ray->SetRelativeScale3D(FVector(1.5f,.012f,.012f));
		Ray->SetRelativeLocation(FVector(75.f,0,0));
	}
}

void ALabVRRuntime::BeginPlay()
{
	Super::BeginPlay();
	if (FSlateApplication::IsInitialized())
	{
		InputProcessor = MakeShared<FLabVRInputProcessor>(this);
		FSlateApplication::Get().RegisterInputPreProcessor(InputProcessor,0);
	}
	UE_LOG(LogLabVR, Display, TEXT("Packaged area-medios audio: apagar=%s, hervir=%s"),
		*GetNameSafe(PackagedApagarEstufaSound), *GetNameSafe(PackagedLiquidoHirviendoSound));
}

void ALabVRRuntime::ActivateVR(APlayerController* PC)
{
	bVRRunning = true;
	UHeadMountedDisplayFunctionLibrary::SetTrackingOrigin(EHMDTrackingOrigin::LocalFloor);
	FVector Location; FRotator Rotation;
	PC->GetPlayerViewPoint(Location,Rotation);
	TrackingYaw = Rotation.Yaw;
	SetActorLocationAndRotation(Location-FVector(0,0,170),FRotator(0,TrackingYaw,0));
	UE_LOG(LogLabVR,Display,TEXT("PC VR active: original gameplay and original widgets, OpenXR."));
}

void ALabVRRuntime::ConfigurePawn(APlayerController* PC)
{
	APawn* Pawn=PC->GetPawn();
	if (bConfiguredPawn && CurrentPawn.Get()==Pawn) return;
	CurrentPawn=Pawn;
	bConfiguredPawn=true;
	TrackingOffset=FVector::ZeroVector;
	ActiveCamera=MenuCamera;
	if (ACharacter* Character=Cast<ACharacter>(Pawn))
	{
		Character->bUseControllerRotationYaw=false;
		Character->bUseControllerRotationPitch=false;
		Character->bUseControllerRotationRoll=false;
		Character->GetCharacterMovement()->bOrientRotationToMovement=false;
		Character->GetCharacterMovement()->bUseControllerDesiredRotation=false;
		Character->GetCharacterMovement()->MaxWalkSpeed=150.f;
		TrackingYaw=Character->GetActorRotation().Yaw;
		TInlineComponentArray<UCameraComponent*> Cameras(Character);
		for (auto* Camera:Cameras)
		{
			Camera->Deactivate();
			if (Camera->GetName().StartsWith(TEXT("FirstPersonCamera"))) ActiveCamera=Camera;
		}
		ActiveCamera->AttachToComponent(TrackingRoot,FAttachmentTransformRules::SnapToTargetNotIncludingScale);
		ActiveCamera->bUsePawnControlRotation=false;
		ActiveCamera->bLockToHmd=true;
		ActiveCamera->Activate(true);
		ActiveCamera->PostProcessSettings.bOverride_MotionBlurAmount=true;
		ActiveCamera->PostProcessSettings.MotionBlurAmount=0;
		Character->AddTickPrerequisiteActor(this);
		// Keep the EPP state/meshes for gameplay; avoid the desktop arms enclosing the headset.
		TInlineComponentArray<UPrimitiveComponent*> Meshes(Character);
		for (auto* Mesh:Meshes)
			if (Mesh->GetName().StartsWith(TEXT("FirstPersonMesh")) || Mesh->GetName().StartsWith(TEXT("FP_BataVisual")) || Mesh->GetName().StartsWith(TEXT("Mirror_")))
				Mesh->SetOwnerNoSee(true);
		if (FBoolProperty* Flag=FindFProperty<FBoolProperty>(Character->GetClass(),TEXT("bModoVRActivo")))
			Flag->SetPropertyValue_InContainer(Character,true);
		PC->SetViewTarget(Character);
	}
	else
	{
		MenuCamera->Activate(true);
		PC->SetViewTarget(this);
	}
	UE_LOG(LogLabVR,Display,TEXT("VR camera configured for %s"),*GetNameSafe(Pawn));
}

void ALabVRRuntime::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	APlayerController* PC=GetWorld()->GetFirstPlayerController();
	if (!PC || !PC->IsLocalController()) return;
	UpdatePackagedAudioFallback(PC);
	const bool bEnabled=!FParse::Param(FCommandLine::Get(),TEXT("nohmd")) && UHeadMountedDisplayFunctionLibrary::IsHeadMountedDisplayEnabled() && UHeadMountedDisplayFunctionLibrary::IsHeadMountedDisplayConnected();
	if (!bEnabled)
	{
		if (bVRRunning) ReleaseActions();
		// A temporary cable disconnect keeps the tracked pawn for reconnection.
		bVRRunning=false;
		InterfacePanel->SetVisibility(false);
		InterfaceLayer->SetVisibility(false);
		LeftRay->SetVisibility(false); RightRay->SetVisibility(false);
		return;
	}
	if (!bVRRunning) ActivateVR(PC);
	ConfigurePawn(PC);
	UpdateTracking(DeltaSeconds,PC);
	UIRefresh-=DeltaSeconds;
	if (UIRefresh<=0.f || GetWorld()->IsPaused())
	{
		UpdateInterface(PC);
		UIRefresh=.1f;
	}
	const bool bCanMove=!bModal && !GetWorld()->IsPaused() && !PC->IsMoveInputIgnored();
	if (bCanMove)
	{
		if (ACharacter* Character=Cast<ACharacter>(PC->GetPawn()))
		{
			FVector2D Axis=MoveAxis;
			const float Magnitude=FMath::Min(Axis.Size(),1.f);
			Axis=Axis.GetSafeNormal()*FMath::Clamp((Magnitude-.2f)/.8f,0.f,1.f);
			const FRotator Heading(0,ActiveCamera->GetComponentRotation().Yaw,0);
			Character->AddMovementInput(Heading.Vector(),Axis.Y);
			Character->AddMovementInput(FRotationMatrix(Heading).GetUnitAxis(EAxis::Y),Axis.X);
		}
		if (bTurnReady && FMath::Abs(TurnAxis)>.7f) { SnapTurn(FMath::Sign(TurnAxis)*30.f); bTurnReady=false; }
	}
	if (FMath::Abs(TurnAxis)<.25f) bTurnReady=true;
	// Aim and hit testing continue while UI-only input or pause is active.
	for (auto* Pointer:{LeftPointer.Get(),RightPointer.Get()}) Pointer->bEnableHitTesting=bModal;
	LeftPointer->SetActive(bModal); RightPointer->SetActive(bModal);
	const bool bLeftTracked=LeftAim->IsTracked(); const bool bRightTracked=RightAim->IsTracked();
	LeftRay->SetVisibility(bModal && bLeftTracked);
	RightRay->SetVisibility(bModal && bRightTracked);
	// HUD follows the headset. Modal panels stay fixed while the player selects buttons.
	if (!bModal || !bWasModal)
	{
		const FRotator Facing(0,ActiveCamera->GetComponentRotation().Yaw,0);
		const FVector Origin=ActiveCamera->GetComponentLocation()+Facing.Vector()*120.f;
		InterfacePanel->SetWorldLocationAndRotation(Origin,(Facing+FRotator(0,180,0)));
		InterfacePanel->SetWorldScale3D(FVector(.1f));
		InterfaceLayer->SetWorldLocationAndRotation(Origin,Facing);
		InterfaceLayer->SetQuadSize(FVector2D(192,108));
	}
	bWasModal=bModal;
}

void ALabVRRuntime::UpdatePackagedAudioFallback(APlayerController* PC)
{
#if UE_BUILD_SHIPPING
	APawn* Pawn = PC ? PC->GetPawn() : nullptr;
	if (!Pawn)
	{
		return;
	}
	auto ReadBool = [Pawn](const TCHAR* Name)
	{
		if (FBoolProperty* Flag = FindFProperty<FBoolProperty>(Pawn->GetClass(), Name))
		{
			return Flag->GetPropertyValue_InContainer(Pawn);
		}
		return false;
	};
	if (AudioFallbackPawn.Get() != Pawn)
	{
		AudioFallbackPawn = Pawn;
		bLastEstufaAreaMediosApagada = ReadBool(TEXT("bEstufaAreaMediosApagada"));
		if (PackagedLiquidoLoop)
		{
			PackagedLiquidoLoop->Stop();
			PackagedLiquidoLoop = nullptr;
		}
	}
	const bool bEstufaAreaMediosApagada = ReadBool(TEXT("bEstufaAreaMediosApagada"));
	const bool bLiquidoHirviendoActivo = ReadBool(TEXT("bLiquidoHirviendoActivo"));
	const bool bAreaMediosIniciada = ReadBool(TEXT("bAreaMediosIniciada"));
	if (bEstufaAreaMediosApagada && !bLastEstufaAreaMediosApagada && bAreaMediosIniciada)
	{
		if (PackagedApagarEstufaSound)
		{
			UGameplayStatics::PlaySound2D(this, PackagedApagarEstufaSound, 1.f);
		}
	}
	const bool bShouldBoil = bAreaMediosIniciada && bLiquidoHirviendoActivo && !bEstufaAreaMediosApagada;
	if (bShouldBoil && PackagedLiquidoHirviendoSound)
	{
		// The original Blueprint cue can be silent in Shipping; drive its source wave
		// from the same scene state and keep a single, explicit audio component.
		if (FObjectProperty* RefProperty = FindFProperty<FObjectProperty>(Pawn->GetClass(), TEXT("AudioLiquidoHirviendoRef")))
		{
			if (UAudioComponent* BlueprintAudio = Cast<UAudioComponent>(RefProperty->GetObjectPropertyValue_InContainer(Pawn)))
			{
				if (BlueprintAudio != PackagedLiquidoLoop && BlueprintAudio->IsPlaying()) BlueprintAudio->Stop();
			}
		}
		if (!IsValid(PackagedLiquidoLoop))
		{
			PackagedLiquidoLoop = UGameplayStatics::SpawnSound2D(this, PackagedLiquidoHirviendoSound, 0.75f, 1.f, 0.f, nullptr, false, false);
		}
		else if (!PackagedLiquidoLoop->IsPlaying())
		{
			PackagedLiquidoLoop->Play();
		}
	}
	else if (!bShouldBoil && PackagedLiquidoLoop)
	{
		PackagedLiquidoLoop->Stop();
		PackagedLiquidoLoop = nullptr;
	}
	bLastEstufaAreaMediosApagada = bEstufaAreaMediosApagada;
#endif
}

void ALabVRRuntime::UpdateTracking(float DeltaSeconds,APlayerController* PC)
{
	FRotator Orientation; FVector Position;
	UHeadMountedDisplayFunctionLibrary::GetOrientationAndPosition(Orientation,Position);
	ACharacter* Character=Cast<ACharacter>(PC->GetPawn());
	if (Character)
	{
		const FVector Floor=Character->GetActorLocation()-FVector(0,0,Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
		SetActorLocationAndRotation(Floor+TrackingOffset,FRotator(0,TrackingYaw,0));
		const FVector Head=GetActorTransform().TransformPosition(Position);
		FVector Delta(Head.X-Character->GetActorLocation().X,Head.Y-Character->GetActorLocation().Y,0);
		if (Delta.SizeSquared()>1.f && !GetWorld()->IsPaused() && !bModal)
		{
			const FVector Before=Character->GetActorLocation();
			FHitResult Hit;
			Character->AddActorWorldOffset(Delta,true,&Hit);
			TrackingOffset-=Character->GetActorLocation()-Before;
		}
	}
	// Existing Blueprint traces use this very camera in their own Tick.
	ActiveCamera->SetRelativeLocationAndRotation(Position,Orientation);
}

void ALabVRRuntime::UpdateInterface(APlayerController* PC)
{
	auto* Viewport=Cast<ULabVRGameViewportClient>(GetWorld()->GetGameViewport());
	if (!Viewport) return;
	Viewport->RefreshVRRouting();
	InterfacePanel->SetSlateWidget(Viewport->GetVRWidgetRoot());
	const bool bWidgets=Viewport->HasVRWidgets();
	bModal=Viewport->HasInteractiveVRWidgets();
	InterfacePanel->SetVisibility(bWidgets);
	// The world widget is also the interaction surface. Keeping the optional
	// compositor layer hidden avoids drawing the same UI twice.
	InterfaceLayer->SetVisibility(false);
	if (bModal && !bWasModal) ReleaseActions();
}

void ALabVRRuntime::SnapTurn(float Degrees)
{
	const FVector Pivot=ActiveCamera->GetComponentLocation();
	const FQuat Turn(FVector::UpVector,FMath::DegreesToRadians(Degrees));
	TrackingOffset=Turn.RotateVector(TrackingOffset);
	if (ACharacter* Character=Cast<ACharacter>(CurrentPawn.Get()))
	{
		const FVector Before=Character->GetActorLocation();
		FVector After=Pivot+Turn.RotateVector(Before-Pivot); After.Z=Before.Z;
		FHitResult Hit; Character->SetActorLocation(After,true,&Hit);
		TrackingOffset+=After-Character->GetActorLocation();
		Character->SetActorRotation(FRotator(0,Character->GetActorRotation().Yaw+Degrees,0));
	}
	TrackingYaw+=Degrees;
}

bool ALabVRRuntime::HandleVRKey(const FKey& Key,bool bPressed,bool bRepeat)
{
	if (!bVRRunning) return false;
	const FName Name=Key.GetFName();
	int32 Index=INDEX_NONE;
	if (Name==TEXT("OculusTouch_Right_Trigger_Click") || Name==TEXT("OculusTouch_Right_A_Click")) Index=0;
	else if (Name==TEXT("OculusTouch_Right_Grip_Click")) Index=1;
	else if (Name==TEXT("OculusTouch_Left_Y_Click") || Name==TEXT("OculusTouch_Right_B_Click")) Index=2;
	else if (Name==TEXT("OculusTouch_Left_Trigger_Click")) Index=3;
	if (Index==INDEX_NONE) return false;
	if (!bRepeat) SetAction(Index,bPressed);
	return true;
}

bool ALabVRRuntime::HandleVRAxis(const FKey& Key,float Value)
{
	if (!bVRRunning) return false;
	const FName Name=Key.GetFName();
	if (Name==TEXT("OculusTouch_Left_Thumbstick_X")) MoveAxis.X=Value;
	else if (Name==TEXT("OculusTouch_Left_Thumbstick_Y")) MoveAxis.Y=Value;
	else if (Name==TEXT("OculusTouch_Right_Thumbstick_X")) TurnAxis=Value;
	else if (Name==TEXT("OculusTouch_Right_Trigger_Axis")) { if(Value>.65f) SetAction(0,true); else if(Value<.25f) SetAction(0,false); }
	else if (Name==TEXT("OculusTouch_Right_Grip_Axis")) { if(Value>.65f) SetAction(1,true); else if(Value<.25f) SetAction(1,false); }
	else if (Name==TEXT("OculusTouch_Left_Trigger_Axis")) { if(Value>.65f) SetAction(3,true); else if(Value<.25f) SetAction(3,false); }
	else return false;
	return true;
}

void ALabVRRuntime::SetAction(int32 Index,bool bPressed)
{
	if (bActions[Index]==bPressed) return;
	bActions[Index]=bPressed;
	const FKey GameKey=Index==1 ? EKeys::R : Index==2 ? EKeys::P : EKeys::E;
	if (!bPressed)
	{
		if (bGameKeys[Index]) SendGameKey(GameKey,false);
		bGameKeys[Index]=false;
		if ((Index==0 || Index==3) && bPointerKeys[Index==0 ? 1:0])
		{
			(Index==0 ? RightPointer:LeftPointer)->ReleasePointerKey(EKeys::LeftMouseButton);
			bPointerKeys[Index==0 ? 1:0]=false;
		}
		return;
	}
	if (bModal)
	{
		if (Index==0 || Index==3)
		{
			auto* Pointer=Index==0 ? RightPointer.Get():LeftPointer.Get();
			Pointer->PressPointerKey(EKeys::LeftMouseButton);
			bPointerKeys[Index==0 ? 1:0]=true;
		}
		return;
	}
	if (Index!=3) { SendGameKey(GameKey,true); bGameKeys[Index]=true; }
}

void ALabVRRuntime::SendGameKey(FKey Key,bool bPressed)
{
	if (APlayerController* PC=GetWorld()->GetFirstPlayerController())
		PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key,bPressed?IE_Pressed:IE_Released,bPressed?1.f:0.f));
}

void ALabVRRuntime::ReleaseActions()
{
	for (int32 I=0;I<4;++I) { bActions[I]=true; SetAction(I,false); }
	MoveAxis=FVector2D::ZeroVector; TurnAxis=0;
}

void ALabVRRuntime::EndPlay(const EEndPlayReason::Type Reason)
{
	ReleaseActions();
	if (PackagedLiquidoLoop)
	{
		PackagedLiquidoLoop->Stop();
		PackagedLiquidoLoop = nullptr;
	}
	if (InputProcessor.IsValid() && FSlateApplication::IsInitialized())
		FSlateApplication::Get().UnregisterInputPreProcessor(InputProcessor);
	InputProcessor.Reset();
	Super::EndPlay(Reason);
}

bool ULabVRWorldSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
	const UWorld* World=Cast<UWorld>(Outer);
	return !IsRunningCommandlet() && World && (World->WorldType==EWorldType::Game || World->WorldType==EWorldType::PIE);
}

void ULabVRWorldSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
	Super::OnWorldBeginPlay(InWorld);
	FActorSpawnParameters Params;
	Params.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	Params.ObjectFlags|=RF_Transient;
	InWorld.SpawnActor<ALabVRRuntime>(Params);
}
