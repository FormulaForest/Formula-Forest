"""
Wind Tunnel GUI — Front/Back + Per-Sensor Calibration (Responsive + Auto-Connect + Reset Data)
Date: 2025-10-12

Mapping (your setup)
  F1 = Front Vertical  (Lift Front)
  F2 = Front Horizontal(Drag Front)
  F3 = Back  Vertical  (Lift Back)
  F4 = Back  Horizontal(Drag Back)

Serial line (space-separated):  velocity density F1 F2 F3 F4
Baud: 115200

Features
- Debounced responsive scaling (no flicker), matplotlib resizes smoothly
- Auto-connect to first working COM port @115200 (can still select manually)
- Welcome Manual at startup + Help→Manual; “Don’t show again” saved in settings.json
- Tare, Start/Stop Recording, Export CSV
- NEW: Per-sensor calibration (dropdown + one button)
  • Choose: Front Lift / Front Drag / Back Lift / Back Drag
  • Each calibration asks for baseline (auto) then 100 g load capture (2 s)
  • Updates only that channel’s row in the 4×4 calibration matrix (no cross-coupling)
  • Auto-saves calibration to calibration_matrix.txt
- Reset Data: clears graph + recording buffer and resets time to 0

Outputs (Fy): [Front Lift, Front Drag, Back Lift, Back Drag]
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

# Channel mapping (0-based for F1..F4) — FRONT/BACK
# Output order (rows in K and boxes): [Front Lift, Front Drag, Back Lift, Back Drag]
# Input/raw order (columns in K):     [F1, F2, F3, F4]
FB_INDEX = {
    "Front Lift (F1)":     (row := 0, col := 0),
    "Front Drag (F2)":     (1, 1),
    "Back Lift (F3)":      (2, 2),
    "Back Drag (F4)":      (3, 3),
}
CAL_OPTIONS = list(FB_INDEX.keys())

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
        """Return [V, rho, F1, F2, F3, F4] as strings, or None if invalid/empty.
           Robust to spaces or commas; we normalize commas to spaces and split().
        """
        if not self.arduino or not self.arduino.is_open:
            return None
        try:
            raw = self.arduino.readline()
            if not raw:
                return None
            line = raw.decode("utf-8", errors="ignore").replace(",", " ").strip()
            if not line:
                return None
            parts = line.split()
            if len(parts) < 6:
                return None
            return parts[:6]
        except Exception:
            return None

    def close(self):
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
            print("🔌 Serial closed")

# ================= Responsive Manager (debounced) =================
class ResponsiveManager:
    """Debounced scaling for fonts and matplotlib figure (no flicker)."""
    DEBOUNCE_MS = 140

    def __init__(self, root, fig=None, base_w=1280, base_h=740):
        self.root = root
        self.fig = fig
        self.base_w = base_w
        self.base_h = base_h
        self._after_id = None
        self._last_applied = (base_w, base_h)

        self.fonts = {
            "title": tkfont.Font(family="Segoe UI", size=14, weight="bold"),
            "label": tkfont.Font(family="Segoe UI", size=11),
            "entry": tkfont.Font(family="Segoe UI", size=11),
            "button": tkfont.Font(family="Segoe UI", size=11, weight="bold"),
            "text": tkfont.Font(family="Consolas", size=11),
            "small": tkfont.Font(family="Segoe UI", size=10),
        }
        style = ttk.Style(self.root)
        style.configure("TLabel", font=self.fonts["label"])
        style.configure("TButton", font=self.fonts["button"])
        style.configure("TEntry", font=self.fonts["entry"])
        style.configure("TCombobox", font=self.fonts["entry"])
        style.configure("TLabelframe.Label", font=self.fonts["title"])
        style.configure("Treeview", font=self.fonts["label"])

        self._text_widgets = []
        self.root.bind("<Configure>", self._on_configure)

    def attach_text_widget(self, text_widget):
        text_widget.configure(font=self.fonts["text"])
        self._text_widgets.append(text_widget)

    def _on_configure(self, event):
        if self._after_id:
            try: self.root.after_cancel(self._after_id)
            except Exception: pass
        self._after_id = self.root.after(self.DEBOUNCE_MS, self._apply_scale)

    def _apply_scale(self):
        self._after_id = None
        w = max(self.root.winfo_width(), 1)
        h = max(self.root.winfo_height(), 1)

        prev_w, prev_h = self._last_applied
        if abs(w - prev_w) < 10 and abs(h - prev_h) < 10:
            return
        self._last_applied = (w, h)

        scale = min(max(w / self.base_w, 0.7), 2.4)
        def set_font(font, base):
            font.configure(size=max(int(base * scale), 8))

        set_font(self.fonts["title"], 14)
        set_font(self.fonts["label"], 11)
        set_font(self.fonts["entry"], 11)
        set_font(self.fonts["button"], 11)
        set_font(self.fonts["text"], 11)
        set_font(self.fonts["small"], 10)

        if self.fig is not None:
            try:
                base_fig_w, base_fig_h = 5.0, 3.0
                k = min(max(w / self.base_w, 0.8), 2.0)
                self.fig.set_size_inches(base_fig_w * k, base_fig_h * k, forward=True)
                self.fig.canvas.draw_idle()
            except Exception:
                pass

# ================= Main GUI =================
class TunnelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wind Tunnel GUI — Front/Back")
        self.root.geometry("1280x740")
        self.root.minsize(900, 600)

        self._build_menu()

        self.settings = load_settings()
        self.serial_reader = None
        self.zero = np.zeros(4, dtype=float)
        self.K = self._load_calibration_or_identity()
        self.record = False
        self.rec_df = pd.DataFrame(columns=["t", "V", "F1", "F2", "F3", "F4"])

        self._build_layout()

        self.resp = ResponsiveManager(self.root, fig=self.fig)

        # Auto-connect on startup
        self._auto_connect()

        if self.settings.get("show_welcome_on_start", True):
            self.open_welcome_manual()

        self.root.after(80, self._update_loop)

    # ---------- Menu ----------
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Manual", command=self.open_welcome_manual)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.root.config(menu=menubar)

    # ---------- Layout ----------
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

        # Controls
        ctrl = ttk.Frame(main)
        ctrl.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        for r in range(12):
            ctrl.rowconfigure(r, weight=0)
        ctrl.rowconfigure(12, weight=1)
        ctrl.columnconfigure(0, weight=1)
        ctrl.columnconfigure(1, weight=1)

        ttk.Label(ctrl, text="Wind Velocity:").grid(row=0, column=0, sticky="w")
        self.vel_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.vel_var, state="readonly", width=12).grid(row=0, column=1, sticky="w")

        ttk.Label(ctrl, text="Air Density:").grid(row=1, column=0, sticky="w")
        self.rho_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.rho_var, state="readonly", width=12).grid(row=1, column=1, sticky="w")

        ttk.Button(ctrl, text="Tare (Zero)", command=self._tare).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 2))
        ttk.Button(ctrl, text="Start Recording", command=self._start_record).grid(row=3, column=0, columnspan=2, sticky="ew", pady=2)
        ttk.Button(ctrl, text="Stop Recording", command=self._stop_record).grid(row=4, column=0, columnspan=2, sticky="ew", pady=2)
        ttk.Button(ctrl, text="Export CSV", command=self._export_csv).grid(row=5, column=0, columnspan=2, sticky="ew", pady=2)

        # Reset Data (graph + record buffer)
        ttk.Button(ctrl, text="Reset Data (Graph + Buffer)", command=self._reset_data).grid(row=6, column=0, columnspan=2, sticky="ew", pady=(8, 2))

        # Calibration (per sensor)
        cal_group = ttk.LabelFrame(ctrl, text="Calibration (Per Sensor, 100 g)")
        cal_group.grid(row=7, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
        for i in range(2):
            cal_group.columnconfigure(i, weight=1)

        ttk.Label(cal_group, text="Select Sensor:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.cal_choice = tk.StringVar(value=CAL_OPTIONS[0])
        cb = ttk.Combobox(cal_group, textvariable=self.cal_choice, state="readonly", values=CAL_OPTIONS)
        cb.grid(row=0, column=1, sticky="ew", padx=6, pady=4)

        self.btn_cal_start = ttk.Button(cal_group, text="Calibrate Selected", command=self._cal_start)
        self.btn_cal_start.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(4, 8))

        # Forces (N)
        mid = ttk.LabelFrame(main, text="Forces (N) — [Front Lift, Front Drag, Back Lift, Back Drag]")
        mid.grid(row=1, column=1, sticky="nsew", padx=8)
        mid.rowconfigure(0, weight=1)
        for c in range(4):
            mid.columnconfigure(c, weight=1)
        self.force_boxes = []
        for i in range(4):
            tbox = tk.Text(mid, width=14, height=24)
            tbox.grid(row=0, column=i, padx=6, sticky="nsew")
            self.force_boxes.append(tbox)

        # Graph
        right = ttk.Frame(main)
        right.grid(row=1, column=2, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        colors = ["b", "g", "r", "m"]
        self.lines = [self.ax.plot([], [], colors[i]+"-", label=lbl)[0] for i, lbl in enumerate(
            ["Front Lift", "Front Drag", "Back Lift", "Back Drag"]
        )]
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Force (N)")
        self.ax.legend()
        self.t0 = time.time()
        self.ts = []
        self.hist = [[] for _ in range(4)]

    # ---------- Auto-connect ----------
    def _auto_connect(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        for p in ports:
            sr = SerialReader(p)
            if sr.arduino and sr.arduino.is_open:
                self.serial_reader = sr
                self.port_var.set(p)
                self.status_var.set(f"✅ Auto-connected: {p} @ {BAUD}")
                return
        self.status_var.set("Status: Not connected (auto-connect failed)")

    # ---------- Welcome Manual ----------
    def open_welcome_manual(self):
        w = tk.Toplevel(self.root)
        w.title("Welcome — Wind Tunnel Manual (Front/Back)")
        w.geometry("640x540")
        w.transient(self.root)

        quick = ttk.LabelFrame(w, text="Quick Start")
        quick.pack(fill="x", padx=10, pady=(10, 6))
        lbl = ttk.Label(
            quick,
            justify="left",
            text=(
                "1) Auto-connect waits a moment; or select COM and click Connect.\n"
                "2) Tare (Zero) with nothing touching.\n"
                "3) Start Recording to log.\n"
                "4) Calibration (Per Sensor): choose Front/Back Lift/Drag → Calibrate Selected.\n"
                "   • It grabs baseline automatically, then asks you to apply 100 g and captures.\n"
                "5) Reset Data clears graph + buffer; Export CSV saves data.\n"
            )
        )
        lbl.pack(anchor="w", padx=8, pady=6)

        btns = ttk.Frame(w)
        btns.pack(fill="x", padx=10, pady=6)
        ttk.Button(btns, text="More detail…", command=self._open_full_manual).pack(side="left")

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
            "Per-Sensor Calibration\n"
            "• Select the sensor (Front Lift, Front Drag, Back Lift, Back Drag).\n"
            "• Click Calibrate Selected → the app captures BASELINE automatically (1 s).\n"
            "• It then asks you to apply a 100 g force on that sensor axis and captures LOAD (2 s).\n"
            "• The gain for that output row is updated and saved to calibration_matrix.txt.\n\n"
            "Reset Data\n"
            "• Clears graph and recording buffer, resets t=0 (does NOT change calibration or tare).\n\n"
            "Tips\n"
            "• For vertical (Lift): place 100 g centered on the platform.\n"
            "• For horizontal (Drag): use a string/pulley so the pull is level at platform height.\n"
            "• Tare again if you change fixtures or see drift.\n"
        )
        txt.insert("1.0", manual)

        if hasattr(self, "resp"):
            self.resp.attach_text_widget(txt)

    # ---------- Serial ----------
    def _refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.cmb_ports["values"] = ports
        if ports and not self.port_var.get():
            self.port_var.set(ports[0])
        return ports

    def _connect_serial(self):
        port = self.port_var.get()
        if not port:
            messagebox.showwarning("Port", "No COM port selected.")
            return
        sr = SerialReader(port)
        if sr.arduino and sr.arduino.is_open:
            if self.serial_reader:
                self.serial_reader.close()
            self.serial_reader = sr
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
        self.zero = (avg + self.zero) / 2.0  # gentle update
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

    def _reset_data(self):
        """Clear graph + recording buffer and reset time base."""
        self.ts = []
        self.hist = [[] for _ in range(4)]
        self.t0 = time.time()
        for i in range(4):
            self.lines[i].set_data([], [])
        self.ax.relim(); self.ax.autoscale_view()
        self.canvas.draw_idle()
        self.rec_df = pd.DataFrame(columns=["t", "V", "F1", "F2", "F3", "F4"])
        messagebox.showinfo("Reset", "✅ All data cleared (graph + buffer).")

    # ---------- Per-Sensor Calibration ----------
    def _cal_start(self):
        if not self.serial_reader:
            messagebox.showerror("Calibration", "Connect serial first.")
            return

        choice = self.cal_choice.get()
        if choice not in FB_INDEX:
            messagebox.showwarning("Calibration", "Select a valid sensor.")
            return

        row_idx, col_idx = FB_INDEX[choice]

        # 1) Baseline capture
        msg = (
            f"Calibrating: {choice}\n\n"
            f"Step 1: Baseline (no load) — capturing for {TARE_SEC:.1f} s…\n"
        )
        messagebox.showinfo("Calibration", msg)
        baseline = self._avg_raw_over(TARE_SEC)
        if baseline is None:
            messagebox.showerror("Calibration", "No data for baseline. Try again.")
            return

        # 2) Load capture
        if "Lift" in choice:
            instr = "Place 100 g centered on the platform (vertical)."
        else:
            instr = "Apply 100 g horizontal pull at platform height."

        msg2 = (
            f"Calibrating: {choice}\n\n"
            f"Step 2: LOAD — {instr}\n"
            f"Capturing for {CAPTURE_SEC:.1f} s once you press OK."
        )
        messagebox.showinfo("Calibration", msg2)
        load = self._avg_raw_over(CAPTURE_SEC)
        if load is None:
            messagebox.showerror("Calibration", "No data for LOAD. Try again.")
            return

        delta = load - baseline
        ch_delta = float(delta[col_idx])

        if (not np.isfinite(ch_delta)) or (abs(ch_delta) < MIN_SIGNAL):
            messagebox.showerror("Calibration", f"Signal too small/invalid on channel {col_idx+1}.")
            return

        gain = CAL_FORCE_N / ch_delta
        # Update only this output row to use this single input channel
        K_new = np.array(self.K)
        K_new[row_idx, :] = 0.0
        K_new[row_idx, col_idx] = gain

        try:
            np.savetxt(CALIB_FILE, K_new, delimiter=",")
            self.K = K_new
            messagebox.showinfo(
                "Calibration",
                f"Saved: {choice}\nGain set on input F{col_idx+1} → output row {row_idx}.\n\n"
                f"Gain = {gain:.6f} (N per raw-unit)"
            )
        except Exception as e:
            messagebox.showerror("Calibration", f"Failed to save calibration:\n{e}")

    # ---------- Live loop ----------
    def _update_loop(self):
        try:
            if self.serial_reader:
                row = self.serial_reader.get_data()
                if row:
                    self.vel_var.set(row[0])
                    self.rho_var.set(row[1])
                    Fraw = self._parse_F(row)
                    if Fraw is not None:
                        Fcorr = Fraw - self.zero
                        Fy = self.K @ Fcorr  # [Front Lift, Front Drag, Back Lift, Back Drag]

                        # Text boxes (cap lines to avoid slowdown)
                        for i, box in enumerate(self.force_boxes):
                            box.insert("1.0", f"{Fy[i]:.3f}\n")
                            if int(box.index('end-1c').split('.')[0]) > 200:
                                box.delete('200.0', 'end')

                        # Graph
                        t = time.time() - self.t0
                        self.ts.append(t)
                        for i in range(4):
                            self.hist[i].append(Fy[i])
                            if len(self.hist[i]) > 2000:
                                self.hist[i] = self.hist[i][-2000:]
                        if len(self.ts) > 2000:
                            self.ts = self.ts[-2000:]

                        for i in range(4):
                            self.lines[i].set_data(self.ts, self.hist[i])
                        self.ax.relim(); self.ax.autoscale_view()
                        self.canvas.draw_idle()

                        # Recording
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
