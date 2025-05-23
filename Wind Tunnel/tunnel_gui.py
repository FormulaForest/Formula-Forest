'''
TODO:

1) Graph all readings
2) Buttons to switch between different graph mods
'''

from serial_reader import SerialReader

import pandas as pd
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class TunnelGUI:
    def __init__(self, root, sr):
        """Initializes GUI."""
        self.root = root
        self.root.title("Win Tunnel")
        self.root.geometry("1300x450")

        self.root.tk.call('tk', 'scaling', 1.5)

        self.serial_reader = sr
        self.record = False

        try:
            self.calib_matrix = np.loadtxt("calibration_matrix.txt")
            self.calibrated = True
        except:
            self.calib_matrix = np.identity(4)
            self.calibrated = False

        print(self.calib_matrix)
        self.last_raw_forces = [0,0,0,0]

        # --- Wind velocity ---
        ttk.Label(root, text="Wind velocity:").place(x=30, y=150)
        self.velocity_val = tk.StringVar()
        self.velocity_entry = ttk.Entry(root, state='readonly', textvariable=self.velocity_val)
        self.velocity_entry.place(x=130, y=150, width=100)

        # --- Wind density ---
        ttk.Label(root, text="Wind density:").place(x=30, y=190)
        self.density_val = tk.StringVar()
        self.density_entry = ttk.Entry(root, state='readonly', textvariable=self.density_val)
        self.density_entry.place(x=130, y=190, width=100)

        # --- Force Output Text ---
        self.output_label = ttk.Label(root, text="Force output (N):")
        if not self.calibrated:
            self.output_label.config(text="Force output (uncalibrated):")
        self.output_label.place(x=350, y=10)

        # self.output_text = tk.Text(root, wrap='word', width=40, height=18, state='normal')
        self.output_texts = []
        for i in range(4):
            output_text = tk.Text(root, wrap='word', width=10, height=18, state='normal')
            output_text.place(x=350 + i * 80, y=30)
            self.output_texts.append(output_text)

        # --- Export Button ---
        self.export_button = ttk.Button(root, text="Export CSV", command=self.export_csv)
        self.export_button.place(x=650, y=350)

        # --- Start Record Button ---
        self.start_button = ttk.Button(root, text="Start Recording Data", command=self.start_record)
        self.start_button.place(x=350, y=350)

        # --- Stop Record Button ---
        self.stop_button = ttk.Button(root, text="Stop Recording Data", command=self.stop_record)
        self.stop_button.place(x=500, y=350)

        # --- Calibration Button ---
        self.calibrate_button = ttk.Button(root, text="Calibrate", command=self.start_calibration)
        self.calibrate_button.place(x=130, y=250)

        # --- Graph Section ---
        self.fig, self.ax = plt.subplots(figsize=(4, 3))
        self.graph_canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.graph_canvas.get_tk_widget().place(x=750, y=30)
        self.ax.set_title("Force Over Time")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Force")
        self.line, = self.ax.plot([], [], 'b-')  # blue line

        # On exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def update_values(self):
        """Constantly checks serial for new data and displays it"""
        data = self.serial_reader.get_data()
        if data:
            # print(data)
            if len(data) == 6:

                self.velocity_val.set(data[0])
                self.density_val.set(data[1])

                # Patching the data (questionable approach)
                for i in range(2, 6):
                    if data[i] == "0" or data[i] == 0:
                        data[i] = self.last_raw_forces[i-2]
                    else:
                        data[i] = float(data[i])
                        self.last_raw_forces[i-2] = data[i]

                raw_forces = np.array(data[2:6], dtype=float)  # F1 to F4 raw
                calibrated_forces = np.dot(self.calib_matrix, raw_forces)

                tag = "normal"
                for i, text in enumerate(self.output_texts):
                    if self.record:
                        tag = "yellow"
                        text.tag_config("yellow", background="yellow")
                    else:
                        text.tag_config("normal", background="white")
                    text.insert("1.0", f"{calibrated_forces[i]:.2f}\n", tag)
                if self.record:
                    time_rounded = round(time.time() - self.start_time, 2)
                    # Replace 0s with np.nan for force columns (F1-F4)
                    calibrated_forces = [str(f) for f in calibrated_forces]
                    self.data.loc[len(self.data)] = [str(time_rounded)] + [data[0]] + calibrated_forces
        root.after(1, self.update_values)

    def start_record(self):
        self.data = pd.DataFrame(columns=["T", "V", "F1", "F2", "F3", "F4"])
        self.start_time = time.time()
        self.record = True

    def stop_record(self):
        self.record = False

    # def stop_record(self):

    def export_csv(self):
        if self.data.empty:
            messagebox.showwarning("Warning", "You have to start recording the data first!")
            return

        self.record = False

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save data as..."
        )
        if filepath:
            try:
                self.data.to_csv(filepath, index=False)
                print(f"Data exported to {filepath}")
            except Exception as e:
                print(f"Failed to export: {e}")
        else:
            print("Export cancelled.")

    def start_calibration(self):
        if self.calibrated:
            formatted_rows = [
            "  [ " + "  ".join(f"{val: .3e}" for val in row) + " ]"
            for row in self.calib_matrix
        ]
            # Combine with brackets
            calib_str = "\n".join(formatted_rows)
            overwrite = messagebox.askyesno(
                "Overwrite Calibration?",
                f"A calibration matrix already exists:\n\n{calib_str}\n\nDo you want to overwrite it?"
            )
            if not overwrite:
                return  # Cancel if user doesn't want to overwrite

        # Proceed to calibration window
        self.open_calibration_window()

    def open_calibration_window(self):
        self.calib_window = tk.Toplevel(self.root)
        self.calib_window.title("Calibration")
        self.calib_window.geometry("400x200")
        self.calib_step = 0
        self.calib_matrix = []

        self.instruction_label = ttk.Label(self.calib_window, text="Step 1: Apply 1 N to Load Cell 1 and press 'Record'")
        self.instruction_label.pack(pady=20)

        self.record_button = ttk.Button(self.calib_window, text="Record", command=self.record_calibration_step)
        self.record_button.pack()

        self.finish_button = ttk.Button(self.calib_window, text="Finish & Save", command=self.finish_calibration, state='disabled')
        self.finish_button.pack(pady=10)

    def record_calibration_step(self):
        # Grab current force readings from load cells (e.g., latest serial_reader data)
        self.start_record()
        # Add a waiting message
        self.calib_window.after(1000, self.finish_recording)
        # self.calib_window.update()
    
    def finish_recording(self):
        self.stop_record()
        # Calculate average and std for each force column
        force_cols = ["F1", "F2", "F3", "F4"]
        raw_data = []
        for col in force_cols:
            avg = self.data[col].astype(float).mean()
            std = self.data[col].astype(float).std()
            raw_data.append(avg)
            print(f"{col}: avg={avg:.4f}, std={std:.4f}")
        time.sleep(1)
        # print(f"Step {self.calib_step + 1}: {raw_data}")
        self.calib_matrix.append(raw_data)

        self.calib_step += 1
        if self.calib_step < 4:
            self.instruction_label.config(text=f"Step {self.calib_step + 1}: Apply 1 N to Load Cell {self.calib_step + 1} and press 'Record'")
        else:
            self.instruction_label.config(text="Done! Click 'Finish & Save'")
            self.record_button.config(state='disabled')
            self.finish_button.config(state='normal')

    def finish_calibration(self):
        matrix = np.array(self.calib_matrix)
        print("Calibration matrix:\n", matrix)
        calibration_matrix = np.linalg.inv(matrix)

        # Save to txt file
        np.savetxt("calibration_matrix.txt", calibration_matrix, delimiter=",")
        self.calib_window.destroy()

    def on_exit(self):
        self.serial_reader.close()
        self.root.destroy()  # Closes the Tkinter window

# --- Run GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    sr = SerialReader("COM5", 9600) # change this to your COM port
    app = TunnelGUI(root, sr)

    app.update_values()
    root.mainloop()