# Stock Market Sonification-MIDI (Ver. 2)
Python: Candlestick Chart → MIDI

1. Download historical price data (I’ll use ```yfinance``` for stocks/ETFs for simplicity).

2. Map closing prices to MIDI note values.

3. Map volume to velocity (loudness).

4. Output a ```.mid``` file you can play in any DAW or MIDI player.

<b>You'll need:</b> ```pip install yfinance pretty_midi numpy```

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Program creates a very basic melody line where:

- Higher prices = higher pitches.

- Bigger volumes = louder notes.

- Each candle (day) = one note.

You can open ```market_music.mid``` in any DAW (Ableton, FL Studio, Logic) or MIDI player.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Can expand this easily:

- Map open-high-low-close to chords or motifs.

- Use different instruments for different market phases.

- Add swing or tempo changes with volatility.

- Create real-time streaming by replacing ```yfinance``` with WebSockets or live APIs (Binance, IBKR, Alpaca, etc.).

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
<b>Version 2 initial objectives:</b>

- Scale-constrained melodies (C major, D minor, etc.)

- Chord generation (triads for long-term uptrends)

- Random humanization for more musicality

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
<b>What actually happened:</b>

- Notes are forced into the C Major scale → sounds far more musical.

- Uptrends trigger chords, giving moments of fullness and positivity.

- Human-like small imperfections make playback sound more organic.

- This will sound noticeably more like an intentional composition.

<b>Where can it be improved:</b>

- Try different scales (e.g., Dorian, Aeolian) → modify the ```SCALE``` list.

- Add multiple instruments for multi-asset sonification.

- Increase ```trend_window``` to smooth the chord decision logic.

- Output live versions by replacing ```yfinance``` with live-feed APIs (Binance, Alpaca, IBKR).
