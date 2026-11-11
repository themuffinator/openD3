// Copyright (C) 2026 DarkMatter Productions. GPL-3.0-or-later.
// Frame-pacing policy (HF-07): the production header driven by deterministic
// models. It proves 50 us interval bins judge the 240 Hz budget where whole
// milliseconds could not, that windows showing nothing never present faster
// than 60 Hz, that the precise limiter's spin follows the timer it runs on
// (covering a jittery high-resolution timer, bounded against preemption) and
// that the pacing report names what actually holds the frame rate. The
// engine's use of the header is pinned by presentation_hf_contract.py.
#include "src/framework/PresentationPacing.h"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

#define CHECK(value) do { if (!(value)) { std::fprintf(stderr, "%s:%d: %s\n", __FILE__, __LINE__, #value); std::exit(1); } } while (0)

static bool Near(double a, double b, double epsilon = 0.0001) { return std::fabs(a - b) < epsilon; }

// a small deterministic generator, so every run sees the same jitter
struct Lcg {
	std::uint32_t state;
	explicit Lcg(std::uint32_t seed) : state(seed) {}
	double Unit() {
		state = state * 1664525u + 1013904223u;
		return double(state >> 8) / double(1u << 24);
	}
};

static void Bins() {
	CHECK(opend3::FramePacingBin(0.0) == 0);
	CHECK(opend3::FramePacingBin(-3.0) == 0);
	CHECK(opend3::FramePacingBin(std::nan("")) == 0);
	CHECK(opend3::FramePacingBin(0.049) == 0);
	CHECK(opend3::FramePacingBin(0.05) == 1);
	CHECK(opend3::FramePacingBin(4.1667) == 83);
	CHECK(opend3::FramePacingBin(65.99) == opend3::FRAME_PACING_OVERFLOW_BIN - 1);
	CHECK(opend3::FramePacingBin(66.0) == opend3::FRAME_PACING_OVERFLOW_BIN);
	CHECK(opend3::FramePacingBin(1000.0) == opend3::FRAME_PACING_OVERFLOW_BIN);

	std::vector<int> bins(opend3::FRAME_PACING_BINS, 0);
	CHECK(opend3::FramePacingPercentileMsec(bins.data(), 0, 95, 0.0f) == 0.0f);
	CHECK(opend3::FramePacingPercentileMsec(nullptr, 10, 95, 1.0f) == 0.0f);

	// a steady cadence reports its own interval: the bin edge never exceeds the longest sample
	bins[opend3::FramePacingBin(4.1667)] = 1000;
	CHECK(Near(opend3::FramePacingPercentileMsec(bins.data(), 1000, 50, 4.1667f), 4.1667, 0.0001));
	CHECK(Near(opend3::FramePacingPercentileMsec(bins.data(), 1000, 99, 4.1667f), 4.1667, 0.0001));

	// 95% at 4.17 ms and 5% at a missed refresh: p95 stays in the short bin (its edge,
	// 4.20 ms, errs long by under a bin) and p99 reports the long interval
	bins[opend3::FramePacingBin(4.1667)] = 950;
	bins[opend3::FramePacingBin(8.3333)] = 50;
	CHECK(Near(opend3::FramePacingPercentileMsec(bins.data(), 1000, 95, 8.3333f), 4.20, 0.0001));
	CHECK(Near(opend3::FramePacingPercentileMsec(bins.data(), 1000, 99, 8.3333f), 8.3333, 0.0001));

	// overflowed samples report the longest interval seen
	std::fill(bins.begin(), bins.end(), 0);
	bins[opend3::FRAME_PACING_OVERFLOW_BIN] = 3;
	CHECK(Near(opend3::FramePacingPercentileMsec(bins.data(), 3, 50, 250.0f), 250.0));
}

