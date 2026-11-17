#!/usr/bin/env python3
"""Antigravity Native Desktop Floating HUD Widget (Windows Always-On-Top).

Floats over ANY application (Antigravity, Chrome, VS Code, etc.).
- Borderless, draggable native desktop card.
- Replicates the exact shape & typography of the Antigravity Usage popover box.
- Supports Light Theme (default) & Dark Theme.
- Real-time polling of http://127.0.0.1:7899/api/telemetry.
- Click to expand / double click to open the full web cockpit in browser.
"""

from __future__ import annotations

import json
import math
import os
import sys
import threading
import time
import urllib.request
import webbrowser
import tkinter as tk
from tkinter import ttk

TELEMETRY_URL = "http://127.0.0.1:7899/api/telemetry"
WEB_HUD_URL = "http://127.0.0.1:7899"


class DesktopFloatingHUD:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Antigravity Usage HUD")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)  # Borderless clean card

        # Window geometry & position (Bottom-right corner of screen)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.w = 310
        self.h = 240
        self.x = screen_w - self.w - 30
        self.y = screen_h - self.h - 60
        self.root.geometry(f"{self.w}x{self.h}+{self.x}+{self.y}")

        self.is_dark = False  # Default to Light Theme as requested
        self._drag_x = 0
        self._drag_y = 0
        self.latest_data: dict = {}

        self.setup_ui()
        self.apply_theme()
        self.bind_events()

        # Start background polling thread
        self.running = True
        self.poll_thread = threading.Thread(target=self._telemetry_worker, daemon=True)
        self.poll_thread.start()

    def setup_ui(self) -> None:
        # Main Card Frame
        self.card = tk.Frame(self.root, highlightthickness=1)
        self.card.pack(fill=tk.BOTH, expand=True)

        # Header Bar
        self.header = tk.Frame(self.card)
        self.header.pack(fill=tk.X, padx=12, pady=(10, 6))

        self.lbl_title = tk.Label(self.header, text="Usage", font=("Segoe UI", 11, "bold"))
        self.lbl_title.pack(side=tk.LEFT)

        self.lbl_pulse = tk.Label(self.header, text="● LIVE", font=("Segoe UI", 8, "bold"), fg="#16a34a")
        self.lbl_pulse.pack(side=tk.LEFT, padx=8)

        # Header Controls (Theme toggle, Minimize, Close)
        self.btn_close = tk.Label(self.header, text="✕", font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.btn_close.pack(side=tk.RIGHT, padx=(4, 0))
        self.btn_close.bind("<Button-1>", lambda e: self.close())

        self.btn_theme = tk.Label(self.header, text="🌙", font=("Segoe UI", 9), cursor="hand2")
        self.btn_theme.pack(side=tk.RIGHT, padx=4)
        self.btn_theme.bind("<Button-1>", lambda e: self.toggle_theme())

        self.btn_cockpit = tk.Label(self.header, text="↗ Web", font=("Segoe UI", 8, "bold"), cursor="hand2")
        self.btn_cockpit.pack(side=tk.RIGHT, padx=4)
        self.btn_cockpit.bind("<Button-1>", lambda e: webbrowser.open(WEB_HUD_URL))

        # Canvas for Drawing Progress Rings & Items
        self.canvas = tk.Canvas(self.card, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)

        # Bottom Status Bar
        self.footer = tk.Frame(self.card)
        self.footer.pack(fill=tk.X, padx=12, pady=(4, 8))

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
        self.btn_close.config(bg=bg_card, fg=fg_sub)
        self.btn_cockpit.config(bg=bg_card, fg="#0284c7")
        self.lbl_directive.config(bg=bg_card)
        self.lbl_saved.config(bg=bg_card)

        self.redraw_canvas()

    def toggle_theme(self) -> None:
        self.is_dark = not self.is_dark
        self.apply_theme()

    def bind_events(self) -> None:
        # Dragging support anywhere on card or header
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
        fg_main = "#f4f4f5" if self.is_dark else "#0f172a"
        fg_sub = "#a1a1aa" if self.is_dark else "#64748b"
        bg_ring = "#27272a" if self.is_dark else "#e2e8f0"

        # Static fallback items if data not yet received
        items = [
            ("Gemini Models", [
                ("Weekly limit", "77% left", 77, "#22c55e", "Resets in 4d 3h"),
                ("5h limit", "47% left", 47, "#22c55e", "Resets in 1h 24m")
            ]),
            ("Claude and GPT models", [
                ("Weekly limit", "19% left", 19, "#eab308", "Resets in 1d 20h"),
                ("5h limit", "100% left", 100, "#22c55e", "100% reserve")
            ]),
            ("Gemini 4 Argon", [
                ("Weekly limit", "89% left", 89, "#22c55e", "Resets in 6d 21h")
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
                        l.get("color", "#22c55e"),
                        l.get("reset_en", "")
                    ))
                cat_list.append((c.get("title_en", "Category"), sub_rows))
            items = cat_list

        y = 6
        for cat_title, rows in items:
            # Category Header
            self.canvas.create_text(
                6, y,
                text=cat_title,
                anchor="w",
                fill=fg_main,
                font=("Segoe UI", 9, "bold")
            )
            y += 18

            # Limits inside category
            for lbl, stat_txt, pct, color, sub_txt in rows:
                # Label
                self.canvas.create_text(
                    14, y,
                    text=lbl,
                    anchor="w",
                    fill=fg_main,
                    font=("Segoe UI", 8)
                )
                # Value text (e.g. 77% left)
                self.canvas.create_text(
                    235, y,
                    text=stat_txt,
                    anchor="e",
                    fill=fg_main,
                    font=("Segoe UI", 8, "bold")
                )

                # Circular Progress Ring (width: 14x14)
                rx = 252
                ry = y - 7
                r = 6
                # Background circle
                self.canvas.create_oval(
                    rx - r, ry - r, rx + r, ry + r,
                    outline=bg_ring, width=2
                )
                # Fill arc
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
