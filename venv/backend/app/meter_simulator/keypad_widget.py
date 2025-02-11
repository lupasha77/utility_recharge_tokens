from PyQt6.QtWidgets import QGridLayout, QPushButton

class KeypadWidget(QGridLayout):
    def __init__(self, token_input):
        super().__init__()
        self.token_input = token_input
        self.create_keypad()

    def create_keypad(self):
        buttons = []
        for i in range(9):
            btn = QPushButton(str(i + 1))
            btn.clicked.connect(lambda checked, num=i+1: self.keypad_pressed(str(num)))
            buttons.append(btn)
            self.addWidget(btn, i // 3, i % 3)
        
        btn_0 = QPushButton('0')
        btn_0.clicked.connect(lambda: self.keypad_pressed('0'))
        self.addWidget(btn_0, 3, 1)
        
        btn_clear = QPushButton('Clear')
        btn_clear.clicked.connect(self.clear_token_input)
        self.addWidget(btn_clear, 3, 0)
        
        btn_back = QPushButton('←')
        btn_back.clicked.connect(self.backspace_token_input)
        self.addWidget(btn_back, 3, 2)

    def keypad_pressed(self, number):
        current_text = self.token_input.text().replace('-', '')
        if len(current_text) < 16:
            current_text += number
            formatted = '-'.join([current_text[i:i+4] for i in range(0, len(current_text), 4)])
            self.token_input.setText(formatted)

    def clear_token_input(self):
        self.token_input.clear()

    def backspace_token_input(self):
        current_text = self.token_input.text().replace('-', '')
        if current_text:
            current_text = current_text[:-1]
            if current_text:
                formatted = '-'.join([current_text[i:i+4] for i in range(0, len(current_text), 4)])
                self.token_input.setText(formatted)
            else:
                self.token_input.clear()