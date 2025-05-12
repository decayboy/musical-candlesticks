import yfinance as yf
import pretty_midi
import numpy as np
import random

# ---- SETTINGS ----
TICKER = "AAPL"
START_DATE = "2024-01-01"
END_DATE = "2024-06-01"
OUTPUT_FILE = "market_music_v2.mid"

SCALE = [0, 2, 4, 5, 7, 9, 11]  # C Major intervals (relative to C)
BASE_NOTE = 60  # C4 middle C
OCTAVES = 2
NOTE_DURATION = 0.5
VELOCITY_RANGE = (40, 100)

# ---- FUNCTIONS ----
def scale_value(val, min_val, max_val, new_min, new_max):
    return new_min + (val - min_val) * (new_max - new_min) / (max_val - min_val)

def quantize_to_scale(note):
    root = BASE_NOTE % 12
    octave = note // 12
    degree = (note % 12) - root
    # Find nearest note in scale
    closest = min(SCALE, key=lambda x: abs(x - degree))
    return (octave * 12) + root + closest

def create_chord(root_note, chord_type='major'):
    if chord_type == 'major':
        intervals = [0, 4, 7]
    elif chord_type == 'minor':
        intervals = [0, 3, 7]
    return [root_note + i for i in intervals]

# ---- MAIN ----
def main():
    data = yf.download(TICKER, start=START_DATE, end=END_DATE)
    closes = data['Close'].values
    volumes = data['Volume'].values

    midi = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(program=0)

    min_price, max_price = np.min(closes), np.max(closes)
    min_vol, max_vol = np.min(volumes), np.max(volumes)

    current_time = 0.0
    trend_window = 3

    for i in range(len(closes)):
        price = closes[i]
        volume = volumes[i]

        # Map price to MIDI note
        raw_note = int(scale_value(price, min_price, max_price,
                                   BASE_NOTE, BASE_NOTE + (12 * OCTAVES)))
        note_number = quantize_to_scale(raw_note)

        # Map volume to velocity
        velocity = int(scale_value(volume, min_vol, max_vol,
                                   VELOCITY_RANGE[0], VELOCITY_RANGE[1]))

        # Determine recent trend
        if i >= trend_window:
            trend = closes[i] - np.mean(closes[i - trend_window:i])
        else:
            trend = 0

        # Apply humanization
        start_time = current_time + random.uniform(-0.05, 0.05)
        velocity = min(127, max(0, velocity + random.randint(-5, 5)))

        if trend > 0:
            # Uptrend = major chord
            chord = create_chord(note_number, 'major')
            for n in chord:
                note = pretty_midi.Note(velocity=velocity,
                                        pitch=n,
                                        start=start_time,
                                        end=start_time + NOTE_DURATION)
                piano.notes.append(note)
        else:
            # Downtrend = single note
            note = pretty_midi.Note(velocity=velocity,
                                    pitch=note_number,
                                    start=start_time,
                                    end=start_time + NOTE_DURATION)
            piano.notes.append(note)

        current_time += NOTE_DURATION

    midi.instruments.append(piano)
    midi.write(OUTPUT_FILE)
    print(f"Version 2 MIDI created: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
