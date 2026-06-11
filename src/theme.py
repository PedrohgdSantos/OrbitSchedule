"""
OrbitSchedule theme manager.

Provides two palettes (LIGHT / DARK) and a ThemeManager that:
  1. Builds a color remap table (old hex → new hex) before toggling.
  2. Patches all UI module-level color constants in-place so new widgets
     created after the switch automatically use the right colors.
  3. Walks every existing tk widget and updates its color attributes.
  4. Re-applies TTK styles (Treeview, Combobox, Scrollbar, etc.).
"""
import sys
import tkinter as tk
from tkinter import ttk
from typing import Dict

# ── Palettes ───────────────────────────────────────────────────────────────────

LIGHT: Dict[str, str] = {
    "BG_PAGE":    "#F5F6FA",
    "BG_SIDEBAR": "#FFFFFF",
    "BG_CARD":    "#FFFFFF",
    "TEXT_DARK":  "#111827",
    "TEXT_MID":   "#6B7280",
    "TEXT_LIGHT": "#9CA3AF",
    "BORDER":     "#E5E7EB",
    "ORANGE":     "#F97316",
    "ORANGE_DIM": "#FFF7ED",
    "GREEN":      "#16A34A",
    "GREEN_BG":   "#DCFCE7",
    "BLUE":       "#2563EB",
    "BLUE_BG":    "#DBEAFE",
    "RED":        "#DC2626",
    "RED_BG":     "#FEE2E2",
    "AMBER":      "#D97706",
    "AMBER_BG":   "#FEF3C7",
    "ROW_EVEN":   "#FAFAFA",
    "ROW_ODD":    "#FFFFFF",
}

DARK: Dict[str, str] = {
    "BG_PAGE":    "#18191C",
    "BG_SIDEBAR": "#1E1F23",
    "BG_CARD":    "#25262B",
    "TEXT_DARK":  "#F1F3F5",
    "TEXT_MID":   "#ADB5BD",
    "TEXT_LIGHT": "#6B7280",
    "BORDER":     "#373A40",
    "ORANGE":     "#F97316",
    "ORANGE_DIM": "#4A2E0D",   # mais saturado — visível no dark
    "GREEN":      "#22C55E",
    "GREEN_BG":   "#1A3D28",   # verde escuro com cor suficiente
    "BLUE":       "#3B82F6",
    "BLUE_BG":    "#1D3461",   # azul escuro saturado
    "RED":        "#EF4444",
    "RED_BG":     "#3D1515",   # vermelho escuro com cor
    "AMBER":      "#F59E0B",
    "AMBER_BG":   "#3D2C0A",   # âmbar escuro com cor
    "ROW_EVEN":   "#2C2D32",
    "ROW_ODD":    "#25262B",
}

# Widget color attributes that can be recolored.
_RECOLOR_ATTRS = (
    "bg", "fg",
    "activebackground", "activeforeground",
    "highlightbackground", "highlightcolor",
    "insertbackground",
    "selectbackground", "selectforeground",
    "troughcolor", "disabledforeground",
)

# Module suffixes whose global color constants will be patched on theme change,
# so that widgets created AFTER the toggle also use the correct palette.
_PATCH_SUFFIXES = (
    ".app", ".absence_manager", ".professor_manager",
    ".turma_manager", ".sala_manager", ".charts",
)


class _ThemeManager:
    def __init__(self):
        self._mode: str = "light"

    # ── Public API ─────────────────────────────────────────────────────────────

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def is_dark(self) -> bool:
        return self._mode == "dark"

    def current(self) -> Dict[str, str]:
        return DARK if self._mode == "dark" else LIGHT

    def build_remap(self) -> Dict[str, str]:
        """
        Return {old_hex_lower: new_hex} for the NEXT mode (call before toggle).
        Only includes colors that actually differ between palettes.
        """
        from_pal = LIGHT if self._mode == "light" else DARK
        to_pal   = DARK  if self._mode == "light" else LIGHT
        remap: Dict[str, str] = {}
        for key in from_pal:
            old = from_pal[key].lower()
            new = to_pal[key]
            if old != new.lower():
                remap[old] = new
        return remap

    def toggle(self):
        self._mode = "dark" if self._mode == "light" else "light"

    def apply(self, root: tk.Misc, style: ttk.Style, remap: Dict[str, str]):
        """Full theme application: patch globals + recolor widgets + TTK styles."""
        self._patch_module_globals(remap)
        self._recolor_tree(root, remap)
        self._apply_ttk(style)

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _patch_module_globals(self, remap: Dict[str, str]):
        """
        Update color constants in every loaded UI module so that new widgets
        (e.g., a professor added after the theme switch) use the new palette.
        """
        for mod_name, mod in list(sys.modules.items()):
            if mod is None:
                continue
            if not any(mod_name.endswith(s) for s in _PATCH_SUFFIXES):
                continue
            for attr in list(vars(mod)):
                val = getattr(mod, attr, None)
                if isinstance(val, str) and val.lower() in remap:
                    try:
                        setattr(mod, attr, remap[val.lower()])
                    except (AttributeError, TypeError):
                        pass

    def _recolor_tree(self, widget: tk.Misc, remap: Dict[str, str]):
        """Recursively walk all widgets and remap their color attributes."""
        for attr in _RECOLOR_ATTRS:
            try:
                cur = widget.cget(attr)
                if isinstance(cur, str) and cur.lower() in remap:
                    widget.config(**{attr: remap[cur.lower()]})
            except (tk.TclError, AttributeError, TypeError):
                pass
        for child in widget.winfo_children():
            self._recolor_tree(child, remap)

    def _apply_ttk(self, style: ttk.Style):
        """Re-apply all TTK style rules using the current palette."""
        p = self.current()
        f = "Segoe UI"
        style.configure(".",
            background=p["BG_PAGE"], foreground=p["TEXT_DARK"], font=(f, 10))
        style.configure("TFrame",  background=p["BG_PAGE"])
        style.configure("TLabel",  background=p["BG_PAGE"], foreground=p["TEXT_DARK"])
        style.configure("TEntry",
            fieldbackground=p["BG_CARD"], background=p["BG_CARD"],
            foreground=p["TEXT_DARK"], insertcolor=p["TEXT_DARK"],
            padding=8, relief="flat", borderwidth=1,
        )
        style.configure("TCombobox",
            fieldbackground=p["BG_CARD"], background=p["BG_CARD"],
            foreground=p["TEXT_DARK"], padding=8,
        )
        style.configure("Treeview",
            background=p["BG_CARD"], fieldbackground=p["BG_CARD"],
            foreground=p["TEXT_DARK"], rowheight=36,
            font=(f, 10), borderwidth=0,
        )
        style.configure("Treeview.Heading",
            background=p["BG_PAGE"], foreground=p["TEXT_MID"],
            font=(f, 9, "bold"), relief="flat", borderwidth=0,
        )
        style.map("Treeview",
            background=[("selected", p["ORANGE_DIM"])],
            foreground=[("selected", p["ORANGE"])],
        )
        style.configure("TSeparator", background=p["BORDER"])
        style.configure("TScrollbar",
            background=p["BORDER"], troughcolor=p["BG_PAGE"],
            borderwidth=0, arrowsize=12,
        )
        style.configure("TCheckbutton",
            background=p["BG_CARD"], foreground=p["TEXT_DARK"])


# Singleton — import and use this object everywhere.
Theme = _ThemeManager()
