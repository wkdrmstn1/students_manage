from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout

class MemoDialog(QDialog):
    def __init__(self, initial_text="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("특이사항 메모")
        self.setMinimumSize(300, 200)

        self.text_edit = QTextEdit()
        self.text_edit.setText(initial_text)

        self.btn_save = QPushButton("저장")
        self.btn_cancel = QPushButton("취소")

        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        button_box = QHBoxLayout()
        button_box.addStretch(1)
        button_box.addWidget(self.btn_save)
        button_box.addWidget(self.btn_cancel)

        layout = QVBoxLayout(self)
        layout.addWidget(self.text_edit)
        layout.addLayout(button_box)

    def get_text(self):
        """저장된 텍스트를 반환하는 함수"""
        return self.text_edit.toPlainText()