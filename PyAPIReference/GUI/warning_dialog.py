from PyQt5.QtWidgets import QWidget, QDialog, QLabel, QPushButton, QGridLayout, QStyle
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSize, Qt

class WarningDialog(QDialog):
	def __init__(self, title: str, text: str, yes_btn_callback: callable=1, yes_btn_text: str="Yes", no_btn_callback: callable=0, no_btn_text: str="No", icon_size: (tuple, list)=(60, 60), parent=None):
		super().__init__(parent=parent)

		self.setWindowTitle(title)
		self.setLayout(QGridLayout())
		self.setMaximumSize(0, 0)

		icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
		icon_label = QLabel()

		pixmap = QPixmap(icon.pixmap(QSize(*icon_size)))
		icon_label.setPixmap(pixmap)
		
		yes_btn = QPushButton(self.style().standardIcon(QStyle.SP_DialogApplyButton), yes_btn_text)
		yes_btn.clicked.connect(lambda: self.done(yes_btn_callback))

		no_btn = QPushButton(self.style().standardIcon(QStyle.SP_DialogCancelButton), no_btn_text)
		no_btn.clicked.connect(lambda: self.done(no_btn_callback))

		text_label = QLabel(text)
		text_label.setAlignment(Qt.AlignTop)

		self.layout().addWidget(icon_label, 0, 0)
		self.layout().addWidget(text_label, 0, 1, 0, 2)

		self.layout().addWidget(yes_btn, 1, 1)
		self.layout().addWidget(no_btn, 1, 2)
