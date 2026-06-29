# BREACH

A Game Boy-style hacking roguelike. Descend a system node by node — each node is a
cipher you have to crack. Pick your path, build combos, outrun the trace, and see how
deep you can get before they catch you.

*(add a screenshot or short gif here — it sells the green CRT look instantly)*

## What it is

Every node hands you intercepted data (Base64, Morse, XOR, a Caesar cipher, some
security trivia…) and you type the decoded answer to break through. Clear a node and
you choose your next path: a safe node, a high-risk SECURE node worth double, a market,
or an unknown event. Every 5 nodes a layer guardian blocks the way. Die and your run
ends — climb the leaderboard and try again.

It's solo, terminal-green, and built to be picked up in 30 seconds.

## Run it

Requires Python 3 and a couple of libraries:

```bash
pip install pygame numpy
python3 breach.py
```

That's it. Saves, leaderboard and achievements live in `~/.breach_save.json`.

## How to play

- Read the intercepted data, type the answer, press **ENTER**.
- After each node, pick your route with **← →** (or **1–3**) and **ENTER**.
- **F1** hint · **F2** skip · **F3** decode · **F4** scanner · **ESC** pause
- In the menu: **←/→** pick runner, **H** how-to-play, **L** leaderboard.

Tools are bought with your score in the markets that appear between runs.

## Features

- 15 puzzle types: Base64, ROT13, Hex, Binary, Caesar, XOR, Morse, Vigenère, Atbash,
  Leetspeak, ASCII, URL-encode, a number sequence, and real security trivia.
- 6 runners with different perks, 4 difficulties (Script Kiddie → Zero Day).
- Combos, a rising TRACE timer, branching paths, random events, named layer guardians.
- A shop economy (no extra currency — you spend score), achievements and a local
  leaderboard. Chiptune music and SFX.
- On **Zero Day**, the shop is randomized and your tools can jam and break.

## Built with

Python + [pygame](https://www.pygame.org) + numpy. No assets, no engine — just code.

## License

MIT — do what you want with it. *(change this if you prefer another license)*

---

*(Optional: add a short line here in your own words about who made it and why — that
part should sound like you, not like a README.)*
