// Copyright (C) 2026 DarkMatter Productions. GPL-3.0-or-later.
#include "EventQueueContinuity.h"

namespace {
opend3::EventQueueContinuity eventQueueContinuity;
}

std::uint64_t Sys_EventQueueToken() { return eventQueueContinuity.Token(); }
void Sys_InvalidateEventQueue() { eventQueueContinuity.Invalidate(); }
