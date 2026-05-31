import tkinter as tk
import time as _time

# ══════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════
BG        = "#0d1117"
RAIL_CLR  = "#00ff88"
WIRE_CLR  = "#00ff88"
SYM_CLR   = "#00ff88"
LABEL_CLR = "#8892a4"
BTN_BG    = "#161b22"
BTN_HOV   = "#21262d"
BTN_ACT   = "#00ff88"
TEXT_CLR  = "#e6edf3"
RUNG_H    = 100
RUNG_PAD  = 60
COL_W     = 80
BRANCH_H  = 70

# ══════════════════════════════════════════════════════════════
#  LEVEL DEFINITIONS
#  Each level has:
#    title, description, hint,
#    inputs: {var: initial_bool},
#    target_outputs: {var: bool}  — what the user must achieve
#    locked_inputs: set of var names the user cannot toggle
# ══════════════════════════════════════════════════════════════
LEVELS = [
    {
        "title":        "Level 1 — Power On",
        "description":  "Create a rung that always passes power to energise output Q1.",
        "hint":         "Place a Normally Open contact assigned to I1,\nthen an Output Coil assigned to Q1.\nTurn I1 ON in the inputs bar.",
        "inputs":       {"I1": False},
        "target_outputs": {"Q1": True},
        "locked_inputs":  set(),
    },
    {
        "title":        "Level 2 — AND Gate",
        "description":  "Q1 must only be ON when BOTH I1 AND I2 are ON.",
        "hint":         "Place two NO contacts (I1 and I2) in series,\nthen an Output Coil (Q1).\nBoth must be ON for Q1 to energise.",
        "inputs":       {"I1": False, "I2": False},
        "target_outputs": {"Q1": True},
        "locked_inputs":  set(),
    },
    {
        "title":        "Level 3 — OR Gate",
        "description":  "Q1 must be ON when EITHER I1 OR I2 is ON.",
        "hint":         "Place a column with two NO contacts in parallel\n(use Add Branch), one for I1 and one for I2.\nEither being ON will pass power.",
        "inputs":       {"I1": False, "I2": False},
        "target_outputs": {"Q1": True},
        "locked_inputs":  set(),
    },
    {
        "title":        "Level 4 — NOT Gate",
        "description":  "Q1 must be ON when I1 is OFF, and OFF when I1 is ON.",
        "hint":         "Use a Normally Closed contact assigned to I1.\nNC contacts pass power when their variable is FALSE.",
        "inputs":       {"I1": False},
        "target_outputs": {"Q1": True},
        "locked_inputs":  set(),
    },
    {
        "title":        "Level 5 — Seal Circuit",
        "description":  "Q1 latches ON when I1 is pressed. I2 (NC) acts as a stop.",
        "hint":         "Place I1 (NO) in parallel with Q1 (NO — self-seal).\nPlace I2 (NC) in series before the coil.\nQ1 stays ON after I1 is released.",
        "inputs":       {"I1": False, "I2": False},
        "target_outputs": {"Q1": True},
        "locked_inputs":  set(),
    },
    {
        "title":        "Level 6 — NAND Gate",
        "description":  "Q1 must be OFF only when both I1 AND I2 are ON.",
        "hint":         "Use NC contacts for I1 and I2 in parallel.\nIf either is off, power still flows.\nOnly both ON blocks Q1.",
        "inputs":       {"I1": False, "I2": False},
        "target_outputs": {"Q1": True},
        "locked_inputs":  set(),
    },
    {
        "title":        "Level 7 — NOR Gate",
        "description":  "Q1 must only be ON when BOTH I1 AND I2 are OFF.",
        "hint":         "Use NC contacts for I1 and I2 in series.\nEither being ON will block power to Q1.",
        "inputs":       {"I1": False, "I2": False},
        "target_outputs": {"Q1": True},
        "locked_inputs":  set(),
    },
    {
        "title":        "Level 8 — Two Outputs",
        "description":  "I1 controls Q1. I2 controls Q2. Each on its own rung.",
        "hint":         "Add two rungs. Rung 1: I1 (NO) → Q1.\nRung 2: I2 (NO) → Q2.\nBoth must be independently controllable.",
        "inputs":       {"I1": False, "I2": False},
        "target_outputs": {"Q1": True, "Q2": True},
        "locked_inputs":  set(),
    },
    {
        "title":        "Level 9 — Timer Delay",
        "description":  "Q1 must turn ON 2 seconds after I1 is turned ON.",
        "hint":         "Create a variable T1 as INT and set it to 2000ms.\nPlace I1 (NO), then Timer (TON) assigned to T1,\nthen Q1 coil. Turn I1 ON and wait.",
        "inputs":       {"I1": False},
        "target_outputs": {"Q1": True},
        "locked_inputs":  set(),
    },
    {
        "title":        "Level 10 — Master Control",
        "description":  "E-Stop (I3, NC) must cut power to ALL outputs.\nI1 controls Q1, I2 controls Q2.\nWhen I3 is ON, both outputs go OFF.",
        "hint":         "Place I3 (NC) first in both rungs as a master guard.\nThen I1→Q1 in rung 1, I2→Q2 in rung 2.\nToggling I3 ON should kill everything.",
        "inputs":       {"I1": False, "I2": False, "I3": False},
        "target_outputs": {"Q1": True, "Q2": True},
        "locked_inputs":  set(),
    },
]

# ══════════════════════════════════════════════════════════════
#  SYMBOL DRAW FUNCTIONS
# ══════════════════════════════════════════════════════════════

def _draw_contact_bars(c, cx, cy):
    g = 18
    c.create_line(cx-40, cy, cx-g, cy,    fill=SYM_CLR, width=2)
    c.create_line(cx+g,  cy, cx+40, cy,   fill=SYM_CLR, width=2)
    c.create_line(cx-g, cy-g, cx-g, cy+g, fill=SYM_CLR, width=2)
    c.create_line(cx+g, cy-g, cx+g, cy+g, fill=SYM_CLR, width=2)

def draw_no(c, cx, cy):
    _draw_contact_bars(c, cx, cy)
    c.create_text(cx, cy-26, text="NO", fill=LABEL_CLR, font=("Courier", 8))

def draw_nc(c, cx, cy):
    g = 18
    c.create_line(cx-40, cy, cx-g, cy,    fill=SYM_CLR, width=2)
    c.create_line(cx+g,  cy, cx+40, cy,   fill=SYM_CLR, width=2)
    c.create_line(cx-g, cy-g, cx-g, cy+g, fill=SYM_CLR, width=2)
    c.create_line(cx+g, cy-g, cx+g, cy+g, fill=SYM_CLR, width=2)
    c.create_line(cx-g, cy+g, cx+g, cy-g, fill=SYM_CLR, width=2)
    c.create_text(cx, cy-26, text="NC",   fill=LABEL_CLR, font=("Courier", 8))