// Why the bins moved below a millisecond: a 240 Hz cadence with 0.1 ms of wake
// jitter, stamped by a millisecond clock, reads p95 5 ms and fails a budget the
// same frames meet on the high-resolution clock.
static void WholeMillisecondsCouldNotJudge240() {
	Lcg random(240);
	const int frames = 4000;
	std::vector<double> starts(frames);
	for (int i = 0; i < frames; ++i) {
		starts[i] = 1000.0 + i * (1000.0 / 240.0) + random.Unit() * 0.1;
	}
	std::vector<int> fine(opend3::FRAME_PACING_BINS, 0);
	std::vector<int> whole(66, 0);
	float longest = 0.0f;
	int longestWhole = 0;
	for (int i = 1; i < frames; ++i) {
		const double interval = starts[i] - starts[i - 1];
		++fine[opend3::FramePacingBin(interval)];
		longest = std::max(longest, float(interval));
		const int wholeInterval = int(std::floor(starts[i])) - int(std::floor(starts[i - 1]));
		++whole[std::min(wholeInterval, 65)];
		longestWhole = std::max(longestWhole, wholeInterval);
	}
	const int samples = frames - 1;
	auto wholePercentile = [&](int percentile) {
		const int target = std::max(1, (samples * percentile + 99) / 100);
		int accumulated = 0;
		for (int i = 0; i < 66; ++i) {
			accumulated += whole[i];
			if (accumulated >= target) {
				return i;
			}
		}
		return longestWhole;
	};
	const float p95 = opend3::FramePacingPercentileMsec(fine.data(), samples, 95, longest);
	const float p99 = opend3::FramePacingPercentileMsec(fine.data(), samples, 99, longest);
	CHECK(wholePercentile(95) == 5);
	CHECK(float(wholePercentile(95)) > opend3::SUPPORTED_CAP_P95_BUDGET_MSEC);
	CHECK(p95 < 4.30f && p99 < 4.30f);
	CHECK(opend3::JudgeFramePacingBudget(240, p95, p99) == opend3::FramePacingBudget::Met);
}

static void Budget() {
	CHECK(opend3::JudgeFramePacingBudget(240, 4.6f, 6.3f) == opend3::FramePacingBudget::Met);
	CHECK(opend3::JudgeFramePacingBudget(240, 4.61f, 5.0f) == opend3::FramePacingBudget::Missed);
	CHECK(opend3::JudgeFramePacingBudget(240, 4.0f, 6.31f) == opend3::FramePacingBudget::Missed);
	CHECK(opend3::JudgeFramePacingBudget(144, 1.0f, 1.0f) == opend3::FramePacingBudget::NotDeclared);
	CHECK(opend3::JudgeFramePacingBudget(0, 1.0f, 1.0f) == opend3::FramePacingBudget::NotDeclared);
}

static void WindowCap() {
	CHECK(opend3::PresentationCapForWindow(240, true) == 240);
	CHECK(opend3::PresentationCapForWindow(0, true) == 0);
	CHECK(opend3::PresentationCapForWindow(-5, true) == 0);
	CHECK(opend3::PresentationCapForWindow(240, false) == 60);
	CHECK(opend3::PresentationCapForWindow(0, false) == 60);
	CHECK(opend3::PresentationCapForWindow(-5, false) == 60);
	CHECK(opend3::PresentationCapForWindow(60, false) == 60);
	CHECK(opend3::PresentationCapForWindow(30, false) == 30);
}

