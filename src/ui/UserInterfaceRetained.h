// Copyright (C) 2026 DarkMatter Productions. GPL-3.0-or-later.
#pragma once
#ifndef ID_DEDICATED
#include "UserInterfaceManaged.h"
#include <memory>
#include <string>
#include <vector>

// Semantic diagnostics for a manager-created retained view. They never read
// or inject physical input. The session dispatches any resulting typed queue.
bool UI_RetainedDiagnostic(idUserInterface* gui, const idCmdArgs& args);
bool UI_RetainedSettingsDocument(idUserInterface* gui);
bool UI_RetainedSettingsCanReturn(idUserInterface* gui);
// A retained GUI that can no longer draw (its view failed to come back
// after a renderer or language change); callers present the stock screen.
bool UI_RetainedViewFailed(idUserInterface* gui);
// The validated model of a retained GUI's document, which lives as long as
// the GUI holds that document: how a HUD peer reads the declared state and
// the generator's extension data without parsing the source again.
namespace opend3::ui { struct DocumentModel; }
const opend3::ui::DocumentModel* UI_RetainedDocumentModel(idUserInterface* gui);
// The names of a retained GUI's declared state that start with `prefix`, in
// order: how a session finds the application lines a document shows.
int UI_RetainedStateNames(idUserInterface* gui, const char* prefix, std::vector<std::string>& names);
// Read semantic focus so a refreshed catalog can follow the same entry.
std::string UI_RetainedFocusedControl(idUserInterface* gui);
// The right stick's vertical deflection in a retained menu (section 13.5),
// past the rest zone in -1..1, held for `seconds`: it scrolls the detail area.
// Whether the area moved.
bool UI_RetainedDetailStick(idUserInterface* gui, float y, float seconds);

// Engine adapter for explicit .rui resources. The public game ABI remains
// idUserInterface; RmlUi, canonical nodes and device ownership stay private.
class idUserInterfaceRetained final : public idUserInterfaceManaged {
	friend bool UI_RetainedDiagnostic(idUserInterface*, const idCmdArgs&);
	friend bool UI_RetainedSettingsDocument(idUserInterface*);
	friend bool UI_RetainedSettingsCanReturn(idUserInterface*);
	friend bool UI_RetainedViewFailed(idUserInterface*);
	friend const opend3::ui::DocumentModel* UI_RetainedDocumentModel(idUserInterface*);
	friend int UI_RetainedStateNames(idUserInterface*, const char*, std::vector<std::string>&);
	friend std::string UI_RetainedFocusedControl(idUserInterface*);
	friend bool UI_RetainedDetailStick(idUserInterface*, float, float);
public:
	explicit idUserInterfaceRetained(bool managed = true);
	~idUserInterfaceRetained() override;
	const char* Name() const override;
	const char* Comment() const override;
	bool IsInteractive() const override;
	void SetInteractive(bool value) override;
	bool IsUniqued() const override;
	void SetUniqued(bool value) override;
	bool InitFromFile(const char* path, bool rebuild = true, bool cache = true) override;
	const char* HandleEvent(const sysEvent_t* event, int time, bool* updateVisuals = NULL) override;
	void HandleNamedEvent(const char* name) override;
	void Redraw(int time, bool useAspectCorrection = true) override;
	void DrawCursor() override;
	const idDict& State() const override;
	void DeleteStateVar(const char* name) override;
	void SetStateString(const char* name, const char* value) override;
	void SetStateBool(const char* name, bool value) override;
	void SetStateInt(const char* name, int value) override;
	void SetStateFloat(const char* name, float value) override;
	void SetStateVec4(const char* name, const idVec4& value) override;
	const char* GetStateString(const char* name, const char* fallback = "") const override;
	bool GetStateBool(const char* name, const char* fallback = "0") const override;
	int GetStateInt(const char* name, const char* fallback = "0") const override;
	float GetStateFloat(const char* name, const char* fallback = "0") const override;
	bool GetPresentationValue(const char* name, idStr& value) const override;
	bool SetPresentationValue(const char* name, const char* value, bool overrideExpression = true) override;
	bool GetTextInputState(idRectangle& area, float& cursorOffset) const override;
	void StateChanged(int time, bool redraw = false) override;
	const char* Activate(bool activate, int time) override;
	void Trigger(int time) override;
	bool WriteToSaveGame(idFile* file) const override;
	bool ReadFromSaveGame(idFile* file) override;
	void SetKeyBindingNames() override;
	void SetCursor(float x, float y) override;
	float CursorX() override;
	float CursorY() override;
	bool GetMaxTextIndex(const char* name, const char* text, wrapInfo_t& info) const override;
	const char* GetSourceFile() const override;
	ID_TIME_T GetTimeStamp() const override;
	bool Active() const override;
	bool HasInteractiveOverride() const override;
	bool IsMenuGui() const override;
	bool AlwaysThink() const override;
	void RunTimeEvents(int time) override;
	size_t Size() override;
	int NumTransitions() override;
	bool DispatchApplicationActions(const char* command, bool& closeRequested) override;
	const char* PendingApplicationCommand() const override;
	opend3::ui::TextBrokerContext QueryTextContext(std::uint64_t allocation,
		std::uint64_t window, std::uint64_t session) override;
	bool ApplyTextInput(const opend3::ui::TextBrokerContext& expected,
		const opend3::ui::TextInputEvent& input, std::string& error) override;
	bool TakeClipboardRequest(const char* command, uiClipboardRequest_t& out) override;
	bool TakeSessionRequest(const char* command, idStr& out) override;
	bool KeepForLevelLoad() override;
	bool QueryClipboardEditor(uiNumberEditorSnapshot_t& out, std::string& error) override;
	bool ReplaceClipboardSelection(const uiNumberEditorTarget_t& expected,
		std::string_view text, std::string& error) override;
	bool SetClipboardNotice(const uiNumberEditorTarget_t& expected,
		opend3::ui::NumberEditNotice notice, std::string& error) override;