def draw_p_contact(c, cx, cy):
    g = 18
    _draw_contact_bars(c, cx, cy)
    c.create_line(cx, cy+g-2,  cx, cy-g+2,  fill=SYM_CLR, width=2)
    c.create_line(cx-5, cy-g+7, cx, cy-g+2, fill=SYM_CLR, width=2)
    c.create_line(cx+5, cy-g+7, cx, cy-g+2, fill=SYM_CLR, width=2)
    c.create_text(cx, cy-26, text="P",       fill=LABEL_CLR, font=("Courier", 8))

def draw_n_contact(c, cx, cy):
    g = 18
    _draw_contact_bars(c, cx, cy)
    c.create_line(cx, cy-g+2,  cx, cy+g-2,  fill=SYM_CLR, width=2)
    c.create_line(cx-5, cy+g-7, cx, cy+g-2, fill=SYM_CLR, width=2)
    c.create_line(cx+5, cy+g-7, cx, cy+g-2, fill=SYM_CLR, width=2)
    c.create_text(cx, cy-26, text="N",       fill=LABEL_CLR, font=("Courier", 8))

def draw_coil(c, cx, cy):
    r = 18
    c.create_line(cx-40, cy, cx-r, cy,    fill=SYM_CLR, width=2)
    c.create_line(cx+r,  cy, cx+40, cy,   fill=SYM_CLR, width=2)
    c.create_oval(cx-r, cy-r, cx+r, cy+r, outline=SYM_CLR, width=2)
    c.create_text(cx, cy-26, text="OUT",   fill=LABEL_CLR, font=("Courier", 8))

def draw_neg(c, cx, cy):
    r = 18
    c.create_line(cx-40, cy, cx-r, cy,    fill=SYM_CLR, width=2)
    c.create_line(cx+r,  cy, cx+40, cy,   fill=SYM_CLR, width=2)
    c.create_oval(cx-r, cy-r, cx+r, cy+r, outline=SYM_CLR, width=2)
    c.create_line(cx-r+5, cy+r-5, cx+r-5, cy-r+5, fill=SYM_CLR, width=2)
    c.create_text(cx, cy-26, text="NEG",   fill=LABEL_CLR, font=("Courier", 8))

def draw_ton(c, cx, cy):
    bw, bh = 28, 18
    c.create_line(cx-40, cy, cx-bw, cy,    fill=SYM_CLR, width=2)
    c.create_line(cx+bw, cy, cx+40, cy,    fill=SYM_CLR, width=2)
    c.create_rectangle(cx-bw, cy-bh, cx+bw, cy+bh, outline=SYM_CLR, width=2)
    c.create_text(cx, cy,      text="TON",   fill=SYM_CLR,   font=("Courier", 9, "bold"))
    c.create_text(cx, cy-bh-8, text="TIMER", fill=LABEL_CLR, font=("Courier", 8))

CONTACT_DRAW = {"NO": draw_no, "NC": draw_nc, "P": draw_p_contact, "N": draw_n_contact}
SYMBOLS = {
    "Contact":        ("NO",  draw_no),
    "Output Coil":    ("OUT", draw_coil),
    "Timer (TON)":    ("TON", draw_ton),
    "Negated Output": ("NEG", draw_neg),
}
TOOLTIP_TEXT = {
    "Contact":        "Contact\n\nClick: change type (NO/NC/P/N)\nDrag: move or remove",
    "Output Coil":    "Output Coil\n\nEnergises when rung has power.",
    "Timer (TON)":    "Timer On-Delay\n\nFires after INT variable ms.",
    "Negated Output": "Negated Output\n\nEnergises when rung lacks power.",
}

# ══════════════════════════════════════════════════════════════
#  GEOMETRY HELPERS
# ══════════════════════════════════════════════════════════════

def sym_half(sym_name):
    if sym_name == "Contact":     return 40
    if sym_name == "Timer (TON)": return 28
    return 18

def rung_height(rung):
    if not rung: return RUNG_H
    return RUNG_H + max(0, max(len(c["branches"]) for c in rung) - 1) * BRANCH_H

def branch_ys(cy, n):
    if n == 1: return [cy]
    top = cy - (n-1)*BRANCH_H//2
    return [top + i*BRANCH_H for i in range(n)]

