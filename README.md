# strobetune

A strobe tuner for an LED strand, aimed at an ESP32 driving WS2812B LEDs. This repo currently holds a browser prototype for working out the parameters (LED count, periods across the strand, averaging time constant, filtering) before building hardware.

The first target instruments are tuba and trombone.

## How it works

Audio samples are placed along the strand by a phase accumulator that wraps every few periods of the target pitch. Each LED keeps an exponentially decaying average of the signed samples that land on it. When the note is in tune, each pass reinforces the same pattern and it stands still. When the note is sharp or flat, the pattern drifts one way or the other, faster the further off it is.

## Running the prototype

```sh
npx live-server --port=8000 --open=strobe-proto.html
```

Click **Start**. Use the built-in test tone (with a detune slider) or switch the source to the microphone. Serve the page from localhost rather than opening it as a file, so microphone access works.

Features:

- Note selection by hand or with **Detect pitch** (autocorrelation, snapped to the nearest semitone)
- Strip or ring layout, with adjustable LED count and periods across the strand
- Averaging time constant, gain, and dot sharpness
- Optional bandpass at the target pitch
- Mono, RGB period-band, and just-intonation major-chord (3:4:5) color modes
- A readout of derived values: time per LED, drift per cent, and the smear limit

See [AGENTS.md](AGENTS.md) for design notes, findings, and plans for the ESP32 version.
