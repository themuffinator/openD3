// Copyright (C) 2026 DarkMatter Productions. GPL-3.0-or-later.
#pragma once
#include "retained/Interaction.h"

class idUserInterface;
// Observed afresh by an engine-owned, callback-free accessor. This is not a
// cached authorization token: the manager still checks its allocation registry,
// backend/document generation and the Runtime's exact editor barrier.
struct uiNativeTextRoute_t {
	idUserInterface* current = nullptr;
	std::uint64_t window = 0;
	bool inputAllowed = false;
};
using uiNativeTextRouteProbe_t = uiNativeTextRoute_t (*)(void*) noexcept;

// Private engine-thread endpoints. The probe must not allocate, dispatch events
// or enter foreign/native callbacks. The probe and its context outlive each call.
// Inputs/outputs/error may not alias. Failure preserves output values. No method
// enables a provider, infers text origin, pumps or writes accepted settings.
bool UI_NativeTextAttach(uiNativeTextRouteProbe_t,void*,const opend3::ui::TextEditorIdentity&,
	opend3::ui::NativeTextIdentity,opend3::ui::NativeTextEditorBarrier&,std::string&);
bool UI_NativeTextRefresh(uiNativeTextRouteProbe_t,void*,const opend3::ui::NativeTextEditorBarrier&,
	opend3::ui::NativeTextEditorView&,std::string&);
bool UI_NativeTextCurrent(uiNativeTextRouteProbe_t,void*,const opend3::ui::NativeTextEditorBarrier&) noexcept;
bool UI_NativeTextBegin(uiNativeTextRouteProbe_t,void*,const opend3::ui::NativeTextEditorBarrier&,
	const opend3::ui::NativeTextCollection&,opend3::ui::NativeTextEditorBarrier&,std::string&);
bool UI_NativeTextApply(uiNativeTextRouteProbe_t,void*,const opend3::ui::NativeTextEditorBarrier&,
	const opend3::ui::NativeTextOffer&,opend3::ui::NativeTextEditorReceipt&,std::string&);
bool UI_NativeTextComplete(uiNativeTextRouteProbe_t,void*,const opend3::ui::NativeTextEditorBarrier&,
	const opend3::ui::NativeTextCollection&,opend3::ui::NativeTextEditorBarrier&,std::string&);
#ifndef ID_DEDICATED
// Client-only; the dedicated server links no retained settlement owner.
std::unique_ptr<opend3::ui::Interaction::NativeSettlement> UI_NativeTextPrepareSettlement(
	uiNativeTextRouteProbe_t,void*,const opend3::ui::NativeTextEditorBarrier&,std::string&);
#endif
bool UI_NativeTextPublishSettlement(uiNativeTextRouteProbe_t,void*,
	opend3::ui::Interaction::NativeSettlement&,opend3::ui::NativeTextEditorReceipt&) noexcept;
// Teardown deliberately ignores current-route/input eligibility. Only the
// original allocation/backend/document/native/editor lease can be retired;
// editing revision progress does not redirect cleanup to a replacement lease.
bool UI_NativeTextRetireExact(opend3::ui::NativeTextIdentity,const opend3::ui::TextEditorIdentity&) noexcept;
// Callback/allocation-free inspection of the ORIGINAL allocation and actual
// stored native barrier. No route probe, resource preparation or policy check.
// Current document-generation invalidation alone cannot prove lease absence.
// Busy/unknown never authorizes disposal; this does not retire store/provider.
opend3::ui::NativeTextPresence UI_NativeTextPresence(opend3::ui::NativeTextIdentity,
    const opend3::ui::TextEditorIdentity&) noexcept;
