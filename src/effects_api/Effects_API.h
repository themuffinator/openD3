#ifndef _EFFECTS_API_H_INC_
#define _EFFECTS_API_H_INC_

#include "EffectsInterface.h"

const int EFFECTS_API_VERSION = 2;

class idSys;
class idCommon;
class idCmdSystem;
class idCVarSystem;
class idFileSystem;
class idNetworkSystem;
class idRenderSystem;
class idSoundSystem;
class idRenderModelManager;
class idUserInterfaceManager;
class idDeclManager;
class idAASFileManager;
class idCollisionModelManager;
class idGame;
class idGameEdit;
class idSession;
class idDecl;

typedef void (*Effects_SetRuntimePointers_t)(idGame* game, idGameEdit* gameEdit, idSession* session);
typedef idDecl* (*Effects_AllocDeclEffect_t)(void);

struct effectsImport_t {
	int						version;
	idSys*						sys;
	idCommon*					common;
	idCmdSystem*				cmdSystem;
	idCVarSystem*				cvarSystem;
	idFileSystem*				fileSystem;
	idNetworkSystem*			networkSystem;
	idRenderSystem*				renderSystem;
	idSoundSystem*				soundSystem;
	idRenderModelManager*		renderModelManager;
	idUserInterfaceManager*		uiManager;
	idDeclManager*				declManager;
	idAASFileManager*			AASFileManager;
	idCollisionModelManager*	collisionModelManager;
	idGame*						game;
	idGameEdit*					gameEdit;
	idSession*					session;
};
struct effectsExport_t {
	int						version;
	rvEffectsManager*			effects;
	rvDeclEffectEdit*			declEffectEdit;
	Effects_SetRuntimePointers_t	SetRuntimePointers;
	Effects_AllocDeclEffect_t		AllocDeclEffect;
};

extern "C" {
typedef effectsExport_t* (*GetEffectsAPI_t)(effectsImport_t* import);
}

extern Effects_AllocDeclEffect_t	effectsAllocDeclEffect;

#endif // _EFFECTS_API_H_INC_
