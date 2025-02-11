from PyQt6.QtWidgets import QGridLayout, QPushButton

class NumericKeypad:
    def __init__(self):
        self.layout = QGridLayout()
        self.buttons = []
        self._setup_keypad()
        
    def _setup_keypad(self):
        # Create number buttons 0-9
        for i in range(10):
            button = QPushButton(str(i))
            self.buttons.append(button)
            
        # Add clear button
        clear_button = QPushButton("Clear")
        self.buttons.append(clear_button)
        
        # Arrange buttons in grid
        positions = [(i, j) for i in range(4) for j in range(3)]
        for position, button in zip(positions, self.buttons):
            self.layout.addWidget(button, *position)
            
    def get_layout(self):
        return self.layout