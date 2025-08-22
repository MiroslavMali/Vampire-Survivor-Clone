# 8bit_synth_gui.py
# deps: pip install numpy sounddevice
import tkinter as tk
from tkinter import ttk
import numpy as np
import sounddevice as sd
import threading, time, random

SR = 11025          # classic low sample rate
BLOCK = 256         # small buffer for low-ish latency

# GUI state (thread-safe-ish reading)
state = {
    "wave": "square",
    "freq": 220.0,
    "duty": 0.5,
    "vol": 0.4,
    "bit_depth": 8,     # 8-bit quantization
    # Playback controls
    "playing": False,    # if True, generates sound; in one-shot, auto-stops after envelope
    "loop_mode": False,  # if True, sustain indefinitely; if False, one-shot envelope
    "note_len_ms": 500,  # one-shot duration (ms) excluding release
    # ADSR envelope (seconds)
    "attack": 0.01,
    "decay": 0.10,
    "sustain": 0.7,
    "release": 0.20,
    # Filters and smoothing
    "highpass": True,
    # UI / behavior
    "play_on_change": True,
}

phase = 0.0
# Smoothing and filter state (audio thread)
smooth_freq = state["freq"]
smooth_vol = state["vol"]
smooth_duty = state["duty"]
SMOOTH_ALPHA = 0.02
VOL_ALPHA = 0.3  # make volume respond faster
hp_z1 = 0.0
hp_prev = 0.0

# Envelope state
env_active = False
env_t = 0.0
env_stage = "idle"  # "attack","decay","sustain","release","idle"
env_target_len = 0.5  # seconds (note_len_ms)

state_lock = threading.Lock()

def gen_wave(n, freq, wave, duty, vol):
    global phase
    t = (np.arange(n) + phase) / SR
    w = 2*np.pi*freq*t
    if wave == "square":
        y = np.where((w % (2*np.pi)) < 2*np.pi*duty, 1.0, -1.0)
    elif wave == "saw":
        y = 2*((t*freq) % 1.0) - 1.0
    elif wave == "triangle":
        y = 2*np.abs(2*((t*freq) % 1.0) - 1.0) - 1.0
    elif wave == "noise":
        y = np.random.uniform(-1.0, 1.0, n)
    else:
        y = np.zeros(n)
    phase = (phase + n) % SR
    y *= vol

    # 8-bit quantization (“bitcrush”)
    levels = 2**state["bit_depth"]
    yq = np.round((y * 0.5 + 0.5) * (levels - 1)) / (levels - 1)  # map [-1,1] -> [0,1] -> quantize -> back
    yq = (yq - 0.5) * 2.0
    return yq.astype(np.float32)


def gen_envelope(n, params):
    global env_active, env_t, env_stage, env_target_len
    a = max(1e-4, float(params["attack"]))
    d = max(1e-4, float(params["decay"]))
    s = max(0.0, min(1.0, float(params["sustain"])) )
    r = max(1e-4, float(params["release"]))
    loop_mode = bool(params["loop_mode"])
    out = np.zeros(n, dtype=np.float32)
    if not params["playing"]:
        # not playing -> ensure envelope is idle
        env_active = False
        env_stage = "idle"
        env_t = 0.0
        return out

    # Start envelope if needed
    if not env_active:
        env_active = True
        env_stage = "attack"
        env_t = 0.0
        env_target_len = float(params["note_len_ms"]) / 1000.0

    t = 0.0
    dt = 1.0 / SR
    for i in range(n):
        if env_stage == "attack":
            val = min(1.0, env_t / a)
            env_t += dt
            if env_t >= a:
                env_stage = "decay"
                env_t = 0.0
        elif env_stage == "decay":
            # decay from 1.0 to s
            val = 1.0 - (1.0 - s) * min(1.0, env_t / d)
            env_t += dt
            if env_t >= d:
                env_stage = "sustain"
                env_t = 0.0
        elif env_stage == "sustain":
            val = s
            if not loop_mode:
                # count sustain time toward target note length
                env_t += dt
                if env_t >= max(0.0, env_target_len - a - d):
                    env_stage = "release"
                    env_t = 0.0
        elif env_stage == "release":
            # release from current value to 0 over r
            # approximate linear release from s to 0
            val = max(0.0, s * (1.0 - min(1.0, env_t / r)))
            env_t += dt
            if env_t >= r:
                env_stage = "idle"
                env_active = False
        else:
            val = 0.0
        out[i] = val
    # If envelope finished in one-shot, signal stop
    if not loop_mode and not env_active:
        with state_lock:
            state["playing"] = False
    return out

