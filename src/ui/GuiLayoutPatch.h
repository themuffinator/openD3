// Copyright (C) 2026 DarkMatter Productions. GPL-3.0-or-later.
#ifndef OPEND3_GUI_LAYOUT_PATCH_H
#define OPEND3_GUI_LAYOUT_PATCH_H

/*
===============================================================================

	GUI layout patches

	A layout patch adds window properties to a stock GUI as it is parsed, as if
	the GUI's own definition of each named window had carried them. openD3 uses
	them to give the retail Doom 3 menus and HUDs their wide and tall screen
	layout (screenalignx, screenstretchx and the rest) without shipping copies of
	the retail GUI scripts.

	Patch files are guis/layouts/*.layout. Each holds blocks of this form:

		gui "guis/hud.gui" {
			window Border, BgL, Lines* {
				screenalignx left
				screenaligny bottom
			}
		}

	The gui pattern and the window names may use the * and ? wildcards and match
	without regard to case. "name#2" names the second window the GUI defines
	under that name, for the scripts that reuse one. A window's properties are read by the same parser as
	the GUI's own, after the window's own properties and before its expressions
	are first evaluated. Every matching block applies, in file order, then in the
	order of the files' names.

	A GUI that a mod ships itself (idLegacyHudLayout::ModOwns) takes no patch,
	and ui_widescreenLayouts 0 turns patches off.

===============================================================================
*/

class idWindow;

class idGuiLayoutPatchSet {
public:
	struct Entry {
		idStrList	windows;		// name patterns
		idStr		body;			// property text
		idStr		origin;			// file:line, for warnings
	};

	bool			IsEmpty() const { return entries.Num() == 0; }
	// The entries point into the shared table, which a change of game
	// directory or reloadGuis rereads: a GUI holds them only while it parses.
	void			Clear() { entries.Clear(); seenNames.Clear(); seenCounts.Clear(); matchedPatterns.Clear(); }
	// Adds every matching block's properties to the window.
	void			Apply( idWindow *window ) const;
	// With ui_widescreenLayoutsDebug, names the patterns no window matched.
	void			ReportUnmatched( const char *guiSource ) const;

	idList<const Entry *> entries;

private:
	// How many windows of each name have parsed, for "name#N".
	mutable idStrList	seenNames;
	mutable idList<int>	seenCounts;
	// Per entry, a bit for each of its first 32 patterns that matched.
	mutable idList<unsigned int> matchedPatterns;
	friend class idGuiLayoutPatches;
};

class idGuiLayoutPatches {
public:
	// The patches for one GUI source path, empty when none apply.
	static void		Collect( const char *guiSource, idGuiLayoutPatchSet &out );
	// Forgets the parsed patch files, so the next GUI load reads them again.
	static void		Invalidate();
	static int		NumEntries();
};

#endif
