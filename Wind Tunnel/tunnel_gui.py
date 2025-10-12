"""
Wind Tunnel GUI — Responsive (Debounced) + Welcome + Persistent Calibration
Date: 2025-10-11

Changes in this version:
- Pro-grade responsive scaling:
  • Debounced <Configure> events (no flicker, no constant font reconfig)
  • Scales fonts & widgets smoothly after user stops resizing
  • Resizes Matplotlib figure proportionally to window
- Persistent calibration: loads/saves 'calibration_matrix.txt'
- Welcome Manual at startup (+ Help→Manual, + "Don't show again" remembered in 'settings.json')
- Calibration modes: Easy (Lift only) and Advanced (Lift+Drag)
- Start/Stop Recording, Tare, CSV export

Expected serial CSV per line:  V, rho, F1, F2, F3, F4

Channel map (0-based):
  F1=Left-Vertical, F2=Left-Horizontal, F3=Right-Vertical, F4=Right-Horizontal
"""

import json
import os
import time
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkfont

import serial
import serial.tools.list_ports

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ================= Config =================
BAUD = 115200
TARE_SEC = 1.0
CAPTURE_SEC = 2.0
CAL_FORCE_N = 0.981         # 100 g ≈ 0.981 N
MIN_SIGNAL = 1e-6           # minimal acceptable delta to avoid NaNs

SETTINGS_FILE = "settings.json"
CALIB_FILE = "calibration_matrix.txt"

# Channel mapping (0-based for F1..F4)
CHANNEL_MAP = {
    "L": (0, 1),            # (Left-Vertical index, Left-Horizontal index)
    "R": (2, 3),            # (Right-Vertical index, Right-Horizontal index)
}


# ================= Utilities =================
def load_settings():
    s = {"show_welcome_on_start": True}
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                s.update(data)
    except Exception:
        pass
    return s

def save_settings(s):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
    except Exception as e:
        print("Settings save error:", e)


# ================= Serial Reader =================
class SerialReader:
    def __init__(self, port, baudrate=BAUD, timeout=0.05):
        self.port = port
        try:
            self.arduino = serial.Serial(port, baudrate=baudrate, timeout=timeout)
            print(f"✅ Connected to {port} @ {baudrate}")
        except Exception as e:
            print(f"❌ Connection failed on {port}: {e}")
            self.arduino = None

    def get_data(self):
        """Return [V, rho, F1, F2, F3, F4] as strings, or None if invalid/empty."""
        if not self.arduino or not self.arduino.is_open:
            return None
        try:
            raw = self.arduino.readline()
            if not raw:
                return None
            line = raw.decode("utf-8", errors="ignore").strip()
            if not line:
                return None
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 6:
                return None
            return parts[:6]
        except Exception:
            return None

    def close(self):
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
            print("🔌 Serial closed")


