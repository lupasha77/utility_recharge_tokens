 
# // backend/app/meter_simulator/prepaid_meter_emulator.py
import sys
from PyQt6.QtWidgets import QApplication
from meter_emulator import MeterEmulator

if __name__ == '__main__':
    app = QApplication(sys.argv)
    emulator = MeterEmulator()
    emulator.show()
    sys.exit(app.exec())