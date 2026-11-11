#ifndef _BSE_API_H_INC_
#define _BSE_API_H_INC_

#include "BSEInterface.h"

class idDecl;

typedef idDecl* (*BSE_AllocDeclEffect_t)(void);

rvBSEManager*				openD3_GetIntegratedBSEManager( void );
rvDeclEffectEdit*			openD3_GetIntegratedBSEDeclEffectEdit( void );
idDecl*						openD3_AllocIntegratedBSEDeclEffect( void );
bool						openD3_IsIntegratedBSEDeclEffect( const idDecl *decl );

extern BSE_AllocDeclEffect_t	bseAllocDeclEffect;

#endif // _BSE_API_H_INC_
