# strobetune

Goal: an ESP32 + WS2812B strobe tuner (strand of ~30–60 LEDs). Before building hardware, `strobe-proto.html` is a browser prototype (Web Audio) used to find good parameters.

Target instruments to start: tuba and trombone, so the note range is mostly below middle C (selector covers C1–C5). Pitch is chosen manually, or with the Detect button.

## Running

Single self-contained file, no build step:

```sh
npx live-server --port=8000 --open=strobe-proto.html
```

Serve over localhost rather than `file://` so mic access and AudioWorklet load reliably.

## How it works

The display is synchronous averaging, which is what a strobe disc does:

- **Phase accumulator.** Each band keeps a fractional phase that advances by `f·ratio / sampleRate` per sample and wraps at `periods` (the number of tone periods across the strand). LED index = `floor(phase / periods · N)`. Never round the period to whole samples: at 44.1 kHz, C4 rounded to 169 samples is ~4.5¢ off.
- **Exponential averaging per bin.** `b += α(x − b)` with `α = 1 − exp(−N / (sr·τ))`. Each bin gets about `sr/N` writes per second, so τ is a real-time time constant regardless of N.
- **Signed samples, not rectified.** Off-pitch sound and noise average toward zero; the in-tune waveform builds up. Rectifying (|x| or x²) adds a DC floor that washes out contrast and doubles the dot count. x² is cleaner than |x| for a sine (DC + 2f only), but neither beats signed averaging. A rectify toggle is kept for comparison.
- **Display rate is decoupled.** The worklet posts bins at ~60 Hz. WS2812B takes ~30 µs/LED (~1.8 ms for 60), so it's not a constraint.

### Useful relationships

- Drift speed = Δf period-widths per second = `Δf · N / k` LEDs/s; it does not depend on k. With 60 LEDs and k = 4 at C4, 1¢ ≈ 2.3 LEDs/s.
- Smear limit: the pattern washes out beyond Δf ≈ 1/(2τ). Long τ is steadier but only shows near-in-tune notes. Default τ ≈ 250 ms (≈ ±29¢ at B♭2).
- Harmonics show as finer patterns: the 2nd harmonic shows 2k dots. A note an octave up still locks; an octave down partly cancels.

## Prototype features (`strobe-proto.html`)

- **Target:** note select (concert pitch, default B♭2), A4 reference, and Detect pitch.
  - Detect uses YIN autocorrelation (25–1000 Hz, 16384-sample analyser before the filters) and snaps to the nearest 12-TET semitone.
- **Strand:** LED count, periods across strand, strip or ring layout.
- **Color modes:**
  - *Mono:* amber. The bipolar display shows positive values red and negative values green.
  - *RGB period bands:* same pitch, different periods per color, like Peterson bands.
  - *Major chord 3:4:5:* green = selected note, red = ×3/4 (a fourth below), blue = ×5/4 (a just major third above).
    - Each band has its own phase accumulator, its own worklet input, and its own bandpass chain at its pitch.
    - The readout shows the just-intonation deviation from equal temperament (+2.0¢ for the fourth, −13.7¢ for the third).
- **Display:** auto or manual gain, sharpness γ, positive-half or bipolar.
- **Bandpass:** off / 1 / 2 biquad stages at each band's pitch, with adjustable Q. It's optional so you can see the pattern with harmonics present too.
- **Test input:**
  - Waveforms: brass-like (custom harmonics), sine, saw, square, triangle.
  - Optional 3:4:5 chord tone, detune in cents, and added noise.
  - Mic input with echo cancellation, noise suppression and auto-gain turned off.
  - Forced sample rates (e.g. 16 kHz or 8 kHz) to approximate the ESP32.
- **Readout:** period, strand window, time and samples per LED, rounding error if the period were a whole number of samples, drift per cent, smear limit, α.

## Findings

- In chord mode, bands cross-lock when a band's window holds a whole number of another chord tone's periods. That happens when k is a multiple of 3, 4 or 5 (e.g. k = 4: the green window holds 3 red and 5 blue periods).
  - With pure tones, only k = 1 or 2 keep the bands separate. Even then, harmonic-rich tones leak 15–50% because the chord tones share harmonics.
  - The user accepted the overlap, so k is not constrained in chord mode.
- YIN on synthetic sine and brass tones (37–349 Hz, including a weak fundamental) came within 0.01 Hz of the true pitch.

## ESP32 notes (planned)

- Use an I2S MEMS mic (e.g. INMP441) rather than the noisy built-in ADC.
- Use a 32-bit fixed-point phase accumulator.
- Chord mode needs 3 accumulators, 3 sets of bins, and 3 filter chains if bandpass is used.
- Pitch detection: downsample or use FFT-based autocorrelation. The direct YIN version is about 28M multiply-adds per attempt at 48 kHz.
- Open questions: strip vs ring, LED count, final τ and k.
