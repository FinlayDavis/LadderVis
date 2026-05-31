import tkinter as tk

# ── Constants ─────────────────────────────────────────────────
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

# ── Symbol draw functions ─────────────────────────────────────
# All use global SYM_CLR / WIRE_CLR so _draw_entry can override them

def _draw_contact_bars(c, cx, cy):
    """Shared bars for all contact types — no label."""
    g = 18
    c.create_line(cx-40, cy, cx-g, cy,    fill=SYM_CLR, width=2)
    c.create_line(cx+g,  cy, cx+40, cy,   fill=SYM_CLR, width=2)
    c.create_line(cx-g, cy-g, cx-g, cy+g, fill=SYM_CLR, width=2)
    c.create_line(cx+g, cy-g, cx+g, cy+g, fill=SYM_CLR, width=2)

def draw_no(c, cx, cy):
    g = 18
    _draw_contact_bars(c, cx, cy)
    c.create_text(cx, cy-g-8, text="NO",   fill=LABEL_CLR, font=("Courier", 8))

def draw_nc(c, cx, cy):
    # Draw bars only — not draw_no, to avoid the NO label appearing underneath
    g = 18
    c.create_line(cx-40, cy, cx-g, cy,    fill=SYM_CLR, width=2)
    c.create_line(cx+g,  cy, cx+40, cy,   fill=SYM_CLR, width=2)
    c.create_line(cx-g, cy-g, cx-g, cy+g, fill=SYM_CLR, width=2)
    c.create_line(cx+g, cy-g, cx+g, cy+g, fill=SYM_CLR, width=2)
    c.create_line(cx-g, cy+g, cx+g, cy-g, fill=SYM_CLR, width=2)
    c.create_text(cx, cy-g-8, text="NC",  fill=LABEL_CLR, font=("Courier", 8))

def draw_p_contact(c, cx, cy):
    g = 18
    _draw_contact_bars(c, cx, cy)
    c.create_line(cx, cy+g-2,  cx, cy-g+2,  fill=SYM_CLR, width=2)
    c.create_line(cx-5, cy-g+7, cx, cy-g+2, fill=SYM_CLR, width=2)
    c.create_line(cx+5, cy-g+7, cx, cy-g+2, fill=SYM_CLR, width=2)
    c.create_text(cx, cy-g-8, text="P",      fill=LABEL_CLR, font=("Courier", 8))

def draw_n_contact(c, cx, cy):
    g = 18
    _draw_contact_bars(c, cx, cy)
    c.create_line(cx, cy-g+2,  cx, cy+g-2,  fill=SYM_CLR, width=2)
    c.create_line(cx-5, cy+g-7, cx, cy+g-2, fill=SYM_CLR, width=2)
    c.create_line(cx+5, cy+g-7, cx, cy+g-2, fill=SYM_CLR, width=2)
    c.create_text(cx, cy-g-8, text="N",      fill=LABEL_CLR, font=("Courier", 8))

def draw_coil(c, cx, cy):
    r = 18
    # Don't draw horizontal lines - let redraw handle wiring
    c.create_oval(cx-r, cy-r, cx+r, cy+r,  outline=SYM_CLR, width=2)
    c.create_text(cx, cy-r-8, text="OUT",  fill=LABEL_CLR, font=("Courier", 8))

def draw_neg(c, cx, cy):
    r = 18
    c.create_oval(cx-r, cy-r, cx+r, cy+r,  outline=SYM_CLR, width=2)
    c.create_line(cx-r+5, cy+r-5, cx+r-5, cy-r+5, fill=SYM_CLR, width=2)
    c.create_text(cx, cy-r-8, text="NEG",  fill=LABEL_CLR, font=("Courier", 8))

def draw_ton(c, cx, cy):
    bw, bh = 28, 18
    c.create_line(cx-40, cy, cx-bw, cy,    fill=SYM_CLR, width=2)
    c.create_line(cx+bw, cy, cx+40, cy,    fill=SYM_CLR, width=2)
    c.create_rectangle(cx-bw, cy-bh, cx+bw, cy+bh, outline=SYM_CLR, width=2)
    c.create_text(cx, cy,      text="TON",   fill=SYM_CLR,   font=("Courier", 9, "bold"))
    c.create_text(cx, cy-bh-8, text="TIMER", fill=LABEL_CLR, font=("Courier", 8))

# Contact type → draw function
CONTACT_DRAW = {"NO": draw_no, "NC": draw_nc, "P": draw_p_contact, "N": draw_n_contact}

SYMBOLS = {
    "Contact":       ("NO",  draw_no),
    "Output Coil":   ("OUT", draw_coil),
    "Timer (TON)":   ("TON", draw_ton),
    "Negated Output":("NEG", draw_neg),
}

TOOLTIP_TEXT = {
    "Contact":        "Contact\n\nClick to change type\n(NO, NC, P, N)\nDrag to move/remove",
    "Output Coil":    "Output Coil (OUT)\n\nEnergises when rung\nhas power.  --( )--",
    "Timer (TON)":    "Timer On-Delay (TON)\n\nFires after preset\ntime with power.",
    "Negated Output": "Negated Output (NEG)\n\nEnergises when rung\nlacks power. --(/)--",
}

# ── Geometry helpers ──────────────────────────────────────────

