import tkinter as tk
from tkinter import font as tkfont
import math

class CircularCountdown:
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown Timer")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.70)
        self.root.configure(bg="#0d0d0d")
        self.root.resizable(True, True)

        self.total_seconds = 0
        self.remaining = 0
        self.running = False
        self.after_id = None

        self._drag_x = 0
        self._drag_y = 0

        self._resize_start_x = 0
        self._resize_start_y = 0
        self._resize_start_w = 0
        self._resize_start_h = 0
        self._resizing = False
        self.RESIZE_MARGIN = 14

        self.canvas_size = 280
        self.build_ui()
        self.center_window()

        self.root.bind("<ButtonPress-1>",   self._on_press)
        self.root.bind("<B1-Motion>",       self._on_motion)
        self.root.bind("<ButtonRelease-1>", self._on_release)

    def build_ui(self):
        self.topbar = tk.Frame(self.root, bg="#1a1a1a", height=28, cursor="fleur")
        self.topbar.pack(fill=tk.X, side=tk.TOP)
        self.topbar.pack_propagate(False)

        tk.Label(self.topbar, text="⏱  COUNTDOWN", bg="#1a1a1a",
                 fg="#888", font=("Courier", 9, "bold")).pack(side=tk.LEFT, padx=8)

        close_btn = tk.Button(self.topbar, text="✕", bg="#1a1a1a", fg="#ff5555",
                              font=("Courier", 10, "bold"), bd=0, cursor="hand2",
                              activebackground="#ff5555", activeforeground="white",
                              command=self.root.destroy)
        close_btn.pack(side=tk.RIGHT, padx=6)

        minimize_btn = tk.Button(self.topbar, text="—", bg="#1a1a1a", fg="#aaa",
                                 font=("Courier", 10, "bold"), bd=0, cursor="hand2",
                                 activebackground="#333", activeforeground="white",
                                 command=self.hide_app)
        minimize_btn.pack(side=tk.RIGHT, padx=2)

        self.canvas = tk.Canvas(self.root, width=self.canvas_size,
                                height=self.canvas_size, bg="#0d0d0d",
                                highlightthickness=0)
        self.canvas.pack(pady=(10, 4))

        # ── ONLY change from v1: zero-padded format ──
        self.time_var = tk.StringVar(value="00:00:00")
        self.time_label = tk.Label(self.root, textvariable=self.time_var,
                                   bg="#0d0d0d", fg="#ff8c00",
                                   font=("Courier", 22, "bold"))
        self.time_label.pack(pady=(0, 6))

        input_frame = tk.Frame(self.root, bg="#0d0d0d")
        input_frame.pack(pady=4)

        for label, attr, maxval in [("H", "h_var", 23), ("M", "m_var", 59), ("S", "s_var", 59)]:
            var = tk.StringVar(value="0")
            setattr(self, attr, var)
            tk.Label(input_frame, text=label, bg="#0d0d0d", fg="#888",
                     font=("Courier", 10)).pack(side=tk.LEFT)
            sp = tk.Spinbox(input_frame, textvariable=var,
                            from_=0, to=maxval, wrap=True,
                            width=3,
                            bg="#1e1e1e", fg="#ffffff",
                            insertbackground="white",
                            selectbackground="#ff8c00",
                            selectforeground="#000000",
                            buttonbackground="#2a2a2a",
                            font=("Courier", 12), bd=0,
                            highlightthickness=1,
                            highlightcolor="#ff8c00",
                            highlightbackground="#333",
                            justify="center")
            sp.pack(side=tk.LEFT, padx=2)
            # click → focus so keyboard works under overrideredirect
            sp.bind("<ButtonPress-1>", lambda e, w=sp: w.focus_force())

        btn_frame = tk.Frame(self.root, bg="#0d0d0d")
        btn_frame.pack(pady=(6, 12))

        self._make_btn(btn_frame, "START",  "#ff8c00", "#3a2000", self.start_timer).pack(side=tk.LEFT, padx=4)
        self._make_btn(btn_frame, "PAUSE",  "#ffaa00", "#3a2800", self.pause_timer).pack(side=tk.LEFT, padx=4)
        self._make_btn(btn_frame, "RESET",  "#ff4466", "#3a0011", self.reset_timer).pack(side=tk.LEFT, padx=4)

        self.grip = tk.Label(self.root, text="◢", bg="#0d0d0d", fg="#444",
                             font=("Courier", 14), cursor="sizing")
        self.grip.pack(anchor="se", padx=2, pady=0)

        self.draw_circle(1.0)

    def _make_btn(self, parent, text, fg, bg, cmd):
        return tk.Button(parent, text=text, bg=bg, fg=fg,
                         font=("Courier", 9, "bold"), bd=0, padx=10, pady=4,
                         cursor="hand2", activebackground=fg, activeforeground="#000",
                         command=cmd, relief="flat")

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def draw_circle(self, fraction):
        self.canvas.delete("all")
        cs = self.canvas_size
        pad = 20
        x0, y0, x1, y1 = pad, pad, cs - pad, cs - pad

        self.canvas.create_oval(x0, y0, x1, y1, outline="#1e1e1e", width=14)

        for i, alpha in [(16, "#301800"), (10, "#4a2800"), (4, "#603800")]:
            self.canvas.create_oval(x0-i//2, y0-i//2, x1+i//2, y1+i//2,
                                    outline=alpha, width=1)

        if fraction > 0:
            extent = -fraction * 360
            self.canvas.create_arc(x0, y0, x1, y1,
                                   start=90, extent=extent,
                                   outline="#ff8c00", width=12,
                                   style=tk.ARC)
            cx = (x0 + x1) / 2
            cy = (y0 + y1) / 2
            r  = (x1 - x0) / 2
            dx = cx + r * math.cos(math.radians(90 - fraction * 360))
            dy = cy - r * math.sin(math.radians(90 - fraction * 360))
            self.canvas.create_oval(dx-7, dy-7, dx+7, dy+7,
                                    fill="#ff8c00", outline="#ffffff", width=2)

        pct = int(fraction * 100)
        self.canvas.create_text(cs/2, cs/2 - 8, text=f"{pct}%",
                                fill="#ff8c00" if fraction > 0 else "#333",
                                font=("Courier", 18, "bold"))
        status = "RUNNING" if self.running else ("PAUSED" if self.remaining < self.total_seconds and self.remaining > 0 else "READY")
        if self.remaining == 0 and self.total_seconds > 0 and not self.running:
            status = "DONE ✓"
        self.canvas.create_text(cs/2, cs/2 + 18, text=status,
                                fill="#555", font=("Courier", 9))

    def update_time_label(self):
        h = self.remaining // 3600
        m = (self.remaining % 3600) // 60
        s = self.remaining % 60
        # ── ONLY change: zero-pad all parts ──
        self.time_var.set(f"{h:02d}:{m:02d}:{s:02d}")

    def start_timer(self):
        if self.running:
            return
        if self.remaining == 0:
            try:
                h = int(self.h_var.get() or 0)
                m = int(self.m_var.get() or 0)
                s = int(self.s_var.get() or 0)
            except ValueError:
                return
            self.total_seconds = h * 3600 + m * 60 + s
            if self.total_seconds <= 0:
                return
            self.remaining = self.total_seconds

        self.running = True
        self.tick()

    def pause_timer(self):
        self.running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.draw_circle(self.remaining / self.total_seconds if self.total_seconds else 0)

    def reset_timer(self):
        self.running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.remaining = 0
        self.total_seconds = 0
        self.time_var.set("00:00:00")
        self.draw_circle(1.0)

    def tick(self):
        if not self.running:
            return
        if self.remaining <= 0:
            self.running = False
            self.remaining = 0
            self.update_time_label()
            self.draw_circle(0.0)
            self._play_done()
            return

        self.update_time_label()
        fraction = self.remaining / self.total_seconds
        self.draw_circle(fraction)
        self.remaining -= 1
        self.after_id = self.root.after(1000, self.tick)

    def _play_done(self):
        self.root.bell()
        self.canvas.create_text(self.canvas_size/2, self.canvas_size/2 - 8,
                                text="DONE!", fill="#ff4466",
                                font=("Courier", 24, "bold"))

    def _in_resize_zone(self, x, y):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        return x >= w - self.RESIZE_MARGIN and y >= h - self.RESIZE_MARGIN

    def _on_press(self, e):
        # Don't start drag/resize when clicking on interactive widgets
        widget = e.widget
        if isinstance(widget, (tk.Spinbox, tk.Entry, tk.Button)):
            return

        lx = e.x_root - self.root.winfo_rootx()
        ly = e.y_root - self.root.winfo_rooty()

        if self._in_resize_zone(lx, ly):
            self._resizing = True
            self._resize_start_x = e.x_root
            self._resize_start_y = e.y_root
            self._resize_start_w = self.root.winfo_width()
            self._resize_start_h = self.root.winfo_height()
        else:
            self._resizing = False
            self._drag_x = e.x_root - self.root.winfo_x()
            self._drag_y = e.y_root - self.root.winfo_y()

    def _on_motion(self, e):
        if self._resizing:
            dw = e.x_root - self._resize_start_x
            dh = e.y_root - self._resize_start_y
            new_w = max(240, self._resize_start_w + dw)
            new_h = max(300, self._resize_start_h + dh)
            size = min(new_w, new_h - 160)
            self.canvas_size = max(160, size)
            self.canvas.config(width=self.canvas_size, height=self.canvas_size)
            self.root.geometry(f"{new_w}x{new_h}")
            frac = (self.remaining / self.total_seconds) if self.total_seconds > 0 else 1.0
            self.draw_circle(frac)
        else:
            x = e.x_root - self._drag_x
            y = e.y_root - self._drag_y
            self.root.geometry(f"+{x}+{y}")

    def _on_release(self, e):
        self._resizing = False

    # ── Minimize: just hide the window, click tray icon to restore ──
    def hide_app(self):
        self.root.withdraw()      # hides window completely
        self._show_restore_btn()  # show a small "show" button on screen edge

    def _show_restore_btn(self):
        # Small floating restore button at bottom-right of screen
        self._restore_win = tk.Toplevel()
        self._restore_win.overrideredirect(True)
        self._restore_win.attributes("-topmost", True)
        self._restore_win.attributes("-alpha", 0.85)
        self._restore_win.configure(bg="#1a1a1a")

        sw = self._restore_win.winfo_screenwidth()
        sh = self._restore_win.winfo_screenheight()
        self._restore_win.geometry(f"110x28+{sw-120}+{sh-60}")

        tk.Button(self._restore_win, text="⏱ SHOW TIMER",
                  bg="#1a1a1a", fg="#00e5ff",
                  font=("Courier", 8, "bold"), bd=0, cursor="hand2",
                  activebackground="#00e5ff", activeforeground="#000",
                  command=self._restore_app).pack(fill=tk.BOTH, expand=True)

    def _restore_app(self):
        if hasattr(self, "_restore_win"):
            self._restore_win.destroy()
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)


if __name__ == "__main__":
    root = tk.Tk()
    app = CircularCountdown(root)
    root.mainloop()
