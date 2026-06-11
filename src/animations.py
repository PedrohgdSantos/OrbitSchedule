"""
Animation utilities for OrbitSchedule.
All transitions use root.after() loops — no external dependencies.
"""
import tkinter as tk


# ── Color helpers ──────────────────────────────────────────────────────────────

def lerp_color(src: str, dst: str, t: float) -> str:
    """Linearly interpolate between two hex colors. t=0 → src, t=1 → dst."""
    def _parse(h: str):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    r1, g1, b1 = _parse(src)
    r2, g2, b2 = _parse(dst)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Page transition ────────────────────────────────────────────────────────────

def fade_page(root: tk.Tk, callback, steps: int = 10, delay_ms: int = 14):
    """
    Fade the root window to MIN_ALPHA, execute callback (page switch),
    then fade back to 1.0.  Total duration ≈ steps * delay_ms * 2 ms (~280 ms).
    """
    MIN_ALPHA = 0.55

    def _out(step: int):
        alpha = 1.0 - (1.0 - MIN_ALPHA) * step / steps
        try:
            root.attributes("-alpha", alpha)
        except tk.TclError:
            return
        if step < steps:
            root.after(delay_ms, lambda: _out(step + 1))
        else:
            callback()
            root.after(delay_ms, lambda: _in(0))

    def _in(step: int):
        alpha = MIN_ALPHA + (1.0 - MIN_ALPHA) * step / steps
        try:
            root.attributes("-alpha", alpha)
        except tk.TclError:
            return
        if step < steps:
            root.after(delay_ms, lambda: _in(step + 1))

    _out(0)


# ── Metric card count-up ───────────────────────────────────────────────────────

def count_up(label: tk.Label, target: int, root: tk.Misc, duration_ms: int = 650):
    """
    Animate a Label's text from its current numeric value to target.
    If the label already shows target, returns immediately.
    """
    try:
        start = int(str(label.cget("text")).strip())
    except (ValueError, tk.TclError):
        start = 0

    if start == target:
        return

    diff  = target - start
    steps = min(abs(diff), 22)
    delay = max(duration_ms // max(steps, 1), 18)

    def _tick(step: int):
        value = start + int(diff * step / steps)
        try:
            label.config(text=str(value))
        except tk.TclError:
            return
        if step < steps:
            root.after(delay, lambda: _tick(step + 1))
        else:
            try:
                label.config(text=str(target))
            except tk.TclError:
                pass

    _tick(1)


# ── Hover color animation ──────────────────────────────────────────────────────

def bind_hover(
    root: tk.Misc,
    widgets: list,
    normal_bg: str,
    hover_bg: str,
    steps: int = 6,
    delay_ms: int = 14,
    guard_fn=None,
):
    """
    Bind smooth bg-color <Enter>/<Leave> animation to all widgets in the list.

    guard_fn: optional callable() → bool. When it returns True, the animation
              is skipped (used to protect active nav items from being re-styled).
    """
    state = {"job": None, "current": normal_bg}

    def _cancel():
        if state["job"] is not None:
            try:
                root.after_cancel(state["job"])
            except Exception:
                pass
            state["job"] = None

    def _animate(target: str, step: int):
        _cancel()
        if guard_fn and guard_fn():
            return
        color = lerp_color(state["current"], target, step / steps)
        for w in widgets:
            try:
                w.config(bg=color)
            except tk.TclError:
                return
        if step < steps:
            state["job"] = root.after(delay_ms, lambda: _animate(target, step + 1))
        else:
            state["current"] = target

    def _enter(_e):
        if guard_fn and guard_fn():
            return
        _animate(hover_bg, 1)

    def _leave(_e):
        if guard_fn and guard_fn():
            return
        _animate(normal_bg, 1)

    for w in widgets:
        w.bind("<Enter>", _enter, add="+")
        w.bind("<Leave>", _leave, add="+")