def sym_half(sym_name):
    """Half-width of a symbol's drawn extent."""
    if sym_name == "Contact":    return 40
    if sym_name == "Timer (TON)":return 28
    return 18

def rung_height(rung):
    if not rung:
        return RUNG_H
    max_b = max(len(col["branches"]) for col in rung)
    return RUNG_H + max(0, max_b - 1) * BRANCH_H

def branch_ys(cy, n):
    """Y positions for n branches centred on cy."""
    if n == 1:
        return [cy]
    top = cy - (n - 1) * BRANCH_H // 2
    return [top + i * BRANCH_H for i in range(n)]

def rung_layout(rung, cw):
    """Return (slot_w, start_x) for a rung given canvas width."""
    usable = cw - 2 * RUNG_PAD
    n      = len(rung)
    slot_w = min(COL_W, usable // max(n, 1))
    start  = RUNG_PAD + (usable - slot_w * n) // 2
    return slot_w, start

# ── Entry / column factories ──────────────────────────────────

def new_entry(sym_name):
    base = {"type": sym_name, "variable": None}
    if sym_name == "Contact":
        base["contact_type"] = "NO"
    return base

def new_col(entry):
    return {"branches": [entry]}

# ── App state ─────────────────────────────────────────────────

rungs          = [[]]
active_rung    = 0
variable_registry = {}
var_counter    = [0]
sim_running    = False
input_states   = {}
output_states  = {}
timer_state = {}   # var_name -> {"running": bool, "start": float, "done": bool}
selected_col = None   # (rung_idx, col_idx) or None
branch_undo_stack = []  # list of (ri, ci, branch_idx) for branch removals


# ── Window ────────────────────────────────────────────────────

window = tk.Tk()
window.title("Ladder Logic Editor")
window.configure(bg=BG)
window.geometry("960x680")
window.resizable(True, True)



# ── Toolbar ───────────────────────────────────────────────────

toolbar = tk.Frame(window, bg=BG, pady=6)
toolbar.pack(fill="x", padx=10)

tk.Label(toolbar, text="LADDER LOGIC EDITOR", bg=BG, fg=RAIL_CLR,
         font=("Courier", 11, "bold")).pack(side="left", padx=(4, 20))

def make_btn(parent, label, cmd, accent=False):
    b = tk.Button(parent, text=label, command=cmd,
                  bg=BTN_BG, fg=BTN_ACT if accent else TEXT_CLR,
                  activebackground=BTN_HOV, activeforeground=TEXT_CLR,
                  relief="flat", font=("Courier", 9, "bold"),
                  padx=10, pady=4, cursor="hand2",
                  bd=1, highlightbackground="#30363d")
    b.pack(side="left", padx=3)
    return b

def refresh():
    """Single call to rebuild everything after state changes."""
    redraw()
    update_variable_panel()
    update_input_bar()

def add_rung():
    global active_rung
    rungs.append([])
    active_rung = len(rungs) - 1
    refresh()

def undo_last():
    global active_rung
    # First undo any branch additions
    if branch_undo_stack:
        ri, ci, bi = branch_undo_stack.pop()
        if ri < len(rungs) and ci < len(rungs[ri]):
            branches = rungs[ri][ci]["branches"]
            if bi < len(branches) and len(branches) > 1:
                branches.pop(bi)
        refresh()
        return
    # Then undo column additions
    if rungs[active_rung]:
        rungs[active_rung].pop()
    elif len(rungs) > 1:
        rungs.pop(active_rung)
        active_rung = min(active_rung, len(rungs) - 1)
    refresh()

def clear_all():
    global active_rung, sim_running, selected_col
    rungs.clear(); rungs.append([])
    active_rung = 0
    selected_col = None
    branch_undo_stack.clear()
    input_states.clear(); output_states.clear()
    sim_running = True
    refresh()

# Create a frame for left buttons
left_btns = tk.Frame(toolbar, bg=BG)
left_btns.pack(side="left")

# Create a frame for right buttons
right_btns = tk.Frame(toolbar, bg=BG)
right_btns.pack(side="right")

# Left group — editing actions
make_btn(left_btns, "+ New Rung",   add_rung)
branch_btn = make_btn(left_btns, "⊥ Add Branch", None)
make_btn(left_btns, "⌫  Undo",      undo_last)
make_btn(left_btns, "✕  Clear All", clear_all)

# Run/Stop button on the right
def toggle_run():
    global sim_running
    sim_running = not sim_running
    if sim_running:
        run_btn.config(text="■  STOP", fg="#ff4444")
        evaluate_ladder()
    else:
        run_btn.config(text="▶  RUN", fg="#00ff88")
        # Clear all output states when stopping
        output_states.clear()
        timer_state.clear()
        input_states.clear()  # Also clear input states on stop
    redraw()
    update_input_bar()

run_btn = tk.Button(right_btns, text="▶  RUN", command=toggle_run,
                    bg=BTN_BG, fg="#00ff88",
                    activebackground=BTN_HOV, activeforeground=TEXT_CLR,
                    relief="flat", font=("Courier", 9, "bold"),
                    padx=10, pady=4, cursor="hand2",
                    bd=1, highlightbackground="#30363d")
run_btn.pack(side="right", padx=3)


# ── Tooltip ───────────────────────────────────────────────────

tooltip = tk.Toplevel(window)
tooltip.withdraw()
tooltip.overrideredirect(True)
tooltip.configure(bg="#21262d")
# Make sure tooltip doesn't steal focus
tooltip.attributes('-topmost', True)
tooltip.withdraw()  # Ensure it's hidden
_tt_label = tk.Label(tooltip, bg="#21262d", fg=TEXT_CLR,
                     font=("Courier", 9), justify="left",
                     padx=10, pady=8, wraplength=180)
_tt_label.pack()

def show_tooltip(event, name):
    _tt_label.config(text=TOOLTIP_TEXT.get(name, name))
    x = event.widget.winfo_rootx() + event.widget.winfo_width() + 8
    y = event.widget.winfo_rooty()
    tooltip.geometry(f"+{x}+{y}")
    tooltip.deiconify()
    tooltip.lift()

def hide_tooltip(_event):
    tooltip.withdraw()


# ── Input bar ─────────────────────────────────────────────────

input_bar = tk.Frame(window, bg="#0d1f0d", pady=4)
input_bar.pack(fill="x", padx=10)
tk.Label(input_bar, text="INPUTS:", bg="#0d1f0d", fg=LABEL_CLR,
         font=("Courier", 8, "bold")).pack(side="left", padx=(6, 10))
input_btn_frame = tk.Frame(input_bar, bg="#0d1f0d")
input_btn_frame.pack(side="left", fill="x", expand=True)

def update_input_bar():
    for w in input_btn_frame.winfo_children():
        w.destroy()
    # Collect contact variables
    cvars = {e["variable"]
             for rung in rungs for col in rung
             for e in col["branches"]
             if e["type"] == "Contact" and e.get("variable")}
    if not cvars:
        tk.Label(input_btn_frame,
                 text="Assign variables to contacts to see inputs here.",
                 bg="#0d1f0d", fg="#444d56", font=("Courier", 8)).pack(side="left")
        return
    for var in sorted(cvars):
        on = input_states.get(var, False)
        b  = tk.Button(input_btn_frame,
                       text=f"{var}  {'ON' if on else 'OFF'}",
                       bg="#00ff88" if on else "#1a1a1a",
                       fg=BG if on else "#444d56",
                       activebackground="#00cc66", activeforeground=BG,
                       relief="flat", font=("Courier", 8, "bold"),
                       padx=8, pady=3, cursor="hand2")
        b.pack(side="left", padx=3)
        def _toggle(v=var, btn=b):
            input_states[v] = not input_states.get(v, False)
            if sim_running: evaluate_ladder()
            update_input_bar()
        b.config(command=_toggle)

# ── Left palette ──────────────────────────────────────────────

palette = tk.Frame(window, bg=BTN_BG, width=110)
palette.pack(side="left", fill="y", padx=(10, 0), pady=(0, 10))
palette.pack_propagate(False)
tk.Label(palette, text="INSERT", bg=BTN_BG, fg=LABEL_CLR,
         font=("Courier", 8, "bold")).pack(pady=(10, 6))
tk.Frame(palette, bg="#30363d", height=1).pack(fill="x", padx=8, pady=(0, 8))

def add_symbol(sym_name):
    rungs[active_rung].append(new_col(new_entry(sym_name)))
    refresh()

for _sym in SYMBOLS:
    _abbr, _fn = SYMBOLS[_sym]
    _bf = tk.Frame(palette, bg=BTN_BG)
    _bf.pack(fill="x", padx=6, pady=3)
    _mc = tk.Canvas(_bf, width=90, height=44, bg=BTN_BG,
                    highlightthickness=1, highlightbackground="#30363d",
                    cursor="hand2")
    _mc.pack()
    (draw_no if _sym == "Contact" else _fn)(_mc, 45, 26)
    for item in _mc.find_all():
        if _mc.type(item) == "text":
            _mc.itemconfig(item, font=("Courier", 6))
    _mc.bind("<ButtonPress-1>",  lambda e, n=_sym: on_sym_drag_start(e, n))
    _mc.bind("<Enter>",          lambda e, n=_sym: show_tooltip(e, n))
    _mc.bind("<Leave>",          hide_tooltip)
    _lbl = tk.Label(_bf, text="CONTACT" if _sym == "Contact" else _abbr,
                    bg=BTN_BG, fg=LABEL_CLR, font=("Courier", 7), cursor="fleur")
    _lbl.pack()
    _lbl.bind("<ButtonPress-1>", lambda e, n=_sym: on_sym_drag_start(e, n))
    _lbl.bind("<Enter>",         lambda e, n=_sym: show_tooltip(e, n))
    _lbl.bind("<Leave>",         hide_tooltip)

# ── Canvas ────────────────────────────────────────────────────

_frame = tk.Frame(window, bg=BG)
_frame.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=(0, 10))
canvas = tk.Canvas(_frame, bg=BG, highlightthickness=0)
_sb    = tk.Scrollbar(_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=_sb.set)
_sb.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
window.bind_all("<MouseWheel>",
    lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))


