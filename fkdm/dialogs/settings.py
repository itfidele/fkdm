from PyQt5.QtWidgets import QDialog,QPushButton,QVBoxLayout
from PyQt5 import QtCore

class SettingsDialog(QDialog):

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.initUI()
    
    def initUI(self):
        main_layout = QVBoxLayout(self)

        button_change_theme = QPushButton("Change theme",self)
        button_change_theme.clicked.connect(self.change_theme)
        self.setLayout(main_layout)
        self.show()

    
    def change_theme(self):
        pass
    
    def show(self) -> None:
        return super().show()