static void SpinPolicy() {
	opend3::LimiterOversleepWindow window;
	CHECK(Near(window.Covered(), opend3::LIMITER_INITIAL_OVERSLEEP_MSEC));
	CHECK(Near(opend3::LimiterSpinMsec(window), 0.6));
	window.Add(0.3);
	CHECK(Near(window.Covered(), 0.3) && Near(opend3::LimiterSpinMsec(window), 0.4));
	window.Add(std::nan(""));
	window.Add(-1.0);
	CHECK(Near(window.Covered(), 0.3, 0.00001));
	// three preemptions in a full window are ignored; the fourth is not
	window = opend3::LimiterOversleepWindow();
	for (int i = 0; i < 64; ++i) {
		window.Add(0.1);
	}
	CHECK(Near(opend3::LimiterSpinMsec(window), opend3::LIMITER_MIN_SPIN_MSEC));
	window.Add(15.0); window.Add(9.0); window.Add(1.7);
	CHECK(Near(window.Covered(), 0.1, 0.00001));
	window.Add(1.2);
	CHECK(Near(window.Covered(), 1.2, 0.00001) && Near(opend3::LimiterSpinMsec(window), 1.3, 0.00001));
	// longer than the longest spin counts as the longest spin
	for (int i = 0; i < 64; ++i) {
		window.Add(5.0);
	}
	CHECK(Near(window.Covered(), opend3::LIMITER_MAX_SPIN_MSEC) && Near(opend3::LimiterSpinMsec(window), opend3::LIMITER_MAX_SPIN_MSEC));
	// the window forgets: 64 quiet sleeps bring the spin back down
	for (int i = 0; i < 64; ++i) {
		window.Add(0.2);
	}
	CHECK(Near(opend3::LimiterSpinMsec(window), 0.3, 0.00001));
	CHECK(Near(opend3::LegacyLimiterSpinMsec(1000.0 / 240.0), 0.5208, 0.001));
	CHECK(Near(opend3::LegacyLimiterSpinMsec(1000.0 / 60.0), 1.5));
	CHECK(Near(opend3::LegacyLimiterSpinMsec(1.0), 0.5));
}

// The limiter loop of Common_ThrottlePresentationFrame against a model timer
// whose sleeps wake late by up to `jitter` ms, with an occasional preemption.
struct LimiterRun {
	double latenessP95 = 0.0;
	double latenessMax = 0.0;
	double spinPerFrame = 0.0;		// mean busy-wait per frame, ms
	double finalSpin = 0.0;
};

static LimiterRun RunLimiter(int cap, double jitter, bool precise, int preemptEvery, std::uint32_t seed) {
	Lcg random(seed);
	const double frameMsec = 1000.0 / cap;
	const double workMsec = frameMsec * 0.4;
	opend3::LimiterOversleepWindow window;
	double now = 0.0;
	double target = frameMsec;
	std::vector<double> lateness;
	double spun = 0.0;
	const int frames = 3000;
	for (int frame = 0; frame < frames; ++frame) {
		now += workMsec;
		const double slack = precise ? opend3::LimiterSpinMsec(window) : opend3::LegacyLimiterSpinMsec(frameMsec);
		double remaining = target - now;
		while (remaining > slack) {
			// precise sleeps request fractions; legacy sleeps whole milliseconds
			const double request = precise ? remaining - slack : std::max(1.0, std::floor(remaining - slack));
			double woke = request + random.Unit() * jitter;
			if (preemptEvery > 0 && frame % preemptEvery == preemptEvery - 1) {
				woke += 12.0;
			}
			now += woke;
			if (precise) {
				window.Add(woke - request);
			}
			remaining = target - now;
		}
		if (remaining > 0.0) {
			spun += remaining;
			now = target;
		}
		lateness.push_back(now - target);
		target += frameMsec;
		if (now > target + frameMsec * 4.0) {
			target = now + frameMsec;	// the engine restarts its cadence after a long hitch
		}
	}
	std::sort(lateness.begin(), lateness.end());
	LimiterRun run;
	run.latenessP95 = lateness[size_t(0.95 * (lateness.size() - 1) + 0.5)];
	run.latenessMax = lateness.back();
	run.spinPerFrame = spun / frames;
	run.finalSpin = precise ? opend3::LimiterSpinMsec(window) : opend3::LegacyLimiterSpinMsec(frameMsec);
	return run;
}

