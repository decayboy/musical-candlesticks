import asyncio
import websockets
import json
import rtmidi
import numpy as np

# ---- SETTINGS ----
SYMBOL = "btcusdt"       # Bitcoin/USDT trading pair
BINANCE_WS = f"wss://stream.binance.com:9443/ws/{SYMBOL}@trade"

MIDI_NOTE_RANGE = (48, 72)  # C3 to C5
BASE_VELOCITY = 80
TREND_WINDOW = 10

# ---- MIDI Setup ----
midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()
if available_ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("Market_Music")

# ---- Scaling Functions ----
def scale_price(price, min_p, max_p):
    return int(np.clip(
        (price - min_p) / (max_p - min_p) * (MIDI_NOTE_RANGE[1] - MIDI_NOTE_RANGE[0]) + MIDI_NOTE_RANGE[0],
        MIDI_NOTE_RANGE[0],
        MIDI_NOTE_RANGE[1]
    ))

# ---- Main Loop ----
async def market_music():
    buffer = []
    async with websockets.connect(BINANCE_WS) as websocket:
        while True:
            msg = await websocket.recv()
            data = json.loads(msg)

            price = float(data['p'])  # Current trade price
            buffer.append(price)
            if len(buffer) > TREND_WINDOW:
                buffer.pop(0)

            min_p, max_p = min(buffer), max(buffer)
            note = scale_price(price, min_p, max_p)

            # Trend detection
            trend = price - np.mean(buffer)

            # Play single note or simple chord
            if trend > 0:
                # Ascending trend = major dyad
                notes = [note, note + 4]
            else:
                # Descending trend = minor dyad
                notes = [note, note + 3]

            # Humanize velocity a bit
            velocity = np.clip(BASE_VELOCITY + np.random.randint(-10, 10), 40, 120)

            # Send MIDI notes
            for n in notes:
                midiout.send_message([0x90, n, velocity])  # Note On
            await asyncio.sleep(0.2)  # Sustain for a moment
            for n in notes:
                midiout.send_message([0x80, n, 0])        # Note Off

# ---- Run ----
if __name__ == "__main__":
    asyncio.run(market_music())