def select_rung(idx):
    global active_rung
    active_rung = idx
    redraw()

# ── Drag state ────────────────────────────────────────────────
# Unified dict for all drag operations

drag = {
    "kind":    None,   # "palette" | "rung"
    "sym":     None,   # palette sym name
    "entry":   None,   # rung entry being dragged
    "ri": None, "ci": None, "bi": None,
    "label":   None,
}

def _start_float_label(event, text, bg, fg):
    lbl = tk.Label(window, text=text, bg=bg, fg=fg,
                   font=("Courier", 8, "bold"), padx=6, pady=3, relief="flat")
    lbl.place(x=event.x_root - window.winfo_rootx() + 8,
              y=event.y_root - window.winfo_rooty() + 8)
    drag["label"] = lbl

def _move_float_label(event):
    if drag["label"]:
        drag["label"].place(x=event.x_root - window.winfo_rootx() + 8,
                            y=event.y_root - window.winfo_rooty() + 8)

def _end_float_label():
    if drag["label"]:
        drag["label"].destroy()
        drag["label"] = None

def _canvas_xy(event):
    """Convert root coords to canvas scroll-adjusted coords."""
    return (event.x_root - canvas.winfo_rootx() + canvas.canvasx(0),
            event.y_root - canvas.winfo_rooty() + canvas.canvasy(0))

