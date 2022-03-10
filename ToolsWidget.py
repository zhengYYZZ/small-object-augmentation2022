from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os

class ToolsQDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        #Tools
        self.txtToXml_btn = QPushButton('txt转xml')
        self.xmlToTxt_btn = QPushButton('xml转txt')
        self.copyXml_btn = QPushButton('复制XML')
        self.addLabel_btn = QPushButton('追加标签')
        self.changeLabel_btn = QPushButton('批量更改指定Label')
        self.lookup_btn = QPushButton('校对图片和xml')
        self.findLabel_btn = QPushButton('拷贝出指定标签图片')
        
        self.tools_vbox = QVBoxLayout()
        self.tools_vbox.addWidget(self.txtToXml_btn)
        self.tools_vbox.addWidget(self.xmlToTxt_btn)
        self.tools_vbox.addWidget(self.copyXml_btn)
        self.tools_vbox.addWidget(self.addLabel_btn)
        self.tools_vbox.addWidget(self.changeLabel_btn)
        self.tools_vbox.addWidget(self.lookup_btn)
        self.tools_vbox.addWidget(self.findLabel_btn)
        # self.tools_group = QGroupBox('Tools')
        # self.tools_group.setLayout(self.tools_vbox)

        self.main_grid = QGridLayout(self)
        self.main_grid.addLayout(self.tools_vbox,0,0)

        self.setWindowTitle('Tools')
        self.setFixedSize(240,300)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    cwidget = ToolsQDialog()
    cwidget.setWindowFlags(Qt.WindowCloseButtonHint)
    cwidget.show()
    sys.exit(app.exec_())