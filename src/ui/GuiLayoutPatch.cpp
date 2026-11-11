// Copyright (C) 2026 DarkMatter Productions. GPL-3.0-or-later.
#include "DeviceContext.h"
#include "Window.h"
#include "GuiLayoutPatch.h"

/*
===============================================================================

	GUI layout patches (GuiLayoutPatch.h)

===============================================================================
*/

idCVar ui_widescreenLayouts( "ui_widescreenLayouts", "1", CVAR_GUI | CVAR_ARCHIVE | CVAR_BOOL,
	"apply openD3's wide and tall screen layouts (guis/layouts/*.layout) to the stock menus and HUDs; takes effect as each GUI loads" );
idCVar ui_widescreenLayoutsDebug( "ui_widescreenLayoutsDebug", "0", CVAR_GUI | CVAR_INTEGER,
	"report each window a layout patch changes, and the patterns that match no window" );

namespace {

struct guiLayoutBlock_t {
	idStr guiPattern;
	idList<idGuiLayoutPatchSet::Entry *> entries;
};

struct guiLayoutTable_t {
	bool loaded = false;
	idStr gameDirs;		// the game directories the table was read under
	idList<guiLayoutBlock_t *> blocks;

	void Clear() {
		for ( int i = 0; i < blocks.Num(); i++ ) {
			blocks[i]->entries.DeleteContents( true );
		}
		blocks.DeleteContents( true );
		loaded = false;
	}
	~guiLayoutTable_t() { Clear(); }
};

guiLayoutTable_t layoutTable;

const int LAYOUT_LEXER_FLAGS = LEXFL_NOFATALERRORS | LEXFL_NOSTRINGCONCAT | LEXFL_ALLOWMULTICHARLITERALS |
	LEXFL_ALLOWBACKSLASHSTRINGCONCAT | LEXFL_ALLOWPATHNAMES;

/*
================
GlobMatch

The whole name against a pattern of * and ?, without regard to case.
(idStr::Filter accepts a name that only starts with the pattern.)
================
*/
bool GlobMatch( const char *pattern, const char *name ) {
	const char *starPattern = NULL;
	const char *starName = NULL;
	while ( *name ) {
		if ( *pattern == '*' ) {
			starPattern = ++pattern;
			starName = name;
		} else if ( *pattern == '?' || idStr::ToLower( *pattern ) == idStr::ToLower( *name ) ) {
			pattern++;
			name++;
		} else if ( starPattern != NULL ) {
			pattern = starPattern;
			name = ++starName;
		} else {
			return false;
		}
	}
	while ( *pattern == '*' ) {
		pattern++;
	}
	return *pattern == '\0';
}

/*
================
ReadNameList

Reads comma-separated names up to the opening brace, which it leaves for the
caller. The lexer splits a wildcard from the name around it, so tokens with no
space between them form one name.
================
*/
bool ReadNameList( idLexer &src, idStrList &names ) {
	idToken token;
	idStr current;
	while ( src.ReadToken( &token ) ) {
		if ( token == "{" || token == "," ) {
			if ( current.Length() ) {
				names.Append( current );
			}
			current.Clear();
			if ( token == "{" ) {
				src.UnreadToken( &token );
				return names.Num() > 0;
			}
			continue;
		}
		if ( current.Length() && token.WhiteSpaceBeforeToken() ) {
			names.Append( current );
			current.Clear();
		}
		current += token;
	}
	return false;
}

/*
================
ParseLayoutFile
================
*/
void ParseLayoutFile( const char *filePath ) {
	const idStr path = filePath;
	idLexer src( LAYOUT_LEXER_FLAGS );
	if ( !src.LoadFile( path ) ) {
		common->Warning( "Couldn't load GUI layout '%s'", path.c_str() );
		return;
	}

	idToken token;
	while ( src.ReadToken( &token ) ) {
		if ( token.Icmp( "gui" ) != 0 ) {
			src.Warning( "expected 'gui', found '%s'", token.c_str() );
			src.SkipBracedSection( false );
			continue;
		}
		idToken pattern;
		if ( !src.ReadToken( &pattern ) || !src.ExpectTokenString( "{" ) ) {
			return;
		}
		guiLayoutBlock_t *block = new guiLayoutBlock_t;
		block->guiPattern = pattern;
		block->guiPattern.BackSlashesToSlashes();
		layoutTable.blocks.Append( block );

		while ( src.ReadToken( &token ) && token != "}" ) {
			if ( token.Icmp( "window" ) != 0 ) {
				src.Warning( "expected 'window' or '}', found '%s'", token.c_str() );
				src.SkipBracedSection( false );
				continue;
			}
			idGuiLayoutPatchSet::Entry *entry = new idGuiLayoutPatchSet::Entry;
			entry->origin = va( "%s:%d", path.c_str(), src.GetLineNum() );
			if ( !ReadNameList( src, entry->windows ) ) {
				src.Warning( "window without names" );
				delete entry;
				return;
			}
			// The body without its braces, line breaks kept: a property the
			// window does not define reads to the end of its line.
			idStr body;
			src.ParseBracedSectionExact( body, -1 );
			const int open = body.Find( '{' );
			const int close = body.Last( '}' );
			if ( open >= 0 && close > open ) {
				body = body.Mid( open + 1, close - open - 1 );
			}
			entry->body = body;
			block->entries.Append( entry );
		}
	}
}

/*
================
LoadTable
================
*/
void LoadTable() {
	// The first GUIs can load before the game directory mounts, so the table
	// is read again whenever the game directories change.
	const char *active = fileSystem->GetActiveGameDir();
	const idStr gameDirs = va( "%s|%s|%s", active != NULL ? active : "",
		cvarSystem->GetCVarString( "fs_game" ), cvarSystem->GetCVarString( "fs_game_base" ) );
	if ( layoutTable.loaded && layoutTable.gameDirs == gameDirs ) {
		return;
	}
	layoutTable.Clear();
	layoutTable.loaded = true;
	layoutTable.gameDirs = gameDirs;
	idFileList *files = fileSystem->ListFiles( "guis/layouts", ".layout", true );
	int numFiles = 0;
	if ( files != NULL ) {
		numFiles = files->GetNumFiles();
		for ( int i = 0; i < numFiles; i++ ) {
			ParseLayoutFile( va( "guis/layouts/%s", files->GetFile( i ) ) );
		}
		fileSystem->FreeFileList( files );
	}
	if ( ui_widescreenLayoutsDebug.GetBool() ) {
		common->Printf( "GUI layouts: %d files, %d blocks (%s)\n", numFiles, layoutTable.blocks.Num(), gameDirs.c_str() );
	}
}

}	// namespace