def _over(event, widget):
    wx, wy = widget.winfo_rootx(), widget.winfo_rooty()
    return wx <= event.x_root <= wx+widget.winfo_width() \
       and wy <= event.y_root <= wy+widget.winfo_height()

def _set_panel_highlight(active):
    col    = "#3a0000" if active else BTN_BG
    border = "#ff4444" if active else BTN_BG
    for panel in (palette, var_panel):
        panel.config(bg=col, highlightbackground=border,
                     highlightthickness=2 if active else 0)
        for w in panel.winfo_children():
            try: w.config(bg=col)
            except: pass

def _find_drop_target(mx, my):
    """Return (rung_idx, insert_col_idx) for a canvas position, or None."""
    cw = canvas.winfo_width()
    y  = 40
    for i, rung in enumerate(rungs):
        rh = rung_height(rung)
        if y <= my <= y + rh and RUNG_PAD <= mx <= cw - RUNG_PAD:
            slot_w, start = rung_layout(rung if rung else [None], cw)
            insert = len(rung)
            for j in range(len(rung)):
                if mx < start + j * slot_w + slot_w // 2:
                    insert = j
                    break
            return i, insert
        y += rh
    return None

# Palette drag
def on_sym_drag_start(event, sym_name):
    drag["kind"] = "palette"
    drag["sym"]  = sym_name
    _start_float_label(event, SYMBOLS[sym_name][0], RAIL_CLR, BG)
    window.bind("<B1-Motion>",       _on_drag_motion)
    window.bind("<ButtonRelease-1>", _on_palette_drag_release)

def _on_drag_motion(event):
    _move_float_label(event)

def _on_palette_drag_release(event):
    _end_float_label()
    window.unbind("<B1-Motion>")
    window.unbind("<ButtonRelease-1>")
    sym_name = drag["sym"]; drag["sym"] = None
    if not sym_name: return
    mx, my = _canvas_xy(event)
    target = _find_drop_target(mx, my)
    if target:
        global active_rung
        ri, ci = target
        active_rung = ri
        rungs[ri].insert(ci, new_col(new_entry(sym_name)))
        refresh()

DRAG_THRESH = 6
_press = {
    "x": 0,
    "y": 0,
    "ri": None,
    "ci": None,
    "bi": None,
    "dragging": False
}


def _on_drag_motion(event):
    _move_float_label(event)


    _set_panel_highlight(_over(event, palette) or _over(event, var_panel))

def _on_rung_drag_release(event):
    window.unbind("<B1-Motion>")
    window.unbind("<ButtonRelease-1>")

    _end_float_label()
    _set_panel_highlight(False)

    ri, ci, bi = drag["ri"], drag["ci"], drag["bi"]

    if ri is None:
        return
    if _over(event, palette) or _over(event, var_panel):
        branches = rungs[ri][ci]["branches"]
        if len(branches) > 1:
            branches.pop(bi)
        else:
            rungs[ri].pop(ci)

    else:
        mx, my = _canvas_xy(event)
        target = _find_drop_target(mx, my)

        if target:
            t_ri, t_ci = target
            entry = rungs[ri][ci]["branches"][bi]

            # remove from source
            if len(rungs[ri][ci]["branches"]) > 1:
                rungs[ri][ci]["branches"].pop(bi)
            else:
                rungs[ri].pop(ci)
                if t_ri == ri and t_ci > ci:
                    t_ci -= 1

            rungs[t_ri].insert(t_ci, new_col(entry))

    drag.update(kind=None, ri=None, ci=None, bi=None, entry=None)
    refresh()

# Variable drag
def on_var_drag_start(event, var_name):
    drag["kind"] = "var"
    drag["sym"]  = var_name
    _start_float_label(event, var_name, BTN_ACT, BG)
    window.bind("<B1-Motion>",       _on_drag_motion)
    window.bind("<ButtonRelease-1>", _on_var_drag_release)

