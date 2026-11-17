#!/usr/bin/env python3
"""Antigravity Native Desktop Floating HUD Widget (Windows Always-On-Top).

Floats over ANY application (Antigravity, Chrome, VS Code, etc.).
- Guaranteed Always-On-Top via Win32 SetWindowPos API.
- Replicates the exact shape & typography of the Antigravity Usage popover box.
- Supports Light Theme (default) & Dark Theme.
- Can toggle between Compact Floating Pill and Expanded Card.
- Draggable anywhere across the screen.
- Real-time polling of http://127.0.0.1:7899/api/telemetry.
"""

from __future__ import annotations

import ctypes
import json
import os
import sys
import threading
import time
import urllib.request
import webbrowser
import tkinter as tk

TELEMETRY_URL = "http://127.0.0.1:7899/api/telemetry"
WEB_HUD_URL = "http://127.0.0.1:7899"
# Use pure ASCII title so Windows Win32 FindWindowW matches 100% reliably
WINDOW_TITLE = "Antigravity_Quota_HUD"


class DesktopFloatingHUD:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)

        # Screen geometry
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        self.is_expanded = True
        self.is_dark = False  # Light Theme by default (لون فاتح)

        self.w_expanded = 310
        self.h_expanded = 280
        self.w_compact = 230
        self.h_compact = 48

        # Position at prominent top-right quadrant
        self.x = max(100, screen_w - self.w_expanded - 50)
        self.y = 80

        self.root.geometry(f"{self.w_expanded}x{self.h_expanded}+{self.x}+{self.y}")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self._drag_x = 0
        self._drag_y = 0
        self.latest_data: dict = {}

        self.setup_ui()
        self.apply_theme()
        self.bind_events()

        # Force Windows TopMost via Win32 API repeatedly on startup
        self.root.after(100, self._force_win32_topmost)
        self.root.after(800, self._force_win32_topmost)

        # Telemetry worker
        self.running = True
        self.poll_thread = threading.Thread(target=self._telemetry_worker, daemon=True)
        self.poll_thread.start()

    def _force_win32_topmost(self) -> None:
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, WINDOW_TITLE)
            if hwnd:
                HWND_TOPMOST = -1
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_SHOWWINDOW = 0x0040
                ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
                ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass

    def setup_ui(self) -> None:
        # Main Card Frame
        self.card = tk.Frame(self.root, highlightthickness=1)
        self.card.pack(fill=tk.BOTH, expand=True)

        # Header Bar
        self.header = tk.Frame(self.card)
        self.header.pack(fill=tk.X, padx=10, pady=(6, 4))

        self.lbl_title = tk.Label(self.header, text="⚡ Usage", font=("Segoe UI", 10, "bold"), cursor="hand2")
        self.lbl_title.pack(side=tk.LEFT)

        self.lbl_pulse = tk.Label(self.header, text="● LIVE", font=("Segoe UI", 8, "bold"), fg="#16a34a")
        self.lbl_pulse.pack(side=tk.LEFT, padx=6)

        # Header Controls
        self.btn_toggle_mode = tk.Label(self.header, text="▼", font=("Segoe UI", 8, "bold"), cursor="hand2")
        self.btn_toggle_mode.pack(side=tk.RIGHT, padx=4)
        self.btn_toggle_mode.bind("<Button-1>", lambda e: self.toggle_expand())

        self.btn_theme = tk.Label(self.header, text="🌙", font=("Segoe UI", 9), cursor="hand2")
        self.btn_theme.pack(side=tk.RIGHT, padx=4)
        self.btn_theme.bind("<Button-1>", lambda e: self.toggle_theme())

        self.btn_cockpit = tk.Label(self.header, text="↗ Web", font=("Segoe UI", 8, "bold"), cursor="hand2")
        self.btn_cockpit.pack(side=tk.RIGHT, padx=4)
        self.btn_cockpit.bind("<Button-1>", lambda e: webbrowser.open(WEB_HUD_URL))

        # Canvas for Drawing Progress Rings & Items
        self.canvas = tk.Canvas(self.card, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=2)

        # Bottom Directive & Savings Bar
        self.footer = tk.Frame(self.card)
        self.footer.pack(fill=tk.X, padx=10, pady=(2, 6))

        self.lbl_directive = tk.Label(
            self.footer,
            text="Argon (89%) Recommended",
            font=("Segoe UI", 8, "bold"),
            fg="#0284c7"
        )
        self.lbl_directive.pack(side=tk.LEFT)

        self.lbl_saved = tk.Label(
            self.footer,
            text="+488K saved",
            font=("Consolas", 8, "bold"),
            fg="#16a34a"
        )
        self.lbl_saved.pack(side=tk.RIGHT)

    def apply_theme(self) -> None:
        if self.is_dark:
            bg_card = "#18181b"
            bg_border = "#3f3f46"
            fg_main = "#f4f4f5"
            fg_sub = "#a1a1aa"
            self.btn_theme.config(text="☀️", fg=fg_main, bg=bg_card)
        else:
            bg_card = "#ffffff"
            bg_border = "#cbd5e1"
            fg_main = "#0f172a"
            fg_sub = "#64748b"
            self.btn_theme.config(text="🌙", fg=fg_main, bg=bg_card)

        self.card.config(bg=bg_card, highlightbackground=bg_border)
        self.header.config(bg=bg_card)
        self.footer.config(bg=bg_card)
        self.canvas.config(bg=bg_card)

        self.lbl_title.config(bg=bg_card, fg=fg_main)
        self.lbl_pulse.config(bg=bg_card)
        self.btn_toggle_mode.config(bg=bg_card, fg=fg_sub)
        self.btn_cockpit.config(bg=bg_card, fg="#0284c7")
        self.lbl_directive.config(bg=bg_card)
        self.lbl_saved.config(bg=bg_card)

        self.redraw_canvas()

    def toggle_expand(self) -> None:
        self.is_expanded = not self.is_expanded
        curr_x = self.root.winfo_x()
        curr_y = self.root.winfo_y()

        if self.is_expanded:
            self.root.geometry(f"{self.w_expanded}x{self.h_expanded}+{curr_x}+{curr_y}")
            self.canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=2)
            self.footer.pack(fill=tk.X, padx=10, pady=(2, 6))
            self.btn_toggle_mode.config(text="▲")
        else:
            self.canvas.pack_forget()
            self.footer.pack_forget()
            self.root.geometry(f"{self.w_compact}x{self.h_compact}+{curr_x}+{curr_y}")
            self.btn_toggle_mode.config(text="▼")

    def toggle_theme(self) -> None:
        self.is_dark = not self.is_dark
        self.apply_theme()

    def bind_events(self) -> None:
        for w in (self.card, self.header, self.lbl_title, self.canvas):
            w.bind("<ButtonPress-1>", self._on_drag_start)
            w.bind("<B1-Motion>", self._on_drag_move)
            w.bind("<Double-Button-1>", lambda e: webbrowser.open(WEB_HUD_URL))

    def _on_drag_start(self, event: tk.Event) -> None:
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag_move(self, event: tk.Event) -> None:
        deltax = event.x - self._drag_x
        deltay = event.y - self._drag_y
        new_x = self.root.winfo_x() + deltax
        new_y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{new_x}+{new_y}")

    def redraw_canvas(self) -> None:
        self.canvas.delete("all")
        if not self.is_expanded:
            return

        fg_main = "#f4f4f5" if self.is_dark else "#0f172a"
        fg_sub = "#a1a1aa" if self.is_dark else "#64748b"
        bg_ring = "#27272a" if self.is_dark else "#e2e8f0"

        items = [
            ("Gemini Models", [
                ("Weekly limit", "77% left", 77, "#16a34a", "Resets in 4d 3h"),
                ("5h limit", "47% left", 47, "#16a34a", "Resets in 1h 24m")
            ]),
            ("Claude and GPT models", [
                ("Weekly limit", "19% left", 19, "#d97706", "Resets in 1d 20h"),
                ("5h limit", "100% left", 100, "#16a34a", "100% reserve")
            ]),
            ("Gemini 4 Argon", [
                ("Weekly limit", "89% left", 89, "#16a34a", "Resets in 6d 21h")
            ])
        ]

        if self.latest_data and "categories" in self.latest_data:
            cat_list = []
            for c in self.latest_data["categories"]:
                sub_rows = []
                for l in c.get("limits", []):
                    sub_rows.append((
                        l.get("name_en", "Limit"),
                        f"{l.get('pct', 0)}% left",
                        l.get("pct", 0),
                        l.get("color", "#16a34a"),
                        l.get("reset_en", "")
                    ))
                cat_list.append((c.get("title_en", "Category"), sub_rows))
            items = cat_list

        y = 6
        for cat_title, rows in items:
            self.canvas.create_text(
                6, y,
                text=cat_title,
                anchor="w",
                fill=fg_main,
                font=("Segoe UI", 9, "bold")
            )
            y += 18

            for lbl, stat_txt, pct, color, sub_txt in rows:
                self.canvas.create_text(
                    14, y,
                    text=lbl,
                    anchor="w",
                    fill=fg_main,
                    font=("Segoe UI", 8)
                )
                self.canvas.create_text(
                    230, y,
                    text=stat_txt,
                    anchor="e",
                    fill=fg_main,
                    font=("Segoe UI", 8, "bold")
                )

                rx = 246
                ry = y - 7
                r = 6
                self.canvas.create_oval(
                    rx - r, ry - r, rx + r, ry + r,
                    outline=bg_ring, width=2
                )
                extent = (pct / 100.0) * -359.9
                self.canvas.create_arc(
                    rx - r, ry - r, rx + r, ry + r,
                    start=90, extent=extent,
                    outline=color, width=2, style=tk.ARC
                )
                y += 18

            y += 4

    def update_data(self, data: dict) -> None:
        self.latest_data = data
        if "advice" in data:
            self.lbl_directive.config(text=f"Target: {data['advice'].get('target_model', 'Argon')}")
        if "roi" in data:
            tok = data["roi"].get("total_tokens_saved", 488281)
            self.lbl_saved.config(text=f"+{tok/1000:.0f}K saved")
        self.redraw_canvas()

    def _telemetry_worker(self) -> None:
        while self.running:
            try:
                req = urllib.request.Request(TELEMETRY_URL, headers={"User-Agent": "Antigravity-HUD/13.0"})
                with urllib.request.urlopen(req, timeout=2.5) as resp:
                    if resp.status == 200:
                        payload = json.loads(resp.read().decode("utf-8"))
                        self.root.after(0, self.update_data, payload)
            except Exception:
                pass
            time.sleep(2.5)

    def close(self) -> None:
        self.running = False
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = DesktopFloatingHUD()
    app.run()
