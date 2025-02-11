from PyQt6.QtWidgets import QLCDNumber
from PyQt6.QtCore import Qt

class MeterDisplay(QLCDNumber):
    def __init__(self, parent=None):
        super().__init__(8, parent)
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.setStyleSheet("background-color: #000; color: #00ff00;")
        
    def update_value(self, value):
        self.display(f"{float(value):.2f}")