def _on_var_drag_release(event):
    _end_float_label()
    window.unbind("<B1-Motion>")
    window.unbind("<ButtonRelease-1>")
    var_name = drag["sym"]; drag["sym"] = None
    if not var_name: return
    mx, my = _canvas_xy(event)
    cw     = canvas.winfo_width()
    y      = 40
    for i, rung in enumerate(rungs):
        rh     = rung_height(rung)
        cy     = y + rh // 2
        slot_w, start = rung_layout(rung, cw) if rung else (COL_W, RUNG_PAD)
        for j, col in enumerate(rung):
            sx  = start + j * slot_w + slot_w // 2
            bys = branch_ys(cy, len(col["branches"]))
            for b, by in enumerate(bys):
                if abs(mx - sx) <= slot_w//2 and abs(my - by) <= 42:
                    col["branches"][b]["variable"] = var_name
                    refresh()
                    return
        y += rh

# ── Coordinate-based hit detection ───────────────────────────

def _locate_symbol(mx, my):
    """Return (ri, ci, bi) or None from mouse coordinates."""
    cw = canvas.winfo_width()
    y = 40

    for i, rung in enumerate(rungs):
        rh = rung_height(rung)
        cy = y + rh // 2

        if y <= my <= y + rh:
            if not rung:
                return None

            slot_w, start = rung_layout(rung, cw)

            for j, col in enumerate(rung):
                sx = start + j * slot_w + slot_w // 2

                # Check horizontal bounds - must be within column
                if abs(mx - sx) > slot_w // 2:
                    continue

                bys_ = branch_ys(cy, len(col["branches"]))

                for b, by in enumerate(bys_):
                    # Check vertical bounds with a tighter hit area
                    if abs(my - by) <= BRANCH_H // 2:
                        return i, j, b

        y += rh

    return None

# ── Canvas Event Handlers ───────────────────────────

def _force_unfocus(event):
    # Don't process events during startup
    if not window.winfo_viewable():
        return
    current = window.focus_get()
    if isinstance(current, tk.Entry) and event.widget is not current:
        try:
            current.event_generate("<FocusOut>")
        except tk.TclError:
            pass  # Widget might have been destroyed


def _canvas_press(event):
    mx = canvas.canvasx(event.x)
    my = canvas.canvasy(event.y)

    # First check if we're clicking on a symbol
    res = _locate_symbol(mx, my)
    if res:
        ri, ci, bi = res
        _press.update(
            x=event.x_root,
            y=event.y_root,
            ri=ri, ci=ci, bi=bi,
            dragging=False
        )
        return
    
    # If not on a symbol, check if we're clicking on a rung (for rung selection)
    cw = canvas.winfo_width()
    y = 40
    for i, rung in enumerate(rungs):
        rh = rung_height(rung)
        if y <= my <= y + rh and RUNG_PAD <= mx <= cw - RUNG_PAD:
            # Clicked on a rung - select it
            select_rung(i)
            return
        y += rh

def _canvas_motion(event):
    if _press["ri"] is None:
        return

    dx = abs(event.x_root - _press["x"])
    dy = abs(event.y_root - _press["y"])

    if not _press["dragging"] and (dx > DRAG_THRESH or dy > DRAG_THRESH):
  
        _press["dragging"] = True

        ri, ci, bi = _press["ri"], _press["ci"], _press["bi"]
        entry = rungs[ri][ci]["branches"][bi]

        drag["kind"]  = "rung"
        drag["entry"] = entry
        drag["ri"], drag["ci"], drag["bi"] = ri, ci, bi

        abbr, _ = SYMBOLS.get(entry["type"], ("?", None))

        _start_float_label(event, abbr, "#ff4444", "white")

        window.bind("<B1-Motion>", _on_drag_motion)
        window.bind("<ButtonRelease-1>", _on_rung_drag_release)

def _canvas_release(event):
    if _press["ri"] is None:
        return

    if not _press["dragging"]:
        # ✅ This is a CLICK
        ri, ci, bi = _press["ri"], _press["ci"], _press["bi"]

        _select_col(ri, ci)
        on_contact_click(event, ri, ci, bi)

    _press.update(ri=None, ci=None, bi=None, dragging=False)

def _canvas_hover(event):
    mx = canvas.canvasx(event.x)
    my = canvas.canvasy(event.y)

    res = _locate_symbol(mx, my)

    if res:
        canvas.config(cursor="hand2")   # interactive
    else:
        canvas.config(cursor="arrow")   # default

canvas.bind("<ButtonPress-1>", _canvas_press)
canvas.bind("<B1-Motion>", _canvas_motion)
canvas.bind("<ButtonRelease-1>", _canvas_release)
canvas.bind("<Motion>", _canvas_hover)



# ── Logic evaluator ───────────────────────────────────────────