	bool PrepareNativeText(const opend3::ui::TextEditorIdentity& owner) override;
	bool AttachNativeText(const opend3::ui::TextEditorIdentity& owner, opend3::ui::NativeTextIdentity native, opend3::ui::NativeTextEditorBarrier& out, std::string& error) override;
	bool RefreshNativeText(const opend3::ui::NativeTextEditorBarrier& expected, opend3::ui::NativeTextEditorView& out, std::string& error) override;
	bool CurrentNativeText(const opend3::ui::NativeTextEditorBarrier& expected) const noexcept override;
	bool BeginNativeText(const opend3::ui::NativeTextEditorBarrier& expected, const opend3::ui::NativeTextCollection& collection, opend3::ui::NativeTextEditorBarrier& out, std::string& error) override;
	bool ApplyNativeText(const opend3::ui::NativeTextEditorBarrier& expected, const opend3::ui::NativeTextOffer& offer, opend3::ui::NativeTextEditorReceipt& out, std::string& error) override;
	bool CompleteNativeText(const opend3::ui::NativeTextEditorBarrier& expected, const opend3::ui::NativeTextCollection& collection, opend3::ui::NativeTextEditorBarrier& out, std::string& error) override;
	std::unique_ptr<opend3::ui::Interaction::NativeSettlement> PrepareNativeTextSettlement(const opend3::ui::NativeTextEditorBarrier& expected, std::string& error) override;
	bool PublishNativeTextSettlement(opend3::ui::Interaction::NativeSettlement& prepared, opend3::ui::NativeTextEditorReceipt& out) noexcept override;
	bool RetireNativeTextExact(opend3::ui::NativeTextIdentity native, const opend3::ui::TextEditorIdentity& owner) noexcept override;
	opend3::ui::NativeTextPresence QueryNativeTextPresence(opend3::ui::NativeTextIdentity, const opend3::ui::TextEditorIdentity&) const noexcept override;

private:
	struct Impl;
	std::unique_ptr<Impl> impl;
};
#endif
