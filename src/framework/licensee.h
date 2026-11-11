
/*
===============================================================================

	Definitions for information that is related to a licensee's game name and location.

===============================================================================
*/

#include "opend3_version_generated.h"

// RAVEN BEGIN
// rjohnson: this is the name of the game we are making
#define PROJECT_NAME					"openD3"
#define PROJECT_AUTHOR					"themuffinator"
#define PROJECT_COMPANY				"DarkMatter Productions"
#define PROJECT_VERSION				OPEND3_VERSION_SHORT
#define PROJECT_VERSION_FULL			OPEND3_VERSION
#define PROJECT_VERSION_DATE			OPEND3_VERSION_DATE
#define PROJECT_WEBSITE				"www.darkmatter-quake.com"
#define PROJECT_REPO					"https://github.com/themuffinator/openD3"
#define PROJECT_RELEASES_URL			PROJECT_REPO "/releases"

#define GAME_NAME						PROJECT_NAME			// appears on errors and secondary windows
#define GAME_ICON						"assets/icons/doom3.ico"

// caption of the main game window: "openD3 - Version: 0.0.1-dev (2026-11-10)"
#define GAME_WINDOW_TITLE				PROJECT_NAME " - Version: " PROJECT_VERSION " (" PROJECT_VERSION_DATE ")"

#define ENGINE_VERSION					PROJECT_NAME " " PROJECT_VERSION

// jnewquist: build type
#if defined(_DEBUG)
#define GAME_BUILD_TYPE					"Debug"
#elif defined(_MPBETA)
#define GAME_BUILD_TYPE					"MPBeta"
#elif defined(_FINAL)
#define GAME_BUILD_TYPE					""
#elif defined(_RELEASE)
#define	GAME_BUILD_TYPE					""
#endif

// Ensure GAME_BUILD_TYPE is always defined (some build systems only define NDEBUG).
#ifndef GAME_BUILD_TYPE
#define GAME_BUILD_TYPE					""
#endif

// paths
#define	CD_BASEDIR						"openD3"
#define	BASE_GAMEDIR					"base"
#define	BASE_MPGAMEDIR					"base"
// BASE_GAMEDIR holds the retail Doom 3 paks; OPEND3_GAMEDIR holds openD3's
// own game module and runtime content.
#define OPEND3_GAMEDIR					"baseod3"
// Resurrection of Evil's retail directory; selects the game-d3xp module.
#define OPEND3_EXPANSION_GAMEDIR			"d3xp"
#define	DEMO_GAMEDIR					"demo"
#define	GAME_PLAYERDEFNAME				"player_doommarine"
#define GAME_PLAYERDEFNAME_MP			"player_doommarine_mp"

// filenames
#if defined( _M_X64 ) || defined( __x86_64__ )
	#define OPEND3_BINARY_ARCH			"x64"
#elif defined( _M_IX86 ) || defined( __i386__ )
	#define OPEND3_BINARY_ARCH			"x86"
#elif defined( _M_ARM64 ) || defined( __aarch64__ )
	#define OPEND3_BINARY_ARCH			"arm64"
#else
	#define OPEND3_BINARY_ARCH			"unknown"
#endif
#define	CD_EXE							PROJECT_NAME "-client_" OPEND3_BINARY_ARCH ".exe"

#ifdef _XENON
#define CONFIG_FILE						"save:/openD3Config.cfg"
#else
#define CONFIG_FILE						"openD3Config.cfg"
#endif

// base folder where the source code lives
#define SOURCE_CODE_BASE_FOLDER			"code"

#define DEVELOPER_DOMAIN				"darkmatter-quake.com"
// RAVEN END


// RAVEN BEGIN
// rjohnson: changed the host to our temp address
// default idnet host address
#ifndef IDNET_HOST
	#define IDNET_HOST					"q4master.idsoftware.com"
#endif
// RAVEN END