def eval_entry(entry, power_in):
    """Return (passes, self_lit). Also writes output coil states."""
    import time
    sym   = entry["type"]
    var   = entry.get("variable")
    ctype = entry.get("contact_type", "NO")

    if sym == "Contact":
        sig = input_states.get(var, False) if var else False
        if   ctype == "NO": lit = sig;       passes = power_in and sig
        elif ctype == "NC": lit = not sig;   passes = power_in and not sig
        else:               lit = sig if ctype == "P" else not sig
        passes = power_in and lit if ctype in ("P","N") else passes
        return passes, lit

    if sym in ("Output Coil", "Negated Output"):
        val = power_in if sym == "Output Coil" else not power_in
        if var:
            output_states[var] = val
            input_states[var]  = val
        return power_in, power_in

    if sym == "Timer (TON)":
        preset_ms = 1000  # default
        if var and var in variable_registry:
            info = variable_registry[var]
            if info["type"] == "int":
                preset_ms = max(1, info["value"])
        ts = timer_state.setdefault(var or id(entry),
                                    {"running": False, "start": 0.0, "done": False})
        if power_in:
            if not ts["running"]:
                ts["running"] = True
                ts["start"]   = time.monotonic()
                ts["done"]    = False
            elapsed_ms = (time.monotonic() - ts["start"]) * 1000
            if elapsed_ms >= preset_ms:
                ts["done"] = True
        else:
            ts["running"] = False
            ts["done"]    = False
        done = ts["done"]
        return (power_in and done), done

    return power_in, power_in

def evaluate_ladder():
    global output_states
    output_states = {}
    for rung in rungs:
        power = True
        for col in rung:
            power = power and any(
                eval_entry(e, power)[0] for e in col["branches"])
    redraw()

# ── Rendering ─────────────────────────────────────────────────

def _draw_entry(c, entry, sx, sy, s_col, w_col):
    """Draw a symbol with overridden colours."""
    global SYM_CLR, WIRE_CLR
    SYM_CLR, WIRE_CLR = s_col, w_col
    fn = CONTACT_DRAW.get(entry.get("contact_type","NO"), draw_no) \
         if entry["type"] == "Contact" \
         else SYMBOLS.get(entry["type"], (None, lambda *a: None))[1]
    fn(c, sx, sy)
    SYM_CLR  = RAIL_CLR
    WIRE_CLR = RAIL_CLR

def wclr(powered):
    if not sim_running:
        return "#2a2a2a"  # Dark grey when stopped
    return "#00ff88" if powered else "#2a2a2a"

def sclr(powered):
    if not sim_running:
        return "#444444"  # Medium grey when stopped
    return "#00ff88" if powered else "#555555"

def _select_col(ri, ci):
    global selected_col, active_rung
    active_rung = ri
    if selected_col == (ri, ci):
        selected_col = None   # click again to deselect
    else:
        selected_col = (ri, ci)
    redraw()


def redraw(*_):
    canvas.delete("all")
    cw = canvas.winfo_width() or 900
    total_h = 80 + sum(rung_height(r) for r in rungs)
    canvas.configure(scrollregion=(0, 0, cw, max(total_h, 300)))
    
    rail_l, rail_r = RUNG_PAD, cw - RUNG_PAD
    y = 40
    for i, rung in enumerate(rungs):
        rh = rung_height(rung)
        cy = y + rh // 2
        is_active = (i == active_rung)

        # Rails
        canvas.create_line(rail_l, y, rail_l, y+rh, fill=RAIL_CLR, width=4)
        # Right rail goes grey when stopped
        right_rail_color = RAIL_CLR if sim_running else "#2a2a2a"
        canvas.create_line(rail_r, y, rail_r, y+rh, fill=right_rail_color, width=4)

        # Rung number (clickable to select)
        canvas.create_text(rail_l-16, cy, text=str(i+1),
                           fill=RAIL_CLR if is_active else LABEL_CLR,
                           font=("Courier", 8, "bold" if is_active else "normal"),
                           anchor="e")

        if not rung:
            empty_color = WIRE_CLR if sim_running else "#2a2a2a"
            canvas.create_line(rail_l, cy, rail_r, cy,
                               fill=empty_color, width=2, dash=(6,4))
            y += rh; continue
    

        # Per-column power + lit state
        col_power, entry_lit = [], []
        p = True
        for col in rung:
            col_power.append(p)
            lit_row, col_ok = [], False
            for e in col["branches"]:
                passes, lit = eval_entry(e, p) if sim_running else (False, False)
                lit_row.append(lit)
                col_ok = col_ok or passes
            entry_lit.append(lit_row)
            p = p and col_ok
        final_power = p

        slot_w, start = rung_layout(rung, cw)

        # Wire: left rail → first symbol
        fh = sym_half(rung[0]["branches"][0]["type"])
        canvas.create_line(rail_l, cy, start + slot_w//2 - fh, cy,
                           fill=wclr(True), width=2)

        for j, col in enumerate(rung):
            branches = col["branches"]
            n_b  = len(branches)
            sx   = start + j * slot_w + slot_w // 2
            sh   = sym_half(branches[0]["type"])
            bys_ = branch_ys(cy, n_b)

            if n_b > 1:
                # Right join is green only if any branch passes (OR result)
                any_passes = any(
                    eval_entry(e, col_power[j])[0]
                    for e in branches) if sim_running else False
                canvas.create_line(sx-sh, bys_[0], sx-sh, bys_[-1],
                                   fill=wclr(col_power[j]), width=2)
                canvas.create_line(sx+sh, bys_[0], sx+sh, bys_[-1],
                                   fill=wclr(any_passes), width=2)
                canvas.create_line(sx-slot_w//2, cy, sx-sh, cy,
                                   fill=wclr(col_power[j]), width=2)

            for b, (entry, by) in enumerate(zip(branches, bys_)):
                lit = entry_lit[j][b] if entry_lit else False
                _draw_entry(canvas, entry, sx, by, sclr(lit), sclr(col_power[j]))
                lc  = "#00ff88" if (sim_running and lit) else \
                      "#555555" if sim_running else "#444444"
                canvas.create_text(sx, by-(48 if n_b>1 else 36),
                                   text=entry.get("variable") or "?",
                                   fill=lc, font=("Courier", 7 if n_b>1 else 8, "bold"))

            # Selected column highlight
            if selected_col == (i, j):
                canvas.create_rectangle(
                    sx - slot_w//2 + 2, y + 4,
                    sx + slot_w//2 - 2, y + rh - 4,
                    outline="#00aaff", width=1, dash=(4, 3))

            # Inter-column wire
            seg_s = sx + sh
            if j < len(rung)-1:
                nh    = sym_half(rung[j+1]["branches"][0]["type"])
                seg_e = start + (j+1)*slot_w + slot_w//2 - nh
                canvas.create_line(seg_s, cy, seg_e, cy,
                                   fill=wclr(col_power[j]), width=2)
            else:
                canvas.create_line(seg_s, cy, rail_r, cy,
                                   fill=wclr(final_power), width=2)

            # Column index label (shows when selected)
            if selected_col == (i, j):
                canvas.create_text(sx, y + rh - 10, text="selected",
                                   fill="#00aaff", font=("Courier", 6))  
                

        y += rh