def rung_layout(rung, cw):
    usable = cw - 2*RUNG_PAD
    n      = len(rung)
    slot_w = min(COL_W, usable // max(n, 1))
    start  = RUNG_PAD + (usable - slot_w*n)//2
    return slot_w, start

def new_entry(sym_name):
    base = {"type": sym_name, "variable": None}
    if sym_name == "Contact":
        base["contact_type"] = "NO"
    return base

def new_col(entry):
    return {"branches": [entry]}

# ══════════════════════════════════════════════════════════════
#  APP STATE
# ══════════════════════════════════════════════════════════════
rungs             = [[]]
active_rung       = 0
variable_registry = {}
var_counter       = [0]
sim_running       = False
input_states      = {}
output_states     = {}
timer_state       = {}
selected_col      = None
branch_undo_stack = []
current_level     = None   # None = free play, int = level index
current_screen    = "start"  # "start" | "levels" | "editor"

# ══════════════════════════════════════════════════════════════
#  WINDOW
# ══════════════════════════════════════════════════════════════
window = tk.Tk()
window.title("Ladder Logic Trainer")
window.configure(bg=BG)
window.geometry("960x680")
window.resizable(True, True)

# ══════════════════════════════════════════════════════════════
#  SCREEN MANAGEMENT — single container, swap frames
# ══════════════════════════════════════════════════════════════
root_frame = tk.Frame(window, bg=BG)
root_frame.pack(fill="both", expand=True)

def _clear_root():
    for w in root_frame.winfo_children():
        w.destroy()

# ══════════════════════════════════════════════════════════════
#  START SCREEN
# ══════════════════════════════════════════════════════════════
def show_start_screen():
    global current_screen
    current_screen = "start"
    _clear_root()

    frame = tk.Frame(root_frame, bg=BG)
    frame.pack(fill="both", expand=True)

    # Decorative top bar
    tk.Frame(frame, bg=RAIL_CLR, height=3).pack(fill="x")

    # Logo / title area
    title_frame = tk.Frame(frame, bg=BG)
    title_frame.pack(pady=(60, 0))

    tk.Label(title_frame, text="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
             bg=BG, fg="#1e3a2a", font=("Courier", 14)).pack()
    tk.Label(title_frame, text="  LADDER  LOGIC  TRAINER  ",
             bg=BG, fg=RAIL_CLR, font=("Courier", 32, "bold")).pack(pady=(8, 4))
    tk.Label(title_frame, text="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
             bg=BG, fg="#1e3a2a", font=("Courier", 14)).pack()

    tk.Label(frame,
             text="Learn PLC ladder logic through interactive challenges.",
             bg=BG, fg=LABEL_CLR, font=("Courier", 11)).pack(pady=(20, 40))

    # Button group
    btn_frame = tk.Frame(frame, bg=BG)
    btn_frame.pack()

    def _btn(parent, text, cmd, accent=False, width=22):
        return tk.Button(parent, text=text, command=cmd,
                         bg=RAIL_CLR if accent else BTN_BG,
                         fg=BG if accent else TEXT_CLR,
                         activebackground="#00cc66" if accent else BTN_HOV,
                         activeforeground=BG if accent else TEXT_CLR,
                         relief="flat", font=("Courier", 11, "bold"),
                         padx=16, pady=10, cursor="hand2", width=width,
                         bd=0)

    _btn(btn_frame, "▶   START TRAINING", show_level_screen, accent=True).pack(pady=8)
    _btn(btn_frame, "    FREE PLAY",       lambda: load_editor(None)).pack(pady=8)

    # Bottom credits / version bar
    tk.Frame(frame, bg="#1a1a1a", height=1).pack(fill="x", side="bottom", pady=(0,0))
    tk.Label(frame, text="10 levels  •  4 symbol types  •  real PLC logic",
             bg=BG, fg="#333d46", font=("Courier", 9)).pack(side="bottom", pady=10)
    tk.Frame(frame, bg=RAIL_CLR, height=3).pack(fill="x", side="bottom")

# ══════════════════════════════════════════════════════════════
#  LEVEL SELECT SCREEN
# ══════════════════════════════════════════════════════════════
def show_level_screen():
    global current_screen
    current_screen = "levels"
    _clear_root()

    outer = tk.Frame(root_frame, bg=BG)
    outer.pack(fill="both", expand=True)

    tk.Frame(outer, bg=RAIL_CLR, height=3).pack(fill="x")

    header = tk.Frame(outer, bg=BG)
    header.pack(fill="x", padx=20, pady=(16, 0))

    tk.Button(header, text="← BACK", command=show_start_screen,
              bg=BTN_BG, fg=LABEL_CLR,
              activebackground=BTN_HOV, activeforeground=TEXT_CLR,
              relief="flat", font=("Courier", 9, "bold"),
              padx=10, pady=4, cursor="hand2").pack(side="left")

    tk.Label(header, text="SELECT LEVEL", bg=BG, fg=RAIL_CLR,
             font=("Courier", 16, "bold")).pack(side="left", padx=20)

    tk.Frame(outer, bg="#1e2a1e", height=1).pack(fill="x", padx=20, pady=10)

    # Scrollable grid of level cards
    grid_outer = tk.Frame(outer, bg=BG)
    grid_outer.pack(fill="both", expand=True, padx=20, pady=10)

    grid = tk.Frame(grid_outer, bg=BG)
    grid.pack()

    for idx, lvl in enumerate(LEVELS):
        col = idx % 5
        row = idx // 5

        card = tk.Frame(grid, bg=BTN_BG, width=160, height=120,
                        highlightbackground="#2a3a2a", highlightthickness=1)
        card.grid(row=row, column=col, padx=8, pady=8)
        card.pack_propagate(False)

        num_lbl = tk.Label(card, text=f"{idx+1:02d}",
                           bg=BTN_BG, fg=RAIL_CLR,
                           font=("Courier", 22, "bold"))
        num_lbl.pack(pady=(14, 2))

        # Short title (strip "Level N — ")
        short = lvl["title"].split("—")[-1].strip() if "—" in lvl["title"] else lvl["title"]
        tk.Label(card, text=short, bg=BTN_BG, fg=TEXT_CLR,
                 font=("Courier", 8), wraplength=140,
                 justify="center").pack(padx=6)

        # Hover highlight
        def _enter(e, c=card, n=num_lbl):
            c.config(bg="#1e2e1e", highlightbackground=RAIL_CLR)
            n.config(bg="#1e2e1e")
            for w in c.winfo_children():
                try: w.config(bg="#1e2e1e")
                except: pass

        def _leave(e, c=card, n=num_lbl):
            c.config(bg=BTN_BG, highlightbackground="#2a3a2a")
            n.config(bg=BTN_BG)
            for w in c.winfo_children():
                try: w.config(bg=BTN_BG)
                except: pass

        def _click(e, i=idx):
            load_editor(i)

        for widget in [card] + list(card.winfo_children()):
            widget.bind("<Enter>",   _enter)
            widget.bind("<Leave>",   _leave)
            widget.bind("<Button-1>", _click)
            widget.config(cursor="hand2")

    tk.Frame(outer, bg=RAIL_CLR, height=3).pack(fill="x", side="bottom")

# ══════════════════════════════════════════════════════════════
#  EDITOR SCREEN
# ══════════════════════════════════════════════════════════════
def load_editor(level_idx):
    """Wipe state and launch the editor, optionally seeded with a level."""
    global current_screen, current_level
    global rungs, active_rung, variable_registry, var_counter
    global sim_running, input_states, output_states, timer_state
    global selected_col, branch_undo_stack

    current_screen    = "editor"
    current_level     = level_idx

    # Reset all state
    rungs             = [[]]
    active_rung       = 0
    variable_registry = {}
    var_counter[0]    = 0
    sim_running       = False
    input_states      = {}
    output_states     = {}
    timer_state       = {}
    selected_col      = None
    branch_undo_stack = []

    # Seed level variables and inputs
    if level_idx is not None:
        lvl = LEVELS[level_idx]
        for var, state in lvl["inputs"].items():
            variable_registry[var] = {"type": "bool", "value": False}
            input_states[var]      = state
        # Pre-create output variables
        for var in lvl["target_outputs"]:
            if var not in variable_registry:
                variable_registry[var] = {"type": "bool", "value": False}
        var_counter[0] = len(variable_registry)

    _clear_root()
    _build_editor_ui()

def _build_editor_ui():
    """Construct the full editor UI inside root_frame."""
    # ── All editor widgets are built here ──────────────────────

    # ── Toolbar ───────────────────────────────────────────────
    toolbar = tk.Frame(root_frame, bg=BG, pady=6)
    toolbar.pack(fill="x", padx=10)

    left_f  = tk.Frame(toolbar, bg=BG)
    left_f.pack(side="left")
    right_f = tk.Frame(toolbar, bg=BG)
    right_f.pack(side="right")

    # Store timer ID so we can cancel it
    _tick_id = [None]
    
    def _tick():
        if current_screen == "editor" and sim_running:
            try:
                canvas.winfo_exists()
                _evaluate()
            except tk.TclError:
                return
        if current_screen == "editor":
            _tick_id[0] = window.after(100, _tick)
    
    # Start the tick
    _tick_id[0] = window.after(100, _tick)

    # Back button
    def _go_back():
        # Cancel the timer
        if _tick_id[0]:
            window.after_cancel(_tick_id[0])
        if current_level is None:
            show_start_screen()
        else:
            show_level_screen()

    tk.Button(left_f, text="←", command=_go_back,
              bg=BTN_BG, fg=LABEL_CLR,
              activebackground=BTN_HOV, activeforeground=TEXT_CLR,
              relief="flat", font=("Courier", 10, "bold"),
              padx=8, pady=4, cursor="hand2").pack(side="left", padx=(0,6))

    # Title
    if current_level is not None:
        title_text = LEVELS[current_level]["title"]
    else:
        title_text = "FREE PLAY"
    tk.Label(left_f, text=title_text, bg=BG, fg=RAIL_CLR,
             font=("Courier", 10, "bold")).pack(side="left", padx=(0,14))

    def _make_btn(parent, label, cmd, accent=False):
        b = tk.Button(parent, text=label, command=cmd,
                      bg=BTN_BG, fg=BTN_ACT if accent else TEXT_CLR,
                      activebackground=BTN_HOV, activeforeground=TEXT_CLR,
                      relief="flat", font=("Courier", 9, "bold"),
                      padx=10, pady=4, cursor="hand2",
                      bd=1, highlightbackground="#30363d")
        b.pack(side="left", padx=3)
        return b

    # ── Add/remove rung helpers ────────────────────────────────
    def _add_rung():
        global active_rung
        rungs.append([]); active_rung=len(rungs)-1; _refresh()

    def _undo_last():
        global active_rung
        if branch_undo_stack:
            ri,ci,bi=branch_undo_stack.pop()
            if ri<len(rungs) and ci<len(rungs[ri]):
                brs=rungs[ri][ci]["branches"]
                if bi<len(brs) and len(brs)>1: brs.pop(bi)
            _refresh(); return
        if rungs[active_rung]:    rungs[active_rung].pop()
        elif len(rungs)>1:
            rungs.pop(active_rung)
            active_rung=min(active_rung,len(rungs)-1)
        _refresh()

    def _clear_all():
        global active_rung, selected_col
        rungs.clear(); rungs.append([])
        active_rung=0; selected_col=None
        branch_undo_stack.clear()
        input_states.clear(); output_states.clear(); timer_state.clear()
        if current_level is not None:
            lvl=LEVELS[current_level]
            for v,s in lvl["inputs"].items():
                input_states[v]=s
        _refresh()

    def _show_hint():
        if current_level is None: return
        d=tk.Toplevel(window); d.title("Hint"); d.configure(bg=BG)
        d.geometry("360x220"); d.resizable(False,False)
        tk.Label(d,text="HINT",bg=BG,fg=RAIL_CLR,
                 font=("Courier",12,"bold")).pack(pady=(16,8))
        tk.Label(d,text=LEVELS[current_level]["hint"],
                 bg=BG,fg=TEXT_CLR,font=("Courier",9),
                 justify="left",wraplength=320).pack(padx=20)
        tk.Button(d,text="OK",command=d.destroy,
                  bg=BTN_BG,fg=TEXT_CLR,relief="flat",
                  font=("Courier",9,"bold"),padx=12,pady=4,
                  cursor="hand2").pack(pady=16)

    # Track UI elements that should be disabled during run
    _editable_widgets = []  # List of widgets to enable/disable

    # Now create the buttons
    _make_btn(left_f, "+ New Rung",   _add_rung)
    branch_btn = _make_btn(left_f, "⊥ Add Branch", None)
    _make_btn(left_f, "⌫  Undo",      _undo_last)
    _make_btn(left_f, "✕  Clear",     _clear_all)

    # Run/Stop button (right side)
    def _toggle_run():
        global sim_running
        sim_running = not sim_running
        if sim_running:
            run_btn.config(text="■  STOP", fg="#ff4444")
            # Disable editing
            _set_editable(False)
            # Clear previous states and start fresh
            output_states.clear()
            timer_state.clear()
            _evaluate()
        else:
            run_btn.config(text="▶  RUN", fg="#00ff88")
            # Re-enable editing
            _set_editable(True)
            # Clear simulation state
            output_states.clear()
            timer_state.clear()
            _redraw()
            _update_input_bar()
            # Reset success label
            success_lbl.config(text="")

    run_btn = tk.Button(right_f, text="▶  RUN", command=_toggle_run,
                        bg=BTN_BG, fg="#00ff88",
                        activebackground=BTN_HOV, activeforeground=TEXT_CLR,
                        relief="flat", font=("Courier", 9, "bold"),
                        padx=10, pady=4, cursor="hand2",
                        bd=1, highlightbackground="#30363d")
    run_btn.pack(side="right", padx=3)

    # Hint button (levels only)
    if current_level is not None:
        _make_btn(right_f, "?  Hint", _show_hint)

    def _set_editable(editable):
        """Enable or disable all editing widgets during run/stop."""
        state = "normal" if editable else "disabled"
        cursor_val = "hand2" if editable else "arrow"
        
        # Disable palette
        for child in palette.winfo_children():
            try:
                child.config(state=state, cursor=cursor_val)
            except tk.TclError:
                pass
        
        # Disable toolbar editing buttons (but not Run or Hint)
        for btn in left_f.winfo_children():
            if isinstance(btn, tk.Button):
                btn.config(state=state)
        
        # Disable variable panel interactions
        for child in var_panel.winfo_children():
            try:
                child.config(state=state, cursor=cursor_val)
            except tk.TclError:
                pass
        
        # Disable Add Branch button
        branch_btn.config(state=state)
        
        # Disable input buttons when running (they're toggles, keep them interactive)
        # Actually, inputs should remain toggleable during run
        
        # Disable canvas drag operations when running
        if not editable:
            canvas.unbind("<ButtonPress-1>")
            canvas.unbind("<B1-Motion>")
            canvas.unbind("<ButtonRelease-1>")
            canvas.config(cursor="arrow")
        else:
            canvas.bind("<ButtonPress-1>", _canvas_press)
            canvas.bind("<B1-Motion>", _canvas_motion)
            canvas.bind("<ButtonRelease-1>", _canvas_release)
            canvas.bind("<Motion>", lambda e: canvas.config(
                cursor="hand2" if _locate(canvas.canvasx(e.x), canvas.canvasy(e.y)) else "arrow"))

    # ── Level objective panel ──────────────────────────────────
    if current_level is not None:
        lvl = LEVELS[current_level]
        obj_bar = tk.Frame(root_frame, bg="#0a1a0a", pady=5)
        obj_bar.pack(fill="x", padx=10)
        tk.Label(obj_bar, text="OBJECTIVE:", bg="#0a1a0a", fg=LABEL_CLR,
                 font=("Courier", 8, "bold")).pack(side="left", padx=(6,10))
        tk.Label(obj_bar, text=lvl["description"],
                 bg="#0a1a0a", fg=TEXT_CLR,
                 font=("Courier", 8), wraplength=600,
                 justify="left").pack(side="left")

        # Target output indicators
        tgt_frame = tk.Frame(obj_bar, bg="#0a1a0a")
        tgt_frame.pack(side="right", padx=10)
        tk.Label(tgt_frame, text="TARGET:", bg="#0a1a0a", fg=LABEL_CLR,
                 font=("Courier", 7, "bold")).pack(side="left", padx=(0,6))
        for var, val in lvl["target_outputs"].items():
            tk.Label(tgt_frame, text=f"{var}={'ON' if val else 'OFF'}",
                     bg="#1e3a1e" if val else "#3a1e1e",
                     fg=RAIL_CLR if val else "#ff6666",
                     font=("Courier", 8, "bold"),
                     padx=6, pady=2).pack(side="left", padx=2)

    # ── Input bar ─────────────────────────────────────────────
    input_bar = tk.Frame(root_frame, bg="#0d1f0d", pady=4)
    input_bar.pack(fill="x", padx=10)
    tk.Label(input_bar, text="INPUTS:", bg="#0d1f0d", fg=LABEL_CLR,
             font=("Courier", 8, "bold")).pack(side="left", padx=(6,10))
    input_btn_frame = tk.Frame(input_bar, bg="#0d1f0d")
    input_btn_frame.pack(side="left", fill="x", expand=True)

    # Success indicator (right of input bar)
    success_lbl = tk.Label(input_bar, text="", bg="#0d1f0d",
                            font=("Courier", 9, "bold"))
    success_lbl.pack(side="right", padx=10)

    # ── Main layout: palette | canvas | var_panel ─────────────
    main_frame = tk.Frame(root_frame, bg=BG)
    main_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))

    palette = tk.Frame(main_frame, bg=BTN_BG, width=110)
    palette.pack(side="left", fill="y")
    palette.pack_propagate(False)

    tk.Label(palette, text="INSERT", bg=BTN_BG, fg=LABEL_CLR,
             font=("Courier", 8, "bold")).pack(pady=(10,6))
    tk.Frame(palette, bg="#30363d", height=1).pack(fill="x", padx=8, pady=(0,8))

    canvas_frame = tk.Frame(main_frame, bg=BG)
    canvas_frame.pack(side="left", fill="both", expand=True, padx=(6,0))

    canvas = tk.Canvas(canvas_frame, bg=BG, highlightthickness=0)
    sb     = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    var_panel = tk.Frame(main_frame, bg=BTN_BG, width=140)
    var_panel.pack(side="right", fill="y", padx=(6,0))
    var_panel.pack_propagate(False)
    tk.Label(var_panel, text="VARIABLES", bg=BTN_BG, fg=LABEL_CLR,
             font=("Courier", 8, "bold")).pack(pady=(10,4))
    tk.Frame(var_panel, bg="#30363d", height=1).pack(fill="x", padx=8, pady=(0,8))

    nv_frame = tk.Frame(var_panel, bg=BTN_BG)
    nv_frame.pack(fill="x", padx=8, pady=(0,8))
    var_list_frame = tk.Frame(var_panel, bg=BTN_BG)
    var_list_frame.pack(fill="both", expand=True)

    # ── Tooltip ───────────────────────────────────────────────
    tooltip = tk.Toplevel(window)
    tooltip.withdraw()
    tooltip.overrideredirect(True)
    tooltip.configure(bg="#21262d")
    tooltip.attributes('-topmost', True)
    _tt = tk.Label(tooltip, bg="#21262d", fg=TEXT_CLR,
                   font=("Courier", 9), justify="left",
                   padx=10, pady=8, wraplength=180)
    _tt.pack()

    def show_tip(event, name):
        _tt.config(text=TOOLTIP_TEXT.get(name, ""))
        tooltip.geometry(f"+{event.widget.winfo_rootx()+event.widget.winfo_width()+8}"
                         f"+{event.widget.winfo_rooty()}")
        tooltip.deiconify(); tooltip.lift()

    def hide_tip(_e): tooltip.withdraw()

    # ── Drag state ────────────────────────────────────────────
    drag = {"kind": None, "sym": None, "entry": None,
            "ri": None, "ci": None, "bi": None, "label": None}
    _press = {"x":0,"y":0,"ri":None,"ci":None,"bi":None,"dragging":False}
    DRAG_THRESH = 6

    def _float(event, text, bg, fg):
        lbl = tk.Label(window, text=text, bg=bg, fg=fg,
                       font=("Courier",8,"bold"), padx=6, pady=3, relief="flat")
        lbl.place(x=event.x_root-window.winfo_rootx()+8,
                  y=event.y_root-window.winfo_rooty()+8)
        drag["label"] = lbl

    def _move_float(event):
        if drag["label"]:
            drag["label"].place(x=event.x_root-window.winfo_rootx()+8,
                                y=event.y_root-window.winfo_rooty()+8)

    def _end_float():
        if drag["label"]:
            drag["label"].destroy()
            drag["label"] = None

    def _cxy(event):
        return (event.x_root - canvas.winfo_rootx() + canvas.canvasx(0),
                event.y_root - canvas.winfo_rooty() + canvas.canvasy(0))

    def _over(event, widget):
        wx,wy = widget.winfo_rootx(), widget.winfo_rooty()
        return wx<=event.x_root<=wx+widget.winfo_width() \
           and wy<=event.y_root<=wy+widget.winfo_height()

    def _panel_hl(active):
        col = "#3a0000" if active else BTN_BG
        bdr = "#ff4444" if active else BTN_BG
        for p in (palette, var_panel):
            p.config(bg=col, highlightbackground=bdr,
                     highlightthickness=2 if active else 0)
            for w in p.winfo_children():
                try: w.config(bg=col)
                except: pass

    def _find_drop(mx, my):
        cw = canvas.winfo_width(); y=40
        for i,rung in enumerate(rungs):
            rh = rung_height(rung)
            if y<=my<=y+rh and RUNG_PAD<=mx<=cw-RUNG_PAD:
                sw,st = rung_layout(rung if rung else [None], cw)
                ins   = len(rung)
                for j in range(len(rung)):
                    if mx < st+j*sw+sw//2: ins=j; break
                return i, ins
            y += rh
        return None

    def _locate(mx, my):
        cw=canvas.winfo_width(); y=40
        for i,rung in enumerate(rungs):
            rh=rung_height(rung); cy=y+rh//2
            if y<=my<=y+rh:
                if not rung: return None
                sw,st=rung_layout(rung,cw)
                for j,col in enumerate(rung):
                    sx=st+j*sw+sw//2
                    if abs(mx-sx)>sw//2: continue
                    for b,by in enumerate(branch_ys(cy,len(col["branches"]))):
                        if abs(my-by)<=BRANCH_H//2: return i,j,b
            y+=rh
        return None

    # Palette drag
    def _sym_drag_start(event, sym_name):
        drag["sym"] = sym_name
        _float(event, SYMBOLS[sym_name][0], RAIL_CLR, BG)
        window.bind("<B1-Motion>",       lambda e: _move_float(e))
        window.bind("<ButtonRelease-1>", _sym_drag_release)

    def _sym_drag_release(event):
        _end_float()
        window.unbind("<B1-Motion>")
        window.unbind("<ButtonRelease-1>")
        sn = drag["sym"]; drag["sym"] = None
        if not sn: return
        mx,my = _cxy(event)
        tgt   = _find_drop(mx,my)
        if tgt:
            global active_rung
            ri,ci = tgt; active_rung=ri
            rungs[ri].insert(ci, new_col(new_entry(sn)))
            _refresh()

    # Rung symbol drag
    def _canvas_press(event):
        mx=canvas.canvasx(event.x); my=canvas.canvasy(event.y)
        res=_locate(mx,my)
        if res:
            ri,ci,bi=res
            _press.update(x=event.x_root,y=event.y_root,
                          ri=ri,ci=ci,bi=bi,dragging=False)

    def _canvas_motion(event):
        if _press["ri"] is None: return
        dx=abs(event.x_root-_press["x"]); dy=abs(event.y_root-_press["y"])
        if not _press["dragging"] and (dx>DRAG_THRESH or dy>DRAG_THRESH):
            _press["dragging"]=True
            ri,ci,bi=_press["ri"],_press["ci"],_press["bi"]
            entry=rungs[ri][ci]["branches"][bi]
            drag.update(kind="rung",entry=entry,ri=ri,ci=ci,bi=bi)
            abbr,_=SYMBOLS.get(entry["type"],("?",None))
            _float(event,abbr,"#ff4444","white")
            window.bind("<B1-Motion>",       lambda e:(_move_float(e),_panel_hl(_over(e,palette) or _over(e,var_panel))))
            window.bind("<ButtonRelease-1>", _rung_release)
        elif _press["dragging"]:
            _move_float(event)
            _panel_hl(_over(event,palette) or _over(event,var_panel))

    def _rung_release(event):
        window.unbind("<B1-Motion>"); window.unbind("<ButtonRelease-1>")
        _end_float(); _panel_hl(False)
        ri,ci,bi=drag["ri"],drag["ci"],drag["bi"]
        if ri is None: return
        if _over(event,palette) or _over(event,var_panel):
            brs=rungs[ri][ci]["branches"]
            if len(brs)>1: brs.pop(bi)
            else:           rungs[ri].pop(ci)
            while len(rungs)>1 and not rungs[-1]: rungs.pop()
        else:
            mx,my=_cxy(event); tgt=_find_drop(mx,my)
            if tgt:
                global active_rung
                t_ri,t_ci=tgt
                entry=rungs[ri][ci]["branches"][bi]
                if len(rungs[ri][ci]["branches"])>1:
                    rungs[ri][ci]["branches"].pop(bi)
                else:
                    rungs[ri].pop(ci)
                    if t_ri==ri and t_ci>ci: t_ci-=1
                active_rung=t_ri
                rungs[t_ri].insert(t_ci,new_col(entry))
        drag.update(kind=None,ri=None,ci=None,bi=None,entry=None)
        _refresh()

    def _canvas_release(event):
        if _press["ri"] is None: return
        if not _press["dragging"]:
            if sim_running: 
                _press.update(ri=None,ci=None,bi=None,dragging=False)
                return  # Block contact menu during run
            ri,ci,bi=_press["ri"],_press["ci"],_press["bi"]
            _select_col(ri,ci)
            _contact_menu(event,ri,ci,bi)
        _press.update(ri=None,ci=None,bi=None,dragging=False)

    canvas.bind("<ButtonPress-1>",   _canvas_press)
    canvas.bind("<B1-Motion>",       _canvas_motion)
    canvas.bind("<ButtonRelease-1>", _canvas_release)
    canvas.bind("<Motion>", lambda e: canvas.config(
        cursor="hand2" if _locate(canvas.canvasx(e.x),canvas.canvasy(e.y)) else "arrow"))
    window.bind_all("<MouseWheel>",
        lambda e: canvas.yview_scroll(-1*(e.delta//120),"units"))

    # ── Column selection ───────────────────────────────────────
    def _select_col(ri,ci):
        global selected_col, active_rung
        active_rung=ri
        selected_col=None if selected_col==(ri,ci) else (ri,ci)
        _redraw()

    window.bind("<Escape>", lambda e: (_select_col.__func__ if hasattr(_select_col,"__func__") else None) or _deselect())

    def _deselect(e=None):
        if sim_running: return  # Don't allow deselection during run
        global selected_col
        selected_col=None; _redraw()
    window.bind("<Escape>", _deselect)

    # ── Variable drag ──────────────────────────────────────────
    def _var_drag_start(event, var_name):
        drag["sym"]=var_name
        _float(event,var_name,BTN_ACT,BG)
        window.bind("<B1-Motion>",       lambda e:_move_float(e))
        window.bind("<ButtonRelease-1>", lambda e:_var_drop(e,var_name))

    def _var_drop(event, var_name):
        _end_float()
        window.unbind("<B1-Motion>"); window.unbind("<ButtonRelease-1>")
        mx,my=_cxy(event); cw=canvas.winfo_width(); y=40
        for i,rung in enumerate(rungs):
            rh=rung_height(rung); cy=y+rh//2
            sw,st=rung_layout(rung,cw) if rung else (COL_W,RUNG_PAD)
            for j,col in enumerate(rung):
                sx=st+j*sw+sw//2
                for b,by in enumerate(branch_ys(cy,len(col["branches"]))):
                    if abs(mx-sx)<=sw//2 and abs(my-by)<=42:
                        col["branches"][b]["variable"]=var_name
                        _refresh(); return
            y+=rh


    def _add_branch_sel():
        if selected_col is not None:
            ri,ci=selected_col
            brs=rungs[ri][ci]["branches"]
            bi=len(brs)
            brs.append(new_entry("Contact"))
            branch_undo_stack.append((ri,ci,bi))
            _redraw()
        else:
            branch_btn.config(bg="#ff4444",fg="white")
            window.after(400,lambda:branch_btn.config(bg=BTN_BG,fg=TEXT_CLR))

    branch_btn.config(command=_add_branch_sel)

    # ── Logic evaluator ───────────────────────────────────────
    def _eval(entry, power_in):
        sym=entry["type"]; var=entry.get("variable")
        ctype=entry.get("contact_type","NO")
        if sym=="Contact":
            sig=input_states.get(var,False) if var else False
            if   ctype=="NO": lit=sig;      passes=power_in and sig
            elif ctype=="NC": lit=not sig;  passes=power_in and not sig
            else:
                lit=sig if ctype=="P" else not sig
                passes=power_in and lit
            return passes,lit
        if sym in ("Output Coil","Negated Output"):
            val=power_in if sym=="Output Coil" else not power_in
            if var: output_states[var]=val; input_states[var]=val
            return power_in,power_in
        if sym=="Timer (TON)":
            preset=1000
            if var and var in variable_registry:
                info=variable_registry[var]
                if info["type"]=="int": preset=max(1,info["value"])
            ts=timer_state.setdefault(var or id(entry),
                {"running":False,"start":0.0,"done":False})
            if power_in:
                if not ts["running"]:
                    ts["running"]=True; ts["start"]=_time.monotonic(); ts["done"]=False
                if (_time.monotonic()-ts["start"])*1000>=preset: ts["done"]=True
            else:
                ts["running"]=False; ts["done"]=False
            return (power_in and ts["done"]), ts["done"]
        return power_in,power_in

    def _evaluate():
        global output_states
        try:
            if not canvas.winfo_exists():
                return
        except tk.TclError:
            return
        output_states={}
        for rung in rungs:
            p=True
            for col in rung:
                p=p and any(_eval(e,p)[0] for e in col["branches"])
        _redraw()
        _check_success()

    # ── Success check ──────────────────────────────────────────
    def _check_success():
        if current_level is None: return
        if not sim_running: 
            success_lbl.config(text="")
            return
        lvl=LEVELS[current_level]
        tgt=lvl["target_outputs"]
        ok=all(bool(output_states.get(v,False))==bool(want) for v,want in tgt.items())
        if ok:
            success_lbl.config(text="✓  OBJECTIVE MET!", fg=RAIL_CLR, bg="#0d1f0d")
        else:
            success_lbl.config(text="✗  Not yet...", fg="#ff6666", bg="#0d1f0d")


    # ── Contact type menu ──────────────────────────────────────
    def _contact_menu(event,ri,ci,bi):
        entry=rungs[ri][ci]["branches"][bi]
        if entry["type"]!="Contact": return
        menu=tk.Menu(window,tearoff=0,bg=BTN_BG,fg=TEXT_CLR,
                     activebackground=BTN_ACT,activeforeground=BG,
                     font=("Courier",9))
        cur=tk.StringVar(value=entry.get("contact_type","NO"))
        def _set(t): entry["contact_type"]=t; _evaluate() if sim_running else _redraw()
        for lbl,val in [("Normally Open (NO)","NO"),("Normally Closed (NC)","NC"),
                        ("Positive Edge (P)","P"),("Negative Edge (N)","N")]:
            menu.add_radiobutton(label=lbl,variable=cur,value=val,
                                 command=lambda v=val:_set(v))
        try:    menu.tk_popup(event.x_root,event.y_root)
        finally:menu.grab_release()

    # ── Drawing ────────────────────────────────────────────────
    def wclr(p): 
        if not sim_running: return "#2a2a2a"  # Grey when stopped
        return "#00ff88" if p else "#2a2a2a"
    def sclr(p): 
        if not sim_running: return "#444444"  # Grey when stopped
        return "#00ff88" if p else "#555555"

    def _draw_sym(c,entry,sx,sy,sc,wc):
        global SYM_CLR,WIRE_CLR
        SYM_CLR,WIRE_CLR=sc,wc
        fn=(CONTACT_DRAW.get(entry.get("contact_type","NO"),draw_no)
            if entry["type"]=="Contact"
            else SYMBOLS.get(entry["type"],(None,lambda *a:None))[1])
        fn(c,sx,sy)
        SYM_CLR=RAIL_CLR; WIRE_CLR=RAIL_CLR

    def _redraw(*_):
        try:
            if not canvas.winfo_exists():
                return
        except tk.TclError:
            return
            
            
        canvas.delete("all")
        cw=canvas.winfo_width() or 900
        total_h=80+sum(rung_height(r) for r in rungs)
        canvas.configure(scrollregion=(0,0,cw,max(total_h,300)))
        rl,rr=RUNG_PAD,cw-RUNG_PAD; y=40
        for i,rung in enumerate(rungs):
            rh=rung_height(rung); cy=y+rh//2; is_act=(i==active_rung)
            
            # Left rail always green, right rail grey when stopped
            canvas.create_line(rl,y,rl,y+rh,fill=RAIL_CLR,width=4)
            right_color = RAIL_CLR if sim_running else "#2a2a2a"
            canvas.create_line(rr,y,rr,y+rh,fill=right_color,width=4)
            canvas.create_text(rl-16,cy,text=str(i+1),
                               fill=RAIL_CLR if is_act else LABEL_CLR,
                               font=("Courier",8,"bold" if is_act else "normal"),
                               anchor="e")
            if not rung:
                canvas.create_line(rl,cy,rr,cy,fill=WIRE_CLR,width=2,dash=(6,4))
                y+=rh; continue
            # Power state
            col_pwr,entry_lit=[],[]
            p=True
            for col in rung:
                col_pwr.append(p); lr,ok=[],False
                for e in col["branches"]:
                    ps,lt=_eval(e,p) if sim_running else (False,False)
                    lr.append(lt); ok=ok or ps
                entry_lit.append(lr); p=p and ok
            fp=p
            sw,st=rung_layout(rung,cw)
            fh=sym_half(rung[0]["branches"][0]["type"])
            canvas.create_line(rl,cy,st+sw//2-fh,cy,fill=wclr(True),width=2)
            for j,col in enumerate(rung):
                brs=col["branches"]; nb=len(brs)
                sx=st+j*sw+sw//2; sh=sym_half(brs[0]["type"])
                bys=branch_ys(cy,nb)
                if nb>1:
                    ap=any(_eval(e,col_pwr[j])[0] for e in brs) if sim_running else False
                    canvas.create_line(sx-sh,bys[0],sx-sh,bys[-1],fill=wclr(col_pwr[j]),width=2)
                    canvas.create_line(sx+sh,bys[0],sx+sh,bys[-1],fill=wclr(ap),width=2)
                    canvas.create_line(sx-sw//2,cy,sx-sh,cy,fill=wclr(col_pwr[j]),width=2)
                for b,(entry,by) in enumerate(zip(brs,bys)):
                    lit=entry_lit[j][b] if entry_lit else False
                    _draw_sym(canvas,entry,sx,by,sclr(lit),sclr(col_pwr[j]))
                    lc="#00ff88" if (sim_running and lit) else "#555555" if sim_running else RAIL_CLR
                    canvas.create_text(sx,by-(48 if nb>1 else 36),
                                       text=entry.get("variable") or "?",
                                       fill=lc,font=("Courier",7 if nb>1 else 8,"bold"))
                if selected_col==(i,j):
                    canvas.create_rectangle(sx-sw//2+2,y+4,sx+sw//2-2,y+rh-4,
                                            outline="#00aaff",width=1,dash=(4,3))
                    canvas.create_text(sx,y+rh-10,text="selected",
                                       fill="#00aaff",font=("Courier",6))
                ss=sx+sh
                if j<len(rung)-1:
                    nh=sym_half(rung[j+1]["branches"][0]["type"])
                    canvas.create_line(ss,cy,st+(j+1)*sw+sw//2-nh,cy,
                                       fill=wclr(col_pwr[j]),width=2)
                else:
                    canvas.create_line(ss,cy,rr,cy,fill=wclr(fp),width=2)
            y+=rh

    def _refresh():
        try:
            if not canvas.winfo_exists():
                return
        except tk.TclError:
            return
        if sim_running:
            _evaluate()
        else:
            _redraw()
        _update_var_panel()
        _update_input_bar()

    # ── Input bar update ───────────────────────────────────────
    def _update_input_bar():
        for w in input_btn_frame.winfo_children(): w.destroy()
        cvars={e["variable"]
               for rung in rungs for col in rung for e in col["branches"]
               if e["type"]=="Contact" and e.get("variable")}
        locked = LEVELS[current_level]["locked_inputs"] if current_level is not None else set()
        if not cvars:
            tk.Label(input_btn_frame,
                     text="Assign variables to contacts to see inputs here.",
                     bg="#0d1f0d",fg="#444d56",font=("Courier",8)).pack(side="left")
            return
        for var in sorted(cvars):
            on=input_states.get(var,False)
            is_locked = var in locked
            b=tk.Button(input_btn_frame,
                        text=f"{var}  {'ON' if on else 'OFF'}",
                        bg="#00ff88" if on else "#1a1a1a",
                        fg=BG if on else "#444d56",
                        activebackground="#00cc66",activeforeground=BG,
                        relief="flat",font=("Courier",8,"bold"),
                        padx=8,pady=3,
                        cursor="arrow" if is_locked else "hand2",
                        state="disabled" if is_locked else "normal")
            b.pack(side="left",padx=3)
            if not is_locked:
                def _tog(v=var,btn=b):
                    input_states[v]=not input_states.get(v,False)
                    _refresh()
                b.config(command=_tog)

    # ── Variable panel update ──────────────────────────────────
    def _add_variable():
        var_counter[0]+=1
        v=f"VAR{var_counter[0]:03d}"
        variable_registry[v]={"type":"bool","value":False}
        _update_var_panel()

    tk.Button(nv_frame,text="+ New Variable",command=_add_variable,
              bg="#238636",fg=TEXT_CLR,activebackground="#2ea043",
              activeforeground=TEXT_CLR,relief="flat",
              font=("Courier",8,"bold"),padx=8,pady=4,
              cursor="hand2").pack(fill="x")

    def _del_var(var_name):
        variable_registry.pop(var_name,None)
        for rung in rungs:
            for col in rung:
                for e in col["branches"]:
                    if e.get("variable")==var_name: e["variable"]=None
        _refresh()

    def _mk_del_btn(parent, var):
        c=tk.Canvas(parent,width=16,height=16,bg=BTN_BG,
                    highlightthickness=0,cursor="hand2")
        def _d(col):
            c.delete("all")
            c.create_line(4,4,12,12,fill=col,width=2)
            c.create_line(12,4,4,12,fill=col,width=2)
        _d("#444d56")
        c.bind("<Enter>",lambda e:_d("#ff4444"))
        c.bind("<Leave>",lambda e:_d("#444d56"))
        c.bind("<Button-1>",lambda e:_del_var(var))
        return c

    def _update_var_panel():
        for w in var_list_frame.winfo_children(): w.destroy()
        if not variable_registry:
            tk.Label(var_list_frame,text="No variables\ndefined yet",
                     bg=BTN_BG,fg="#444d56",
                     font=("Courier",8),justify="center").pack(pady=20)
            return
        for var in list(variable_registry.keys()):
            info=variable_registry[var]; vtype=info["type"]
            card=tk.Frame(var_list_frame,bg="#1e2430",
                          highlightbackground="#30363d",highlightthickness=1)
            card.pack(fill="x",padx=6,pady=3)
            r1=tk.Frame(card,bg="#1e2430"); r1.pack(fill="x",padx=4,pady=(4,1))
            lbl=tk.Label(r1,text=var,bg="#1e2430",fg=RAIL_CLR,
                         font=("Courier",8,"bold"),anchor="w",cursor="fleur")
            lbl.pack(side="left",fill="x",expand=True)
            lbl.bind("<ButtonPress-1>",lambda e,v=var:_var_drag_start(e,v))
            _mk_del_btn(r1,var).pack(side="right",padx=(4,0))
            r2=tk.Frame(card,bg="#1e2430"); r2.pack(fill="x",padx=4,pady=(1,2))
            for t,ltext in [("bool","BOOL"),("int","INT")]:
                act=(vtype==t)
                tb=tk.Button(r2,text=ltext,
                             bg=RAIL_CLR if act else "#2a2a2a",
                             fg=BG if act else "#555555",
                             activebackground=RAIL_CLR,activeforeground=BG,
                             relief="flat",font=("Courier",7,"bold"),
                             padx=6,pady=1,cursor="hand2")
                tb.pack(side="left",padx=(0,2))
                def _st(v=var,tp=t):
                    if variable_registry[v]["type"]==tp: return
                    variable_registry[v]["type"]=tp
                    variable_registry[v]["value"]=False if tp=="bool" else 0
                    _update_var_panel()
                tb.config(command=_st)
            if vtype=="int":
                r3=tk.Frame(card,bg="#1e2430"); r3.pack(fill="x",padx=4,pady=(0,4))
                tk.Label(r3,text="ms:",bg="#1e2430",fg=LABEL_CLR,
                         font=("Courier",7)).pack(side="left")
                sv=tk.StringVar(value=str(info["value"]))
                ew=tk.Entry(r3,textvariable=sv,width=6,
                            bg="#0d1117",fg=TEXT_CLR,insertbackground=TEXT_CLR,
                            relief="flat",font=("Courier",8),
                            highlightbackground="#30363d",highlightthickness=1)
                ew.pack(side="left",padx=(2,0))
                def _si(event=None,v=var,s=sv,w=ew):
                    try:
                        variable_registry[v]["value"]=max(0,int(s.get()))
                        w.config(bg="#0d1117")
                    except ValueError:
                        w.config(bg="#5a1a1a")
                ew.bind("<FocusOut>",_si); ew.bind("<Return>",_si)

    # ── Palette symbol icons ───────────────────────────────────
    for _sym in SYMBOLS:
        _abbr,_fn=SYMBOLS[_sym]
        _bf=tk.Frame(palette,bg=BTN_BG)
        _bf.pack(fill="x",padx=6,pady=3)
        _mc=tk.Canvas(_bf,width=90,height=44,bg=BTN_BG,
                      highlightthickness=1,highlightbackground="#30363d",
                      cursor="hand2")
        _mc.pack()
        (draw_no if _sym=="Contact" else _fn)(_mc,45,26)
        for item in _mc.find_all():
            if _mc.type(item)=="text": _mc.itemconfig(item,font=("Courier",6))
        _mc.bind("<ButtonPress-1>", lambda e,n=_sym:_sym_drag_start(e,n))
        _mc.bind("<Enter>",         lambda e,n=_sym:show_tip(e,n))
        _mc.bind("<Leave>",         hide_tip)
        _l=tk.Label(_bf,text="CONTACT" if _sym=="Contact" else _abbr,
                    bg=BTN_BG,fg=LABEL_CLR,font=("Courier",7),cursor="fleur")
        _l.pack()
        _l.bind("<ButtonPress-1>",  lambda e,n=_sym:_sym_drag_start(e,n))
        _l.bind("<Enter>",          lambda e,n=_sym:show_tip(e,n))
        _l.bind("<Leave>",          hide_tip)

    canvas.bind("<Configure>",_redraw)
    _refresh()

# ══════════════════════════════════════════════════════════════
#  LAUNCH
# ══════════════════════════════════════════════════════════════
show_start_screen()
window.mainloop()