// default idnet master port
#ifndef IDNET_MASTER_PORT
	#define IDNET_MASTER_PORT			"27650"
#endif

#ifndef MOTD_HOST
	#define MOTD_HOST					"q4m-test.ravensoft.com"
#endif

#ifndef MOTD_PORT
	#define MOTD_PORT					"27700"
#endif

// default network server port
#ifndef PORT_SERVER
//RAVEN BEGIN
#define	PORT_SERVER					28004
//RAVEN END
#endif

// Q4TV default network repeater port
#ifndef PORT_REPEATER
#define PORT_REPEATER					28104
#endif

#ifndef PORT_HTTP
#define PORT_HTTP					28004
#endif

// broadcast scan this many ports after PORT_SERVER so a single machine can run multiple servers
#define	NUM_SERVER_PORTS				4

// see ASYNC_PROTOCOL_VERSION
// use a different major for each game
// RAVEN BEGIN
// ddynerman: rev ASYNC_PROTOCOL_MAJOR to 2 for Quake 4
#define ASYNC_PROTOCOL_MAJOR			2
// RAVEN END

// The game name openD3 writes into, and requires of, a savegame header.
#define SAVEGAME_GAME_NAME_DOOM3				"Doom3"
#define SAVEGAME_VERSION						1834
#define LEGACY_OPEND3_SAVEGAME_VERSION			0
#define LEGACY_OPEND3_SAVEGAME_VERSION_ALT		1

// editor info
#define EDITOR_WINDOWTEXT				"QuakeEdit"

// win32 info
#define WIN32_CONSOLE_CLASS				"openD3 WinConsole"
#define WIN32_SPLASH_CLASS				"openD3 Splash"
#define	WIN32_WINDOW_CLASS_NAME			"openD3"
#define	WIN32_FAKE_WINDOW_CLASS_NAME	"OPEND3_WGL_FAKE"

#ifdef __linux__
	#define DEFAULT_BASE_PATH				"/usr/local/games/opend3"
#elif defined( MACOS_X )
	#define DEFAULT_BASE_PATH				"/Applications/openD3"
#endif

// CD Key file info
#define CDKEY_FILE						"doomkey"
#define CDKEY_TEXT						"\n// Do not give this file to ANYONE.\n" \
										"// id Software and Activision will NOT ask you to send this file to them.\n"

// FIXME: Update to Doom
// Product ID. Stored in "productid.txt".
//										This file is copyright 1999 Id Software, and may not be duplicated except during a licensed installation of the full commercial version of Quake 3:Arena
#undef PRODUCT_ID
#define PRODUCT_ID						220, 129, 255, 108, 244, 163, 171, 55, 133, 65, 199, 36, 140, 222, 53, 99, 65, 171, 175, 232, 236, 193, 210, 250, 169, 104, 231, 231, 21, 201, 170, 208, 135, 175, 130, 136, 85, 215, 71, 23, 96, 32, 96, 83, 44, 240, 219, 138, 184, 215, 73, 27, 196, 247, 55, 139, 148, 68, 78, 203, 213, 238, 139, 23, 45, 205, 118, 186, 236, 230, 231, 107, 212, 1, 10, 98, 30, 20, 116, 180, 216, 248, 166, 35, 45, 22, 215, 229, 35, 116, 250, 167, 117, 3, 57, 55, 201, 229, 218, 222, 128, 12, 141, 149, 32, 110, 168, 215, 184, 53, 31, 147, 62, 12, 138, 67, 132, 54, 125, 6, 221, 148, 140, 4, 21, 44, 198, 3, 126, 12, 100, 236, 61, 42, 44, 251, 15, 135, 14, 134, 89, 92, 177, 246, 152, 106, 124, 78, 118, 80, 28, 42
#undef PRODUCT_ID_LENGTH
#define PRODUCT_ID_LENGTH				152

#define CONFIG_SPEC						"config.spec"
