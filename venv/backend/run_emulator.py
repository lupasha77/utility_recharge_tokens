# backend/run_emulator.py
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from app.meter_simulator.meter_emulator import MeterEmulator

def main():
    app = QApplication(sys.argv)
    window = MeterEmulator()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()