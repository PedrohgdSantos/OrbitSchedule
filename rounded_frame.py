import tkinter as tk

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, bg_color="#111827", border_color="#1F2937", corner_radius=16, padding=12, **kwargs):
        parent_bg = None
        try:
            parent_bg = parent.cget("bg")
        except Exception:
            try:
                parent_bg = parent.cget("background")
            except Exception:
                parent_bg = "#050608"

        super().__init__(parent, bg=parent_bg, highlightthickness=0, bd=0, **kwargs)
        self.bg_color = bg_color
        self.border_color = border_color
        self.corner_radius = corner_radius
        self.padding = padding
        self.inner_frame = tk.Frame(self, bg=bg_color)
        self.window_id = self.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.bind("<Configure>", self._resize)

    def _resize(self, event):
        width = max(event.width, 1)
        height = max(event.height, 1)
        self._draw(width, height)

    def _draw(self, width, height):
        self.coords(self.window_id, self.padding / 2, self.padding / 2)
        self.itemconfig(self.window_id, width=max(0, width - self.padding), height=max(0, height - self.padding))
        self.delete("background")
        self._create_rounded_rect(0, 0, width, height, self.corner_radius, fill=self.bg_color, outline=self.border_color, tags=("background",))

    def set_border_color(self, color):
        """Atualiza a cor da borda do quadro arredondado e redesenha."""
        self.border_color = color
        self._draw(self.winfo_width(), self.winfo_height())

    def _create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        if radius > (x2 - x1) / 2:
            radius = (x2 - x1) / 2
        if radius > (y2 - y1) / 2:
            radius = (y2 - y1) / 2

        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, splinesteps=36, **kwargs)