def add_branch_to_selected():
    if selected_col is not None:
        ri, ci = selected_col
        _add_branch(ri, ci)
        redraw()
    else:
        # Flash the button to indicate nothing is selected
        branch_btn.config(bg="#ff4444", fg="white")
        window.after(400, lambda: branch_btn.config(bg=BTN_BG, fg=TEXT_CLR))

def _add_branch(ri, ci):
    branches = rungs[ri][ci]["branches"]
    bi = len(branches)
    # Get the first branch's entry
    first_entry = branches[0]
    
    # Create a new entry based on the first branch's type
    if first_entry["type"] == "Contact":
        new_entry_data = {
            "type": "Contact",
            "contact_type": first_entry.get("contact_type", "NO"),
            "variable": None  # New branch gets no variable assigned
        }
    else:
        # For other symbol types, copy the type but not the variable
        new_entry_data = {
            "type": first_entry["type"],
            "variable": None
        }
    
    branches.append(new_entry_data)
    branch_undo_stack.append((ri, ci, bi))
    redraw()

branch_btn.config(command=add_branch_to_selected)

# ── Contact type menu (left-click on contact) ─────────────────

def on_contact_click(event, ri, ci, bi):
    entry = rungs[ri][ci]["branches"][bi]
    if entry["type"] != "Contact":
        return
    menu = tk.Menu(window, tearoff=0, bg=BTN_BG, fg=TEXT_CLR,
                   activebackground=BTN_ACT, activeforeground=BG,
                   font=("Courier", 9))
    cur = tk.StringVar(value=entry.get("contact_type","NO"))
    for label, val in [("Normally Open (NO)","NO"),("Normally Closed (NC)","NC"),
                       ("Positive Edge (P)","P"),("Negative Edge (N)","N")]:
        menu.add_radiobutton(label=label, variable=cur, value=val,
                             command=lambda v=val: _set_contact_type(ri,ci,bi,v))
    try:    menu.tk_popup(event.x_root, event.y_root)
    finally:menu.grab_release()

def _set_contact_type(ri, ci, bi, t):
    rungs[ri][ci]["branches"][bi]["contact_type"] = t
    evaluate_ladder() if sim_running else redraw()

# ── Variable panel ────────────────────────────────────────────

var_panel = tk.Frame(window, bg=BTN_BG, width=130)
var_panel.pack(side="right", fill="y", padx=(0,10), pady=(0,10))
var_panel.pack_propagate(False)
tk.Label(var_panel, text="VARIABLES", bg=BTN_BG, fg=LABEL_CLR,
         font=("Courier", 8, "bold")).pack(pady=(10,4))
tk.Frame(var_panel, bg="#30363d", height=1).pack(fill="x", padx=8, pady=(0,8))

_new_var_frame = tk.Frame(var_panel, bg=BTN_BG)
_new_var_frame.pack(fill="x", padx=8, pady=(0,8))

def add_variable(vtype="bool"):
    var_counter[0] += 1
    v = f"VAR{var_counter[0]:03d}"
    variable_registry[v] = {"type": vtype, "value": False if vtype == "bool" else 0}
    update_variable_panel()

tk.Button(_new_var_frame, text="+ New Variable", command=add_variable,
          bg="#238636", fg=TEXT_CLR, activebackground="#2ea043",
          activeforeground=TEXT_CLR, relief="flat",
          font=("Courier", 8, "bold"), padx=8, pady=4,
          cursor="hand2").pack(fill="x")

_var_list = tk.Frame(var_panel, bg=BTN_BG)
_var_list.pack(fill="both", expand=True)

def delete_variable(var_name):
    variable_registry.pop(var_name, None)
    for rung in rungs:
        for col in rung:
            for e in col["branches"]:
                if e.get("variable") == var_name:
                    e["variable"] = None
    refresh()