static void LimiterModel() {
	// a high-resolution timer waking up to 0.3 ms late: the spin settles just above the
	// jitter, no frame wakes late, and far less time is spun than the legacy eighth
	const LimiterRun fine240 = RunLimiter(240, 0.3, true, 0, 1);
	CHECK(fine240.latenessP95 == 0.0 && fine240.latenessMax == 0.0);
	CHECK(fine240.finalSpin > 0.3 && fine240.finalSpin < 0.45);
	const LimiterRun fine60 = RunLimiter(60, 0.3, true, 0, 2);
	const LimiterRun legacy60 = RunLimiter(60, 1.0, false, 0, 2);
	CHECK(fine60.latenessP95 == 0.0);
	CHECK(fine60.spinPerFrame < legacy60.spinPerFrame * 0.5);

	// a coarse timer (1.5 ms of wake jitter): the spin widens to cover it
	const LimiterRun coarse = RunLimiter(240, 1.5, true, 0, 3);
	CHECK(coarse.latenessP95 == 0.0);
	CHECK(coarse.finalSpin > 1.2 && coarse.finalSpin <= opend3::LIMITER_MAX_SPIN_MSEC);

	// preemption (12 ms late once every 200 frames) cannot be spun away: the spin stays
	// bounded and the frames between preemptions still wake on time
	const LimiterRun preempted = RunLimiter(240, 0.3, true, 200, 4);
	CHECK(preempted.latenessP95 == 0.0);
	CHECK(preempted.latenessMax > 5.0);
	CHECK(preempted.spinPerFrame < opend3::LIMITER_MAX_SPIN_MSEC);
}

static void Classification() {
	using opend3::FramePacingBound;
	opend3::FramePacingBoundInput in;
	CHECK(opend3::ClassifyFramePacing(in) == FramePacingBound::Unknown);

	// the cap holds at any rate, above the tick rate included
	in.avgFrameMsec = 4.20f; in.presentationCap = 240;
	CHECK(opend3::ClassifyFramePacing(in) == FramePacingBound::PresentationCap);
	in.avgFrameMsec = 16.7f; in.presentationCap = 60; in.avgTicsPerFrame = 1.0f;
	CHECK(opend3::ClassifyFramePacing(in) == FramePacingBound::PresentationCap);
	in.avgFrameMsec = 33.4f; in.presentationCap = 30; in.avgTicsPerFrame = 2.0f;
	CHECK(opend3::ClassifyFramePacing(in) == FramePacingBound::PresentationCap);

	// below the cap with nothing waiting: the frame's own work (196 Hz at a 240 cap)
	in = opend3::FramePacingBoundInput();
	in.avgFrameMsec = 5.1f; in.presentationCap = 240;
	CHECK(opend3::ClassifyFramePacing(in) == FramePacingBound::FrameWork);

	// vsync on a 240 Hz display mixing 4.17 and 8.33 ms refreshes (138 Hz)
	in.swapInterval = 1; in.refreshHz = 240.0f; in.avgFrameMsec = 7.25f;
	CHECK(opend3::ClassifyFramePacing(in) == FramePacingBound::Vsync);
	in.swapInterval = -1;	// adaptive
	CHECK(opend3::ClassifyFramePacing(in) == FramePacingBound::Vsync);
	// faster than the refresh cannot be vsync
	in.swapInterval = 1; in.refreshHz = 60.0f; in.avgFrameMsec = 7.25f;
	CHECK(opend3::ClassifyFramePacing(in) == FramePacingBound::FrameWork);
	// an unknown refresh keeps the old rule: vsync only below the tick rate
	in.refreshHz = 0.0f; in.avgFrameMsec = 20.0f;
	CHECK(opend3::ClassifyFramePacing(in) == FramePacingBound::Vsync);
	in.avgFrameMsec = 7.25f;
	CHECK(opend3::ClassifyFramePacing(in) == FramePacingBound::FrameWork);

	// demos and capture wait for tics; so does play that runs one tic a frame uncapped
	in = opend3::FramePacingBoundInput();
	in.avgFrameMsec = 33.0f; in.waitedForTic = true;
	CHECK(opend3::ClassifyFramePacing(in) == FramePacingBound::Simulation);
	in.waitedForTic = false; in.avgFrameMsec = 16.0f; in.avgGameTicsPerFrame = 1.0f;
	CHECK(opend3::ClassifyFramePacing(in) == FramePacingBound::Simulation);
}

int main() {
	Bins();
	WholeMillisecondsCouldNotJudge240();
	Budget();
	WindowCap();
	SpinPolicy();
	LimiterModel();
	Classification();
	std::printf("presentation pacing policy: ok\n");
	return 0;
}