# ================= Responsive Font/Resize Manager =================
class ResponsiveManager:
    """
    Debounced responsive scaler for fonts and matplotlib figure.
    - Binds <Configure>, but applies scaling only after user stops resizing
      for 'DEBOUNCE_MS' (prevents flicker & CPU churn).
    - Updates a set of named fonts used by ttk styles and Text widgets.
    - Resizes matplotlib figure proportionally to window size.
    """
    DEBOUNCE_MS = 140  # Wait this long after last resize event

    def __init__(self, root, fig=None, base_w=1280, base_h=740):
        self.root = root
        self.fig = fig
        self.base_w = base_w
        self.base_h = base_h
        self._after_id = None
        self._last_applied = (base_w, base_h)

        # Create named fonts once
        self.fonts = {
            "title": tkfont.Font(family="Segoe UI", size=14, weight="bold"),
            "label": tkfont.Font(family="Segoe UI", size=11),
            "entry": tkfont.Font(family="Segoe UI", size=11),
            "button": tkfont.Font(family="Segoe UI", size=11, weight="bold"),
            "text": tkfont.Font(family="Consolas", size=11),
            "small": tkfont.Font(family="Segoe UI", size=10),
        }

        # Apply ttk styles once (don’t reapply on every resize)
        style = ttk.Style(self.root)
        style.configure("TLabel", font=self.fonts["label"])
        style.configure("TButton", font=self.fonts["button"])
        style.configure("TEntry", font=self.fonts["entry"])
        style.configure("TCombobox", font=self.fonts["entry"])
        style.configure("TLabelframe.Label", font=self.fonts["title"])
        style.configure("Treeview", font=self.fonts["label"])

        # Track text widgets to update
        self._text_widgets = []

        # Bind debounced resize
        self.root.bind("<Configure>", self._on_configure)

    def attach_text_widget(self, text_widget):
        text_widget.configure(font=self.fonts["text"])
        self._text_widgets.append(text_widget)

    def _on_configure(self, event):
        # Cancel any pending scaling job and schedule a new one
        if self._after_id:
            try:
                self.root.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = self.root.after(self.DEBOUNCE_MS, self._apply_scale)

    def _apply_scale(self):
        self._after_id = None
        w = max(self.root.winfo_width(), 1)
        h = max(self.root.winfo_height(), 1)

        # Only scale if size changed meaningfully
        prev_w, prev_h = self._last_applied
        if abs(w - prev_w) < 10 and abs(h - prev_h) < 10:
            return
        self._last_applied = (w, h)

        # Compute clamped scale
        scale = min(max(w / self.base_w, 0.7), 2.4)

        def set_font(font, base):
            new_size = max(int(base * scale), 8)
            font.configure(size=new_size)

        # Adjust font sizes smoothly
        set_font(self.fonts["title"], 14)
        set_font(self.fonts["label"], 11)
        set_font(self.fonts["entry"], 11)
        set_font(self.fonts["button"], 11)
        set_font(self.fonts["text"], 11)
        set_font(self.fonts["small"], 10)

        # Also nudge the matplotlib figure size proportional to width
        if self.fig is not None:
            try:
                # Keep a reasonable aspect ratio; scale by width factor
                base_fig_w, base_fig_h = 5.0, 3.0  # matches creation size
                k = min(max(w / self.base_w, 0.8), 2.0)
                self.fig.set_size_inches(base_fig_w * k, base_fig_h * k, forward=True)
                self.fig.canvas.draw_idle()
            except Exception:
                pass


