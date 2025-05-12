import asyncio
import websockets
import json
import rtmidi
import numpy as np
from collections import deque
import time
import random

# --- SETTINGS ---
SYMBOLS = {"btcusdt": 1, "ethusdt": 2}  # market: MIDI channel
PERFORMANCE_CHANNEL = 10  # percussion channel
RSI_PERIOD = 14
TREND_WINDOW = 10
MIDI_NOTE_RANGE = (48, 72)
BASE_VELOCITY = 80
SWING_AMOUNT = 0.02  # 20ms swing delay

# --- INIT MIDI ---
midiout = rtmidi.MidiOut()
ports = midiout.get_ports()
if ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("Market_Music")

buffers = {symbol: deque(maxlen=RSI_PERIOD) for symbol in SYMBOLS}
volumes = {symbol: deque(maxlen=TREND_WINDOW) for symbol in SYMBOLS}

def rsi(prices):
    if len(prices) < RSI_PERIOD:
        return 50
    gains = [max(0, prices[i] - prices[i-1]) for i in range(1, len(prices))]
    losses = [max(0, prices[i-1] - prices[i]) for i in range(1, len(prices))]
    avg_gain = np.mean(gains)
    avg_loss = np.mean(losses)
    return 100 - (100 / (1 + (avg_gain / (avg_loss + 1e-6))))

def scale_price(price, min_p, max_p):
    return int(np.clip(
        (price - min_p) / (max_p - min_p) * (MIDI_NOTE_RANGE[1] - MIDI_NOTE_RANGE[0]) + MIDI_NOTE_RANGE[0],
        MIDI_NOTE_RANGE[0], MIDI_NOTE_RANGE[1]
    ))

async def stream_market(symbol):
    url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
    async with websockets.connect(url) as websocket:
        while True:
            msg = await websocket.recv()
            data = json.loads(msg)
            price = float(data['p'])
            volume = float(data['q'])

            buffers[symbol].append(price)
            volumes[symbol].append(volume)

            # RSI based tempo (frenzied markets = faster)
            current_rsi = rsi(buffers[symbol])
            base_delay = np.interp(current_rsi, [0, 100], [0.5, 0.1])

            min_p, max_p = min(buffers[symbol]), max(buffers[symbol])
            note = scale_price(price, min_p, max_p)
            velocity = np.clip(BASE_VELOCITY + random.randint(-10, 10), 40, 120)

            # Swing + humanization
            delay = base_delay
            if int(time.time() * 2) % 2 == 1:
                delay += SWING_AMOUNT
            delay += random.uniform(-0.01, 0.01)

            channel = SYMBOLS[symbol]
            trend = price - np.mean(buffers[symbol])

            notes = [note + 4, note] if trend > 0 else [note, note - 3]
            for n in notes:
                midiout.send_message([0x90 + channel - 1, n, velocity])
            await asyncio.sleep(delay)
            for n in notes:
                midiout.send_message([0x80 + channel - 1, n, 0])

            # Volume spike = percussion hit
            if len(volumes[symbol]) == TREND_WINDOW:
                recent_vol = np.mean(list(volumes[symbol])[:-1])
                if volume > 1.5 * recent_vol:
                    drum_note = random.choice([36, 38, 42, 46])  # bass, snare, hats
                    midiout.send_message([0x99, drum_note, 100])
                    await asyncio.sleep(0.1)
                    midiout.send_message([0x89, drum_note, 0])

async def main():
    await asyncio.gather(*(stream_market(symbol) for symbol in SYMBOLS))

if __name__ == "__main__":
    asyncio.run(main())
