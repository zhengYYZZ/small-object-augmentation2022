from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os

class ToolsWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        #Tools
        self.txtToXml_btn = QPushButton('txt转xml')
        self.xmlToTxt_btn = QPushButton('xml转txt')
        self.copyXml_btn = QPushButton('第一张图XML复制为所有图片XML')
        self.addLabel_btn = QPushButton('第一张图XML最后n个标签追加到所有图片')
        self.tools_vbox = QVBoxLayout()
        self.tools_vbox.addWidget(self.txtToXml_btn)
        self.tools_vbox.addWidget(self.xmlToTxt_btn)
        self.tools_vbox.addWidget(self.copyXml_btn)
        self.tools_vbox.addWidget(self.addLabel_btn)
        # self.tools_group = QGroupBox('Tools')
        # self.tools_group.setLayout(self.tools_vbox)

        self.main_grid = QGridLayout(self)
        self.main_grid.addLayout(self.tools_vbox,0,0)

        self.setWindowTitle('Tools')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    cwidget = ToolsWidget()
    cwidget.setWindowFlags(Qt.WindowCloseButtonHint)
    cwidget.show()
    sys.exit(app.exec_())