from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os

label_name = {}



class advancedWidget(QDialog):
    def __init__(self):
        super().__init__()
        # 高级设置
        
        self.numItem_label = QLabel('循环次数:')
        self.numItem_edit = QLineEdit()
        self.imgNum_label = QLabel('贴图数量:')
        self.imgNum_edit = QLineEdit()
        self.scaleBox_label = QLabel('标签框比例:')
        self.scaleBox_edit = QLineEdit()
        self.iou_label = QLabel('标签框相交系数(0.8~1.5):')
        self.iou_edit = QLineEdit()
        self.GaussianBlur_label = QLabel('高斯模糊(1,3,5,9):')
        self.GaussianBlur_edit = QLineEdit()
        self.noise_label = QLabel('高斯噪声:')
        self.noise_edit = QLineEdit()
        self.isSeamlessClone_check = QCheckBox('启用泊松融合')
        self.default_btn = QPushButton('恢复默认设置')
        self.box_btn = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # main ui
        self.main_grid = QGridLayout(self)
        self.main_grid.addWidget(self.numItem_label,0,0)
        self.main_grid.addWidget(self.numItem_edit,0,1)
        self.main_grid.addWidget(self.imgNum_label,2,0)
        self.main_grid.addWidget(self.imgNum_edit,2,1)
        self.main_grid.addWidget(self.scaleBox_label,3,0)
        self.main_grid.addWidget(self.scaleBox_edit,3,1)
        self.main_grid.addWidget(self.iou_label,4,0)
        self.main_grid.addWidget(self.iou_edit,4,1)
        self.main_grid.addWidget(self.GaussianBlur_label,5,0)
        self.main_grid.addWidget(self.GaussianBlur_edit,5,1)
        self.main_grid.addWidget(self.noise_label,6,0)
        self.main_grid.addWidget(self.noise_edit,6,1)
        self.main_grid.addWidget(self.isSeamlessClone_check,7,0,1,2)
        self.main_grid.addWidget(self.default_btn,8,0,1,2)
        self.main_grid.addWidget(self.box_btn,9,0,1,2)

        self.setWindowTitle('高级设置')

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        ### ui初始化

        # 选择前背景路径
        self.getsmall_btn = QPushButton('前景图片路径')
        self.gettrain_btn = QPushButton('背景图片路径')
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.getsmall_btn)
        self.h_box.addWidget(self.gettrain_btn)
        self.v_group = QGroupBox('设置前景背景路径')
        self.v_group.setLayout(self.h_box)

        # 设置贴图大小
        self.minLabel = QLabel('min:')
        self.maxLabel = QLabel('max:')
        self.minEdit = QLineEdit('1000')
        self.maxEdit = QLineEdit('2000')
        self.testshow_btn = QPushButton('查看贴图大小')
        self.Tools_btn = QPushButton('工具')
        self.grid_size = QGridLayout()
        self.grid_size.addWidget(self.minLabel,0,0)
        self.grid_size.addWidget(self.minEdit,0,1)
        self.grid_size.addWidget(self.maxLabel,1,0)
        self.grid_size.addWidget(self.maxEdit,1,1)
        self.grid_size.addWidget(self.testshow_btn,2,0,1,2)
        self.grid_size.addWidget(self.Tools_btn,3,0,1,2)
        self.group_size = QGroupBox('设置前景像素大小')
        self.group_size.setLayout(self.grid_size)

        # 设置标志序号
        self.prospectLabel = QLabel('设置贴图标签:')
        self.prospectComboBox = QComboBox()
        self.customLabel = QLabel('自定义标签:')
        self.customEdit = QLineEdit()
        self.isCustomCheckBox = QCheckBox('是否使用自定义标签')
        # self.num_label = QLabel('贴图数量:')
        # self.num_SBox = QSpinBox()
        self.advancedSetting_btn = QPushButton('高级设置')
        self.advancedSetting_btn.clicked.connect(lambda :self.advanced_Setting())
        self.LabelLayout = QGridLayout()
        self.LabelLayout.addWidget(self.prospectLabel,0,0)
        self.LabelLayout.addWidget(self.prospectComboBox,0,1)
        self.LabelLayout.addWidget(self.customLabel,1,0)
        self.LabelLayout.addWidget(self.customEdit,1,1)
        # self.LabelLayout.addWidget(self.num_label,2,0)
        # self.LabelLayout.addWidget(self.num_SBox,2,1)
        self.LabelLayout.addWidget(self.isCustomCheckBox,3,0,1,2)
        self.LabelLayout.addWidget(self.advancedSetting_btn,4,0,1,2)
        self.label_group = QGroupBox('设置标签')
        self.label_group.setLayout(self.LabelLayout)


        # 开始合成
        self.start_btn = QPushButton('开始合成图片')
        horiz1 = QSpacerItem(150, 30, QSizePolicy.Minimum,QSizePolicy.Expanding)
        horiz2 = QSpacerItem(150, 30, QSizePolicy.Minimum,QSizePolicy.Expanding)
        self.h_box = QHBoxLayout()
        self.h_box.addItem(horiz1)
        self.h_box.addWidget(self.start_btn)
        self.h_box.addItem(horiz2)


        # 进度条
        self.pbar  =  QProgressBar()


        # 布局
        self.main_grid = QGridLayout(self)
        self.main_grid.addWidget(self.v_group,0,0,1,2)
        self.main_grid.addWidget(self.group_size,1,0)
        # self.main_grid.addWidget(self.tools_group,0,1)
        self.main_grid.addWidget(self.label_group,1,1)
        self.main_grid.addWidget(self.pbar,2,0,1,2)
        self.main_grid.addLayout(self.h_box,3,0,1,2)
        
        # self.setFixedSize(500,300)
        self.setWindowTitle('贴图工具')

        self.res_init()

    def res_init(self):
        # 资源初始化
        pwd = os.getcwd()
        print(f'pwd={pwd}')


    def advanced_Setting(self):
        awidget = advancedWidget()
        awidget.exec_()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cwidget = MainWidget()
    cwidget.setWindowFlags(Qt.WindowCloseButtonHint)
    cwidget.show()
    sys.exit(app.exec_())