def audio_callback(outdata, frames, time_info, status):
    if status:
        # dropouts etc.
        pass
    # snapshot params (avoid reading mid-write)
    with state_lock:
        params = {
            "freq": float(state["freq"]),
            "wave": state["wave"],
            "duty": float(state["duty"]),
            "vol": float(state["vol"]),
            "bit_depth": int(state["bit_depth"]),
            "playing": bool(state["playing"]),
            "loop_mode": bool(state["loop_mode"]),
            "note_len_ms": int(state["note_len_ms"]),
            "attack": float(state["attack"]),
            "decay": float(state["decay"]),
            "sustain": float(state["sustain"]),
            "release": float(state["release"]),
            "highpass": bool(state["highpass"]),
        }
    # smooth params for click-free control
    global smooth_freq, smooth_vol, smooth_duty, hp_prev, hp_z1
    smooth_freq += (params["freq"] - smooth_freq) * SMOOTH_ALPHA
    smooth_vol  += (params["vol"]  - smooth_vol)  * VOL_ALPHA
    smooth_duty += (params["duty"] - smooth_duty) * SMOOTH_ALPHA

    if params["playing"] or params["loop_mode"]:
        audio = gen_wave(frames, smooth_freq, params["wave"], smooth_duty, 1.0)
        env = gen_envelope(frames, params)
        y = (audio * env) * smooth_vol
    else:
        y = np.zeros(frames, dtype=np.float32)

    # simple high-pass to remove DC when duty != 0.5
    if params["highpass"]:
        # y_hp[n] = y[n] - y[n-1] + a * y_hp[n-1]
        a = 0.995
        out = np.empty_like(y)
        for i in range(frames):
            hp_x = y[i]
            hp = hp_x - hp_prev + a * hp_z1
            hp_prev = hp_x
            hp_z1 = hp
            out[i] = hp
        y = out

    outdata[:, 0] = y  # mono

def run_audio():
    with sd.OutputStream(channels=1, callback=audio_callback, samplerate=SR, blocksize=BLOCK, dtype='float32'):
        while running.is_set():
            time.sleep(0.02)

def on_freq(val):
    with state_lock:
        state["freq"] = float(val)
        if state.get("play_on_change"):
            state["playing"] = True
def on_duty(val):
    with state_lock:
        state["duty"] = max(0.05, min(0.95, float(val)))
        if state.get("play_on_change"):
            state["playing"] = True
def on_vol(val):
    with state_lock:
        state["vol"] = float(val)
def on_bits(val):
    with state_lock:
        state["bit_depth"] = int(float(val))

def on_wave_change(*_):
    with state_lock:
        state["wave"] = wave_var.get()
    # enable duty only for square
    sduty.configure(state=("normal" if wave_var.get()=="square" else "disabled"))
    if state.get("play_on_change"):
        with state_lock:
            state["playing"] = True

def on_play():
    with state_lock:
        state["playing"] = True

def on_stop():
    with state_lock:
        state["playing"] = False
        # also reset envelope
    global env_active, env_stage, env_t
    env_active = False
    env_stage = "idle"
    env_t = 0.0

def on_loop_toggle():
    with state_lock:
        state["loop_mode"] = bool(loop_var.get())

def on_note_len(val):
    with state_lock:
        state["note_len_ms"] = int(float(val))
        if state.get("play_on_change"):
            state["playing"] = True

def on_attack(val):
    with state_lock:
        state["attack"] = max(0.0, float(val))
        if state.get("play_on_change"):
            state["playing"] = True

def on_decay(val):
    with state_lock:
        state["decay"] = max(0.0, float(val))
        if state.get("play_on_change"):
            state["playing"] = True