def _make_delete_btn(parent, var):
    """Small × canvas button that goes red on hover."""
    c = tk.Canvas(parent, width=16, height=16, bg=BTN_BG,
                  highlightthickness=0, cursor="hand2")
    def _draw(col):
        c.delete("all")
        c.create_line(4,4,12,12, fill=col, width=2)
        c.create_line(12,4,4,12, fill=col, width=2)
    _draw("#444d56")
    c.bind("<Enter>",    lambda e: _draw("#ff4444"))
    c.bind("<Leave>",    lambda e: _draw("#444d56"))
    c.bind("<Button-1>", lambda e: delete_variable(var))
    return c

def update_variable_panel():
    for w in _var_list.winfo_children():
        w.destroy()
    if not variable_registry:
        tk.Label(_var_list, text="No variables\ndefined yet",
                 bg=BTN_BG, fg="#444d56",
                 font=("Courier", 8), justify="center").pack(pady=20)
        return
    for var in list(variable_registry.keys()):
        info = variable_registry[var]
        vtype = info["type"]

        # Container for this variable's rows
        card = tk.Frame(_var_list, bg="#1e2430",
                        highlightbackground="#30363d", highlightthickness=1)
        card.pack(fill="x", padx=6, pady=3)

        # ── Row 1: name + type toggle + delete ───────────────
        row1 = tk.Frame(card, bg="#1e2430")
        row1.pack(fill="x", padx=4, pady=(4,1))

        lbl = tk.Label(row1, text=var, bg="#1e2430", fg=RAIL_CLR,
                       font=("Courier", 8, "bold"), anchor="w", cursor="fleur")
        lbl.pack(side="left", fill="x", expand=True)
        lbl.bind("<ButtonPress-1>", lambda e, v=var: on_var_drag_start(e, v))

        _make_delete_btn(row1, var).pack(side="right", padx=(4,0))

        # ── Row 2: type toggle buttons ────────────────────────
        row2 = tk.Frame(card, bg="#1e2430")
        row2.pack(fill="x", padx=4, pady=(1,2))

        for t, label in [("bool","BOOL"), ("int","INT")]:
            active = (vtype == t)
            tb = tk.Button(row2, text=label,
                           bg=RAIL_CLR if active else "#2a2a2a",
                           fg=BG if active else "#555555",
                           activebackground=RAIL_CLR, activeforeground=BG,
                           relief="flat", font=("Courier", 7, "bold"),
                           padx=6, pady=1, cursor="hand2")
            tb.pack(side="left", padx=(0,2))
            def _set_type(v=var, t=t, b=tb):
                old = variable_registry[v]["type"]
                if old == t: return
                variable_registry[v]["type"]  = t
                variable_registry[v]["value"] = False if t == "bool" else 0
                update_variable_panel()
            tb.config(command=_set_type)

        # ── Row 3: integer value editor (INT only) ────────────
        if vtype == "int":
            row3 = tk.Frame(card, bg="#1e2430")
            row3.pack(fill="x", padx=4, pady=(0,4))
            tk.Label(row3, text="ms:", bg="#1e2430", fg=LABEL_CLR,
                     font=("Courier", 7)).pack(side="left")
            val_var = tk.StringVar(value=str(info["value"]))
            entry_w = tk.Entry(row3, textvariable=val_var, width=6,
                               bg="#0d1117", fg=TEXT_CLR, insertbackground=TEXT_CLR,
                               relief="flat", font=("Courier", 8),
                               highlightbackground="#30363d", highlightthickness=1)
            entry_w.pack(side="left", padx=(2,0))
            
            def _save_int(event=None, v=var, sv=val_var, entry_widget=entry_w):
                text = sv.get().strip()

                if event and event.keysym == "Escape":
                    sv.set(str(variable_registry[v]["value"]))
                    window.focus_set()
                    return

                try:
                    val = int(text)
                    val = max(0, val)

                    variable_registry[v]["value"] = val
                    sv.set(str(val))

                    entry_widget.config(bg="#1f3d2b")
                    window.after(150, lambda: entry_widget.config(bg="#0d1117"))

                    window.focus_set()

                    if sim_running:
                        evaluate_ladder()
                    else:
                        redraw()

                except ValueError:
                    entry_widget.config(bg="#5a1a1a")
                    window.after(300, lambda: entry_widget.config(bg="#0d1117"))

                    entry_widget.focus_set()


# ── Init ──────────────────────────────────────────────────────

update_variable_panel()

# Demo variables
for _n in ["OUT001","OUT002","OUT003"]:
    variable_registry[_n] = {"type": "bool", "value": False}
var_counter[0] = 3
update_variable_panel()

def _timer_tick():
    """Periodically re-evaluate so TON timers update live."""
    if sim_running:
        evaluate_ladder()
    window.after(100, _timer_tick)

_timer_tick()

def _deselect(event=None):
    global selected_col
    selected_col = None
    redraw()

window.bind("<Escape>", _deselect)

canvas.bind("<Configure>", redraw)
canvas.bind("<Button-1>", _force_unfocus, add="+")
palette.bind("<Button-1>", _force_unfocus, add="+")
var_panel.bind("<Button-1>", _force_unfocus, add="+")

# Give focus to the main window and bring it to front
window.lift()
window.focus_force()
window.attributes('-topmost', True)
window.after(100, lambda: window.attributes('-topmost', False))

redraw()
window.mainloop()