import serial

class SerialReader:
    def __init__(self, port, baudrate=115200, timeout=0.05):
        """Initialize serial connection to Arduino."""
        self.port = port
        self.baudrate = baudrate
        self.arduino = None
        try:
            self.arduino = serial.Serial(port, baudrate=baudrate, timeout=timeout)
            print(f"✅ Connected to {port} at {baudrate} baud")
        except Exception as e:
            print(f"❌ Failed to connect on {port}: {e}")

    def get_data(self):
        """Read one line from serial, return a list of fields or None."""
        if not self.arduino or not self.arduino.is_open:
            return None
        try:
            raw = self.arduino.readline()
            if not raw:
                return None

            line = raw.decode("utf-8", errors="ignore").strip()
            if not line:
                return None

            # Skip header or text lines
            if any(word in line for word in ["WindSpeed", "Density", "Load", "Temperature"]):
                return None

            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 6:
                return None

            return parts[:6]  # Expect V, rho, F1, F2, F3, F4
        except Exception as e:
            print(f"⚠️ Serial read error: {e}")
            return None

    def close(self):
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
            print("🔌 Serial connection closed")