# ================= Main GUI =================
class TunnelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wind Tunnel GUI")
        self.root.geometry("1280x740")
        self.root.minsize(900, 600)

        # menu
        self._build_menu()

        # state
        self.settings = load_settings()
        self.serial_reader = None
        self.zero = np.zeros(4, dtype=float)
        self.K = self._load_calibration_or_identity()
        self.record = False
        self.rec_df = pd.DataFrame(columns=["t", "V", "F1", "F2", "F3", "F4"])

        # UI
        self._build_layout()

        # responsive manager (debounced scaling, includes figure)
        self.resp = ResponsiveManager(self.root, fig=self.fig)

        # welcome manual on start
        if self.settings.get("show_welcome_on_start", True):
            self.open_welcome_manual()

        # start loop
        self.root.after(80, self._update_loop)

    # ---------- Menu ----------
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Manual", command=self.open_welcome_manual)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.root.config(menu=menubar)

    # ---------- UI ----------
    def _build_layout(self):
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        main = ttk.Frame(self.root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")
        for c in range(3):
            main.columnconfigure(c, weight=1, uniform="col")
        main.rowconfigure(1, weight=1)

        # Top bar
        top = ttk.Frame(main)
        top.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        for i in range(7):
            top.columnconfigure(i, weight=0)
        top.columnconfigure(6, weight=1)

        ttk.Label(top, text="COM Port:").grid(row=0, column=0, padx=4, sticky="w")
        self.port_var = tk.StringVar()
        self.cmb_ports = ttk.Combobox(top, textvariable=self.port_var, state="readonly", width=18)
        self.cmb_ports.grid(row=0, column=1, sticky="w")
        ttk.Button(top, text="Refresh", command=self._refresh_ports).grid(row=0, column=2, padx=4)
        ttk.Button(top, text="Connect", command=self._connect_serial).grid(row=0, column=3, padx=4)
        self.status_var = tk.StringVar(value="Status: Not connected")
        ttk.Label(top, textvariable=self.status_var).grid(row=0, column=5, padx=10, sticky="w")
        self._refresh_ports()

        # Controls panel
        ctrl = ttk.Frame(main)
        ctrl.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        for r in range(10):
            ctrl.rowconfigure(r, weight=0)
        ctrl.rowconfigure(10, weight=1)
        ctrl.columnconfigure(0, weight=1)
        ctrl.columnconfigure(1, weight=1)

        ttk.Label(ctrl, text="Wind Velocity:").grid(row=0, column=0, sticky="w")
        self.vel_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.vel_var, state="readonly", width=12).grid(row=0, column=1, sticky="w")

        ttk.Label(ctrl, text="Density:").grid(row=1, column=0, sticky="w")
        self.rho_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.rho_var, state="readonly", width=12).grid(row=1, column=1, sticky="w")

        ttk.Button(ctrl, text="Tare (Zero)", command=self._tare).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 2))
        ttk.Button(ctrl, text="Start Recording", command=self._start_record).grid(row=3, column=0, columnspan=2, sticky="ew", pady=2)
        ttk.Button(ctrl, text="Stop Recording", command=self._stop_record).grid(row=4, column=0, columnspan=2, sticky="ew", pady=2)
        ttk.Button(ctrl, text="Export CSV", command=self._export_csv).grid(row=5, column=0, columnspan=2, sticky="ew", pady=2)

        # Calibration group
        cal_group = ttk.LabelFrame(ctrl, text="Calibration")
        cal_group.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
        for i in range(2):
            cal_group.columnconfigure(i, weight=1)
        ttk.Label(cal_group, text="Mode:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.cal_mode = tk.StringVar(value="easy")  # "easy" or "advanced"
        ttk.Radiobutton(cal_group, text="Easy (Lift only, 2 steps)", variable=self.cal_mode, value="easy").grid(row=1, column=0, columnspan=2, sticky="w", padx=12)
        ttk.Radiobutton(cal_group, text="Advanced (Lift+Drag, 4 steps)", variable=self.cal_mode, value="advanced").grid(row=2, column=0, columnspan=2, sticky="w", padx=12)
        ttk.Button(cal_group, text="Calibration", command=self._open_cal).grid(row=3, column=0, columnspan=2, sticky="ew", padx=8, pady=8)

        # Forces panel
        mid = ttk.LabelFrame(main, text="Forces (N)")
        mid.grid(row=1, column=1, sticky="nsew", padx=8)
        mid.rowconfigure(0, weight=1)
        for c in range(4):
            mid.columnconfigure(c, weight=1)
        self.force_boxes = []
        for i in range(4):
            tbox = tk.Text(mid, width=14, height=24)
            tbox.grid(row=0, column=i, padx=6, sticky="nsew")
            # Font set via ResponsiveManager after creation
            self.force_boxes.append(tbox)

        # Graph panel
        right = ttk.Frame(main)
        right.grid(row=1, column=2, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        colors = ["b", "g", "r", "m"]
        self.lines = [self.ax.plot([], [], colors[i]+"-", label=f"F{i+1}")[0] for i in range(4)]
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Force (N)")
        self.ax.legend()
        self.t0 = time.time()
        self.ts = []
        self.hist = [[] for _ in range(4)]

        # Attach text widgets to responsive manager after fig exists
        # (done in __init__ after ResponsiveManager creation)
        # But we can set now when resp is assigned later
        self._pending_text_attach = True  # flag to attach once resp is ready

    # ---------- Welcome Manual ----------
    def open_welcome_manual(self):
        w = tk.Toplevel(self.root)
        w.title("Welcome — Wind Tunnel Manual")
        w.geometry("640x520")
        w.transient(self.root)

        # Quick start
        quick = ttk.LabelFrame(w, text="Quick Start")
        quick.pack(fill="x", padx=10, pady=(10, 6))
        lbl = ttk.Label(
            quick,
            justify="left",
            text=(
                "1) Connect → select COM → Connect.\n"
                "2) Click Tare (Zero) with nothing touching.\n"
                "3) Click Start Recording to log.\n"
                "4) Calibration → Easy (Lift) for 100 g on white platforms.\n"
                "5) (Optional) Advanced for Lift+Drag with horizontal pull.\n"
                "6) Export CSV when done."
            )
        )
        lbl.pack(anchor="w", padx=8, pady=6)

        # More detail button
        btns = ttk.Frame(w)
        btns.pack(fill="x", padx=10, pady=6)
        ttk.Button(btns, text="More detail…", command=self._open_full_manual).pack(side="left")

        # Don't show again
        self.var_show_again = tk.BooleanVar(value=self.settings.get("show_welcome_on_start", True))
        cb = ttk.Checkbutton(w, text="Show this at startup", variable=self.var_show_again, command=self._toggle_welcome_setting)
        cb.pack(anchor="w", padx=12, pady=6)

        ttk.Button(w, text="Close", command=w.destroy).pack(pady=(0,10))

    def _toggle_welcome_setting(self):
        self.settings["show_welcome_on_start"] = bool(self.var_show_again.get())
        save_settings(self.settings)

    def _open_full_manual(self):
        m = tk.Toplevel(self.root)
        m.title("Manual — Details")
        m.geometry("760x600")
        m.transient(self.root)

        frame = ttk.Frame(m)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        txt = tk.Text(frame, wrap="word")
        txt.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(frame, command=txt.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        txt.configure(yscrollcommand=scroll.set)

        manual = (
            "Tare (Zero)\n"
            "• Ensure nothing touches the model/plates. Click Tare to zero offsets.\n\n"
            "Recording\n"
            "• Start/Stop controls saving. Export writes a CSV with time, velocity, and forces.\n\n"
            "Calibration — Easy (Lift only)\n"
            "• Step 1: Left — baseline auto-captured; place 100 g on LEFT white platform; Capture (2 s).\n"
            "• Step 2: Right — baseline auto-captured; place 100 g on RIGHT white platform; Capture (2 s).\n"
            "• This updates only the vertical (lift) rows of the 4×4 matrix.\n\n"
            "Calibration — Advanced (Lift + Drag)\n"
            "• Step 1: LEFT vertical — 100 g on LEFT white platform.\n"
            "• Step 2: LEFT horizontal — 100 g pull at platform height (string + pulley) for pure horizontal.\n"
            "• Step 3: RIGHT vertical — 100 g on RIGHT white platform.\n"
            "• Step 4: RIGHT horizontal — 100 g pull at platform height.\n"
            "• Uses load-baseline deltas and least-squares to compute the 2×2 per side.\n\n"
            "Tips\n"
            "• Keep horizontal pulls level at platform height to avoid vertical components.\n"
            "• Center the 100 g on the white platform for vertical loads.\n"
            "• Re-Tare when you change fixtures. Use multiple samples if noisy.\n"
        )
        txt.insert("1.0", manual)

        # Attach font scaling after insertion (so sizing is smooth)
        if hasattr(self, "resp"):
            self.resp.attach_text_widget(txt)

    # ---------- Serial ----------
    def _refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.cmb_ports["values"] = ports
        if ports:
            self.port_var.set(ports[0])
        else:
            self.port_var.set("")
        return ports

    def _connect_serial(self):
        port = self.port_var.get()
        if not port:
            messagebox.showwarning("Port", "No COM port selected.")
            return
        self.serial_reader = SerialReader(port)
        if self.serial_reader.arduino and self.serial_reader.arduino.is_open:
            self.status_var.set(f"Connected: {port} @ {BAUD}")
        else:
            self.status_var.set("Connection failed")

    # ---------- Helpers ----------
    def _parse_F(self, row):
        try:
            return np.array([float(row[2]), float(row[3]), float(row[4]), float(row[5])], dtype=float)
        except Exception:
            return None

    def _avg_raw_over(self, seconds):
        """Average F1..F4 (zero-corrected) for 'seconds'."""
        t_end = time.time() + seconds
        samp = []
        while time.time() < t_end:
            row = self.serial_reader.get_data() if self.serial_reader else None
            if not row:
                continue
            F = self._parse_F(row)
            if F is None:
                continue
            samp.append(F - self.zero)
        if not samp:
            return None
        return np.mean(np.vstack(samp), axis=0)

    # ---------- Tare & Recording ----------
    def _tare(self):
        if not self.serial_reader:
            messagebox.showerror("Tare", "Connect serial first.")
            return
        avg = self._avg_raw_over(TARE_SEC)
        if avg is None:
            messagebox.showwarning("Tare", "No data captured.")
            return
        self.zero = (avg + self.zero) / 2.0  # gentle update to reduce jumps
        messagebox.showinfo("Tare", f"Tare set to: {self.zero.round(4)}")

    def _start_record(self):
        self.record = True
        self.rec_df = pd.DataFrame(columns=["t", "V", "F1", "F2", "F3", "F4"])
        messagebox.showinfo("Record", "Recording started.")

    def _stop_record(self):
        self.record = False
        messagebox.showinfo("Record", "Recording stopped.")

    def _export_csv(self):
        if self.rec_df.empty:
            messagebox.showwarning("Export", "No recorded data.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            self.rec_df.to_csv(path, index=False)
            messagebox.showinfo("Export", f"Saved to {path}")

    # ---------- Calibration (Easy/Advanced) ----------
    def _open_cal(self):
        if not self.serial_reader:
            messagebox.showerror("Calibration", "Connect serial first.")
            return

        self.cal = tk.Toplevel(self.root)
        self.cal.title("Calibration")
        self.cal.geometry("560x420")
        self.cal.transient(self.root)
        self.cal.grab_set()
        self.cal.columnconfigure(0, weight=1)
        self.cal.rowconfigure(2, weight=1)

        mode = self.cal_mode.get()  # "easy" or "advanced"
        self.cal_mode_running = mode

        self.cal_label = ttk.Label(self.cal, text="", wraplength=520, justify="left")
        self.cal_label.grid(row=0, column=0, sticky="ew", padx=10, pady=8)

        btns = ttk.Frame(self.cal)
        btns.grid(row=1, column=0, sticky="ew", padx=10, pady=4)
        for i in range(4):
            btns.columnconfigure(i, weight=1)

        self.btn_next = ttk.Button(btns, text="Start", command=self._cal_next)
        self.btn_next.grid(row=0, column=0, padx=4, sticky="ew")

        self.btn_capture = ttk.Button(btns, text="Capture", command=self._cal_capture, state="disabled")
        self.btn_capture.grid(row=0, column=1, padx=4, sticky="ew")

        self.btn_finish = ttk.Button(btns, text="Finish & Save", command=self._cal_finish, state="disabled")
        self.btn_finish.grid(row=0, column=2, padx=4, sticky="ew")

        self.btn_cancel = ttk.Button(btns, text="Cancel", command=self.cal.destroy)
        self.btn_cancel.grid(row=0, column=3, padx=4, sticky="ew")

        self.cal_log = tk.Text(self.cal, height=12)
        self.cal_log.grid(row=2, column=0, sticky="nsew", padx=10, pady=8)

        if hasattr(self, "resp"):
            self.resp.attach_text_widget(self.cal_log)

        if mode == "easy":
            self.cal_steps = [
                ("L_vert", "Step 1/2 — LEFT VERTICAL:\nBaseline auto-capture → place 100 g on LEFT white platform → Capture (2 s)."),
                ("R_vert", "Step 2/2 — RIGHT VERTICAL:\nBaseline auto-capture → place 100 g on RIGHT white platform → Capture (2 s).")
            ]
        else:
            self.cal_steps = [
                ("L_vert", "Step 1/4 — LEFT VERTICAL (100 g on LEFT white platform)."),
                ("L_horz", "Step 2/4 — LEFT HORIZONTAL (100 g horizontal pull at platform height)."),
                ("R_vert", "Step 3/4 — RIGHT VERTICAL (100 g on RIGHT white platform)."),
                ("R_horz", "Step 4/4 — RIGHT HORIZONTAL (100 g horizontal pull at platform height).")
            ]
        self.cal_idx = -1
        self.cal_store = {}   # key -> {'baseline': vec, 'load': vec, 'delta': vec}
        self._cal_info("Ready. Click Start.")

    def _cal_info(self, msg):
        self.cal_label.config(text=msg)

    def _log(self, msg):
        self.cal_log.insert("end", msg + "\n")
        self.cal_log.see("end")

    def _cal_next(self):
        self.cal_idx += 1
        if self.cal_idx >= len(self.cal_steps):
            self._cal_info("All steps captured. Click 'Finish & Save'.")
            self.btn_capture.config(state="disabled")
            self.btn_finish.config(state="normal")
            self.btn_next.config(state="disabled")
            return

        key, text = self.cal_steps[self.cal_idx]
        self.cal_current_key = key
        # Auto baseline capture
        self._cal_info(text + "\n\nCapturing BASELINE (no load)…")
        baseline = self._avg_raw_over(TARE_SEC)
        if baseline is None:
            messagebox.showerror("Calibration", "No data for baseline. Try again.")
            self.cal_idx -= 1
            return
        self.cal_store[key] = {"baseline": baseline, "load": None, "delta": None}
        self._log(f"[{key}] BASELINE = {baseline.round(6)}")
        self._cal_info(text + "\n\nBaseline captured. Apply the 100 g force, then click 'Capture'.")
        self.btn_capture.config(state="normal")
        self.btn_next.config(state="disabled")
        self.btn_finish.config(state="disabled")

    def _cal_capture(self):
        key = self.cal_current_key
        load = self._avg_raw_over(CAPTURE_SEC)
        if load is None:
            messagebox.showerror("Calibration", "No data for LOAD.")
            return
        baseline = self.cal_store[key]["baseline"]
        delta = load - baseline
        self.cal_store[key]["load"] = load
        self.cal_store[key]["delta"] = delta
        self._log(f"[{key}] LOAD  = {load.round(6)}")
        self._log(f"[{key}] DELTA = {delta.round(6)}")

        # quick signal check on relevant channels
        if key.startswith("L"):
            v_i, h_i = CHANNEL_MAP["L"]
        else:
            v_i, h_i = CHANNEL_MAP["R"]
        if np.all(np.abs(delta[[v_i, h_i]]) < MIN_SIGNAL):
            messagebox.showwarning("Calibration", "Signal too small. Check force and try again.")
            return

        self.btn_capture.config(state="disabled")
        self.btn_next.config(state="normal")
        if self.cal_idx == len(self.cal_steps) - 1:
            self.btn_finish.config(state="normal")
        self._cal_info("Load captured. Click 'Next' for the next step, or 'Finish & Save' if complete.")

    def _cal_finish(self):
        mode = self.cal_mode_running
        try:
            if mode == "easy":
                # Easy (Lift-only): update only vertical rows with per-side gains (no cross-coupling)
                K_new = np.array(self.K)
                LV, LH = CHANNEL_MAP["L"]
                RV, RH = CHANNEL_MAP["R"]

                dL = self.cal_store["L_vert"]["delta"]
                if abs(dL[LV]) < MIN_SIGNAL or np.isnan(dL[LV]):
                    raise ValueError("Left vertical signal too small/invalid.")
                gain_L = CAL_FORCE_N / dL[LV]

                dR = self.cal_store["R_vert"]["delta"]
                if abs(dR[RV]) < MIN_SIGNAL or np.isnan(dR[RV]):
                    raise ValueError("Right vertical signal too small/invalid.")
                gain_R = CAL_FORCE_N / dR[RV]

                # Lift rows at indices 0 and 2
                K_new[0, :] = 0.0
                K_new[0, LV] = gain_L
                K_new[2, :] = 0.0
                K_new[2, RV] = gain_R

                np.savetxt(CALIB_FILE, K_new, delimiter=",")
                self.K = K_new
                self._log("\nEasy calibration complete. Vertical rows updated; drag rows unchanged.")
                messagebox.showinfo("Calibration", "Saved (Lift-only). Will auto-load next time.")
                self.cal.destroy()

            else:
                # Advanced (Lift+Drag): per-side 2×2 via least-squares with deltas
                LV, LH = CHANNEL_MAP["L"]
                RV, RH = CHANNEL_MAP["R"]

                # LEFT
                dL_vert = self.cal_store["L_vert"]["delta"]
                dL_horz = self.cal_store["L_horz"]["delta"]
                R_L = np.column_stack([dL_vert[[LV, LH]], dL_horz[[LV, LH]]])  # 2x2

                # RIGHT
                dR_vert = self.cal_store["R_vert"]["delta"]
                dR_horz = self.cal_store["R_horz"]["delta"]
                R_R = np.column_stack([dR_vert[[RV, RH]], dR_horz[[RV, RH]]])  # 2x2

                F_side = np.array([[CAL_FORCE_N, 0.0],
                                   [0.0,         CAL_FORCE_N]], dtype=float)

                K_L = F_side @ np.linalg.pinv(R_L)
                K_R = F_side @ np.linalg.pinv(R_R)

                K_full = np.block([
                    [K_L,                 np.zeros((2,2))],
                    [np.zeros((2,2)),     K_R           ]
                ])

                if np.isnan(K_full).any():
                    raise ValueError("NaN detected in calibration matrix; check inputs.")
                np.savetxt(CALIB_FILE, K_full, delimiter=",")
                self.K = K_full
                self._log(f"\nAdvanced calibration complete.\nK=\n{np.array2string(K_full, precision=6)}")
                messagebox.showinfo("Calibration", "Saved (Lift+Drag). Will auto-load next time.")
                self.cal.destroy()

        except Exception as e:
            messagebox.showerror("Calibration", f"Failed to compute/save matrix:\n{e}")

    # ---------- Live loop ----------
    def _update_loop(self):
        try:
            # Attach text widgets to responsive manager exactly once (after fig exists)
            if getattr(self, "_pending_text_attach", False) and hasattr(self, "resp"):
                for tbox in self.force_boxes:
                    self.resp.attach_text_widget(tbox)
                self._pending_text_attach = False

            if self.serial_reader:
                row = self.serial_reader.get_data()
                if row:
                    self.vel_var.set(row[0])
                    self.rho_var.set(row[1])
                    Fraw = self._parse_F(row)
                    if Fraw is not None:
                        Fcorr = Fraw - self.zero
                        Fy = self.K @ Fcorr  # 4-vector (N)

                        # Append to text boxes (cap to avoid huge memory & scrollbar lag)
                        for i, box in enumerate(self.force_boxes):
                            box.insert("1.0", f"{Fy[i]:.3f}\n")
                            if int(box.index('end-1c').split('.')[0]) > 200:  # keep ~200 lines max
                                box.delete('200.0', 'end')

                        # graph
                        t = time.time() - self.t0
                        self.ts.append(t)
                        for i in range(4):
                            self.hist[i].append(Fy[i])
                            # keep last N points to avoid slowdown
                            if len(self.hist[i]) > 2000:
                                self.hist[i] = self.hist[i][-2000:]
                        if len(self.ts) > 2000:
                            self.ts = self.ts[-2000:]

                        for i in range(4):
                            self.lines[i].set_data(self.ts, self.hist[i])
                        self.ax.relim()
                        self.ax.autoscale_view()
                        self.canvas.draw_idle()

                        # recording
                        if self.record:
                            self.rec_df.loc[len(self.rec_df)] = [t, row[0]] + list(Fy)
        finally:
            self.root.after(80, self._update_loop)

    # ---------- Calibration load/save ----------
    def _load_calibration_or_identity(self):
        try:
            K = np.loadtxt(CALIB_FILE, delimiter=",")
            if K.shape == (4,4) and not np.isnan(K).any():
                print("Loaded calibration matrix.")
                return K
            raise ValueError("bad matrix")
        except Exception:
            print("Using identity calibration matrix.")
            return np.identity(4)


# ================= Run =================
if __name__ == "__main__":
    root = tk.Tk()
    app = TunnelGUI(root)
    root.mainloop()