/*
================
idGuiLayoutPatches::Collect
================
*/
void idGuiLayoutPatches::Collect( const char *guiSource, idGuiLayoutPatchSet &out ) {
	out.entries.Clear();
	out.seenNames.Clear();
	out.seenCounts.Clear();
	out.matchedPatterns.Clear();
	if ( guiSource == NULL || guiSource[0] == '\0' || !ui_widescreenLayouts.GetBool() ) {
		return;
	}
	LoadTable();
	idStr source = guiSource;
	source.BackSlashesToSlashes();
	for ( int i = 0; i < layoutTable.blocks.Num(); i++ ) {
		const guiLayoutBlock_t *block = layoutTable.blocks[i];
		if ( !GlobMatch( block->guiPattern, source ) ) {
			continue;
		}
		for ( int j = 0; j < block->entries.Num(); j++ ) {
			out.entries.Append( block->entries[j] );
			out.matchedPatterns.Append( 0 );
		}
	}
}

/*
================
idGuiLayoutPatches::Invalidate
================
*/
void idGuiLayoutPatches::Invalidate() {
	layoutTable.Clear();
}

/*
================
idGuiLayoutPatches::NumEntries
================
*/
int idGuiLayoutPatches::NumEntries() {
	LoadTable();
	int count = 0;
	for ( int i = 0; i < layoutTable.blocks.Num(); i++ ) {
		count += layoutTable.blocks[i]->entries.Num();
	}
	return count;
}

/*
================
idGuiLayoutPatchSet::Apply
================
*/
void idGuiLayoutPatchSet::Apply( idWindow *window ) const {
	if ( window == NULL || entries.Num() == 0 ) {
		return;
	}
	const char *name = window->GetName();
	if ( name == NULL || name[0] == '\0' ) {
		return;
	}
	if ( ui_widescreenLayoutsDebug.GetInteger() > 1 ) {
		common->Printf( "GUI layout: parsed %s\n", name );
	}
	int occurrence = 1;
	for ( int i = 0; i < seenNames.Num(); i++ ) {
		if ( seenNames[i].Icmp( name ) == 0 ) {
			occurrence = ++seenCounts[i];
			break;
		}
	}
	if ( occurrence == 1 ) {
		seenNames.Append( name );
		seenCounts.Append( 1 );
	}
	for ( int i = 0; i < entries.Num(); i++ ) {
		const Entry *entry = entries[i];
		bool matches = false;
		for ( int j = 0; j < entry->windows.Num(); j++ ) {
			const idStr &pattern = entry->windows[j];
			const int hash = pattern.Find( '#' );
			bool hit;
			if ( hash < 0 ) {
				hit = GlobMatch( pattern, name );
			} else {
				hit = atoi( pattern.c_str() + hash + 1 ) == occurrence &&
					GlobMatch( pattern.Left( hash ), name );
			}
			if ( hit ) {
				matches = true;
				if ( j < 32 ) {
					matchedPatterns[i] |= 1u << j;
				}
			}
		}
		if ( !matches ) {
			continue;
		}
		if ( ui_widescreenLayoutsDebug.GetBool() ) {
			common->Printf( "GUI layout: %s #%d <- %s\n", name, occurrence, entry->origin.c_str() );
		}
		idParser src( entry->body.c_str(), entry->body.Length(), entry->origin.c_str(), LAYOUT_LEXER_FLAGS );
		window->ApplyLayoutProperties( &src );
	}
}

/*
================
idGuiLayoutPatchSet::ReportUnmatched
================
*/
void idGuiLayoutPatchSet::ReportUnmatched( const char *guiSource ) const {
	if ( !ui_widescreenLayoutsDebug.GetBool() ) {
		return;
	}
	for ( int i = 0; i < entries.Num(); i++ ) {
		for ( int j = 0; j < entries[i]->windows.Num() && j < 32; j++ ) {
			if ( !( matchedPatterns[i] & ( 1u << j ) ) ) {
				common->Warning( "GUI layout %s: '%s' matches no window in %s", entries[i]->origin.c_str(),
					entries[i]->windows[j].c_str(), guiSource );
			}
		}
	}
}