def on_sustain(val):
    with state_lock:
        state["sustain"] = max(0.0, min(1.0, float(val)))
        if state.get("play_on_change"):
            state["playing"] = True

def on_release(val):
    with state_lock:
        state["release"] = max(0.0, float(val))
        if state.get("play_on_change"):
            state["playing"] = True

def on_hp_toggle():
    with state_lock:
        state["highpass"] = bool(hp_var.get())
        if state.get("play_on_change"):
            state["playing"] = True

def on_play_on_change():
    with state_lock:
        state["play_on_change"] = bool(poc_var.get())

# --- Presets ---
PRESETS = {
    "Pickup/Coin": {"wave":"triangle","freq":880,"vol":0.5,"attack":0.0,"decay":0.08,"sustain":0.0,"release":0.12},
    "Laser/Shoot": {"wave":"square","freq":480,"duty":0.2,"vol":0.5,"attack":0.0,"decay":0.02,"sustain":0.2,"release":0.05},
    "Explosion": {"wave":"noise","freq":200,"vol":0.7,"attack":0.0,"decay":0.2,"sustain":0.0,"release":0.3},
    "Powerup": {"wave":"saw","freq":520,"vol":0.5,"attack":0.0,"decay":0.1,"sustain":0.6,"release":0.25},
}

def _clamp(x, lo, hi):
    return max(lo, min(hi, x))

def apply_preset(name: str):
    base = PRESETS.get(name)
    if not base:
        return
    # Make a randomized copy each click (small jitter around base values)
    params = dict(base)
    if 'freq' in params:
        params['freq'] = _clamp(params['freq'] * random.uniform(0.9, 1.1), 50, 4000)
    if 'duty' in params:
        params['duty'] = _clamp(params['duty'] + random.uniform(-0.1, 0.1), 0.05, 0.95)
    if 'vol' in params:
        params['vol'] = _clamp(params['vol'] + random.uniform(-0.15, 0.15), 0.0, 1.0)
    for k in ('attack','decay','release'):
        if k in params:
            params[k] = _clamp(params[k] * random.uniform(0.7, 1.3), 0.0, 1.5)
    if 'sustain' in params:
        params['sustain'] = _clamp(params['sustain'] + random.uniform(-0.15, 0.15), 0.0, 1.0)

    with state_lock:
        for k, v in params.items():
            state[k] = v
        state["playing"] = True
    # sync controls
    wave_var.set(state["wave"])
    on_wave_change()
    sfreq.set(state["freq"])
    sduty.set(state.get("duty", 0.5))
    svol.set(state["vol"])
    sa.set(state.get("attack", 0.01))
    sdec.set(state.get("decay", 0.10))
    ss.set(state.get("sustain", 0.70))
    sr_.set(state.get("release", 0.20))

# --- GUI ---
root = tk.Tk()
root.title("8-Bit Synth (Python)")
try:
    # Minimal dark style
    style = ttk.Style()
    # On Windows, 'vista'/'clam' exist. Configure a darker palette.
    style.theme_use('clam')
    bg = '#2b2b2b'; fg = '#e6e6e6'; accent = '#3d3d40'
    style.configure('.', background=bg, foreground=fg)
    style.configure('TLabel', background=bg, foreground=fg)
    style.configure('TFrame', background=bg)
    style.configure('TLabelframe', background=bg, foreground=fg)
    style.configure('TLabelframe.Label', background=bg, foreground=fg)
    style.configure('TButton', background=accent, foreground=fg)
    style.configure('TCheckbutton', background=bg, foreground=fg)
    style.configure('TCombobox', fieldbackground=bg, background=accent, foreground=fg)
except Exception:
    pass

main = ttk.Frame(root, padding=10)
main.grid()

ttk.Label(main, text="Waveform").grid(row=0, column=0, sticky="w")
wave_var = tk.StringVar(value="square")
wave_box = ttk.Combobox(main, textvariable=wave_var, values=["square","triangle","saw","noise"], state="readonly", width=10)
wave_box.grid(row=0, column=1, sticky="we")
wave_box.bind("<<ComboboxSelected>>", on_wave_change)

