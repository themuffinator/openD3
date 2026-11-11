// Copyright (C) 2026 openD3 contributors. SPDX-License-Identifier: GPL-3.0-or-later
#ifndef OPEND3_VOICE_CHAT_H
#define OPEND3_VOICE_CHAT_H
void SoundVoiceChat_InitCommands();
void SoundVoiceChat_Render();
// Must run before destroying the OpenAL context, including hotplug/restart.
void SoundVoiceChat_Shutdown();
// What a lost output does to every source, these included (s_testDeviceInterruption):
// playback stops, and the next frame after the output returns starts it again.
void SoundVoiceChat_OutputInterrupted();
#endif
