// Copyright (C) 2026 DarkMatter Productions. GPL-3.0-or-later.
#ifndef OPEND3_LEGACY_GUI_LAYOUT_H
#define OPEND3_LEGACY_GUI_LAYOUT_H

/*
================
openD3_ParseScreenStretchToken

"screenstretchx": none, fill, left or right (or 0 to 3); "screenstretchy":
none, fill, top or bottom.
================
*/
inline bool openD3_ParseScreenStretchToken( const char *token, bool vertical, unsigned char &out ) {
	if ( token == NULL || token[0] == '\0' ) {
		return false;
	}
	if ( token[0] >= '0' && token[0] <= '9' ) {
		out = static_cast<unsigned char>( idMath::ClampInt( idWindow::SCREEN_STRETCH_NONE, idWindow::SCREEN_STRETCH_TRAILING, atoi( token ) ) );
		return true;
	}
	if ( !idStr::Icmp( token, "none" ) ) {
		out = idWindow::SCREEN_STRETCH_NONE;
	} else if ( !idStr::Icmp( token, "fill" ) || !idStr::Icmp( token, "both" ) ) {
		out = idWindow::SCREEN_STRETCH_FILL;
	} else if ( !idStr::Icmp( token, vertical ? "top" : "left" ) ) {
		out = idWindow::SCREEN_STRETCH_LEADING;
	} else if ( !idStr::Icmp( token, vertical ? "bottom" : "right" ) ) {
		out = idWindow::SCREEN_STRETCH_TRAILING;
	} else {
		return false;
	}
	return true;
}

/*
================
openD3_ApplyScreenStretchAxis

Moves the leading edge out by leadOut and the trailing edge by trailOut, when
the stretch asks for them, on one axis of a rectangle. A negative extent only
mirrors the material (idDeviceContext::DrawMaterial): the rectangle still runs
from pos to pos + |extent|. An extent of zero is left alone. Returns how far
the origin moved.
================
*/
inline float openD3_ApplyScreenStretchAxis( unsigned char stretch, float leadOut, float trailOut, float &pos, float &extent ) {
	// A window collapsed to nothing on this axis (a closed dialog, which
	// hides its contents that way) stays collapsed.
	if ( stretch == idWindow::SCREEN_STRETCH_NONE || extent == 0.0f ) {
		return 0.0f;
	}
	const float lead = ( stretch == idWindow::SCREEN_STRETCH_FILL || stretch == idWindow::SCREEN_STRETCH_LEADING ) ? leadOut : 0.0f;
	const float trail = ( stretch == idWindow::SCREEN_STRETCH_FILL || stretch == idWindow::SCREEN_STRETCH_TRAILING ) ? trailOut : 0.0f;
	pos -= lead;
	extent += ( extent < 0.0f ) ? -( lead + trail ) : ( lead + trail );
	return -lead;
}

#endif