ttk.Label(main, text="Freq (Hz)").grid(row=1, column=0, sticky="w")
sfreq = ttk.Scale(main, from_=50, to=2000, value=220, command=on_freq)
sfreq.grid(row=1, column=1, sticky="we")

ttk.Label(main, text="Duty (square)").grid(row=2, column=0, sticky="w")
sduty = ttk.Scale(main, from_=0.05, to=0.95, value=0.5, command=on_duty)
sduty.grid(row=2, column=1, sticky="we")

ttk.Label(main, text="Volume").grid(row=3, column=0, sticky="w")
svol = ttk.Scale(main, from_=0.0, to=1.0, value=0.4, command=on_vol)
svol.grid(row=3, column=1, sticky="we")

ttk.Label(main, text="Bit depth").grid(row=4, column=0, sticky="w")
sbits = ttk.Scale(main, from_=4, to=12, value=8, command=on_bits)
sbits.grid(row=4, column=1, sticky="we")

# Playback controls & presets
loop_var = tk.BooleanVar(value=False)
ttk.Checkbutton(main, text="Loop", variable=loop_var, command=on_loop_toggle).grid(row=0, column=2, padx=(10,0))
ttk.Button(main, text="Play", command=on_play).grid(row=1, column=2, padx=(10,0))
ttk.Button(main, text="Stop", command=on_stop).grid(row=2, column=2, padx=(10,0))

ttk.Label(main, text="Note len (ms)").grid(row=3, column=2, sticky="w")
sdur = ttk.Scale(main, from_=50, to=2000, value=500, command=on_note_len)
sdur.grid(row=4, column=2, sticky="we")

preset_frame = ttk.LabelFrame(main, text="Presets", padding=6)
preset_frame.grid(row=0, column=3, rowspan=5, sticky="nswe", padx=(10,0))
# One button per preset; applies and plays immediately
for i, name in enumerate(PRESETS.keys()):
    ttk.Button(preset_frame, text=name, command=lambda n=name: apply_preset(n)).grid(row=i, column=0, sticky='we', pady=2)

controls_frame = ttk.Frame(main)
controls_frame.grid(row=6, column=1, columnspan=3, sticky='we')
poc_var = tk.BooleanVar(value=True)
ttk.Checkbutton(controls_frame, text='Play on change', variable=poc_var, command=on_play_on_change).grid(row=0, column=0, sticky='w')

# ADSR controls
adsr_frame = ttk.LabelFrame(main, text="ADSR", padding=6)
adsr_frame.grid(row=5, column=0, columnspan=3, sticky="we", pady=(10,0))
ttk.Label(adsr_frame, text="Attack (s)").grid(row=0, column=0, sticky="w")
sa = ttk.Scale(adsr_frame, from_=0.0, to=0.5, value=0.01, command=on_attack)
sa.grid(row=0, column=1, sticky="we")
ttk.Label(adsr_frame, text="Decay (s)").grid(row=1, column=0, sticky="w")
sdec = ttk.Scale(adsr_frame, from_=0.0, to=1.0, value=0.10, command=on_decay)
sdec.grid(row=1, column=1, sticky="we")
ttk.Label(adsr_frame, text="Sustain").grid(row=2, column=0, sticky="w")
ss = ttk.Scale(adsr_frame, from_=0.0, to=1.0, value=0.70, command=on_sustain)
ss.grid(row=2, column=1, sticky="we")
ttk.Label(adsr_frame, text="Release (s)").grid(row=3, column=0, sticky="w")
sr_ = ttk.Scale(adsr_frame, from_=0.0, to=1.0, value=0.20, command=on_release)
sr_.grid(row=3, column=1, sticky="we")

# Filters
hp_var = tk.BooleanVar(value=True)
ttk.Checkbutton(main, text="High-pass", variable=hp_var, command=on_hp_toggle).grid(row=6, column=0, sticky="w", pady=(8,0))

for i in range(2):
    main.columnconfigure(i, weight=1)
main.columnconfigure(2, weight=0)

running = threading.Event()
running.set()
thread = threading.Thread(target=run_audio, daemon=True)
thread.start()

def on_close():
    running.clear()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
