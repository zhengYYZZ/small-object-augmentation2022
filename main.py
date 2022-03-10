from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os
from configparser import ConfigParser
import sys
sys.path.append('api_core')
from api_core import util
import ToolsWidget

label_name = {}


class advancedWidget(QDialog):
    def __init__(self):
        super().__init__()
        # 高级设置
        
        self.numItem_label = QLabel('循环次数:')
        self.numItem_edit = QLineEdit()
        self.imgNum_label = QLabel('贴图数量:')
        self.imgNum_edit = QLineEdit()
        self.scaleBox_label = QLabel('标签框比例(0.8~1.5):')
        self.scaleBox_edit = QLineEdit()
        self.iou_label = QLabel('标签框相交系数(0~1):')
        self.iou_edit = QLineEdit()
        self.GaussianBlur_label = QLabel('高斯模糊(1,3,5,9):')
        self.GaussianBlur_edit = QLineEdit()
        self.noise_label = QLabel('高斯噪声:')
        self.noise_edit = QLineEdit()
        self.isSeamlessClone_check = QCheckBox('启用泊松融合')
        self.default_btn = QPushButton('恢复默认设置')
        self.default_btn.clicked.connect(lambda:self.default_click())
        self.box_btn = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.box_btn.accepted.connect(lambda:self.clicked_ok())
        self.box_btn.rejected.connect(lambda:self.dlg_close())

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

        self.res_init()

    def default_click(self):
        self.numItem_edit.setText('1')
        self.imgNum_edit.setText('1')
        self.scaleBox_edit.setText('1.1')
        self.iou_edit.setText('1')
        self.GaussianBlur_edit.setText('0')
        self.noise_edit.setText('0')
        self.isSeamlessClone_check.setChecked(True)

    def res_init(self):
        # 资源初始化
        config = ConfigParser()
        config.read("config.ini")
        self.numItem_edit.setText(config.get("advanced","numItem"))
        self.imgNum_edit.setText(config.get("advanced","imgNum"))
        self.scaleBox_edit.setText(config.get("advanced","scaleBox"))
        self.iou_edit.setText(config.get("advanced","iou"))
        self.GaussianBlur_edit.setText(config.get("advanced","GaussianBlur"))
        self.noise_edit.setText(config.get("advanced","noise"))
        if config.getint("advanced","isSeamlessClone") == 1:
            self.isSeamlessClone_check.setChecked(True)
        else:
            self.isSeamlessClone_check.setChecked(False)
    
    def clicked_ok(self):
        config = ConfigParser()
        config.read('config.ini')
        # config.add_section('advanced')
        config.set('advanced','numItem',self.numItem_edit.text())
        config.set('advanced','imgNum',self.imgNum_edit.text())
        config.set('advanced','scaleBox',self.scaleBox_edit.text())
        config.set('advanced','iou',self.iou_edit.text())
        config.set('advanced','GaussianBlur',self.GaussianBlur_edit.text())
        config.set('advanced','noise',self.noise_edit.text())
        if self.isSeamlessClone_check.isChecked() == True:
            config.set('advanced','isSeamlessClone',"1")
        else:
            config.set('advanced','isSeamlessClone',"0")
        config.write(open('config.ini','w+'))

        self.close()
    
    def dlg_close(self):
        self.close()


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        ### ui初始化
        self.ui_init()

        self.res_init()

    def ui_init(self):
        # ui 初始化

        # 选择前背景路径
        self.getsmall_btn = QPushButton('前景图片路径')
        self.getsmall_btn.clicked.connect(lambda: self.open_small_btn())
        self.gettrain_btn = QPushButton('背景图片路径')
        self.gettrain_btn.clicked.connect(lambda :self.open_train_btn())
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.getsmall_btn)
        self.h_box.addWidget(self.gettrain_btn)
        self.v_group = QGroupBox('设置前景背景路径')
        self.v_group.setLayout(self.h_box)

        # 设置贴图大小
        self.minLabel = QLabel('min:')
        self.maxLabel = QLabel('max:')
        self.minEdit = QLineEdit()
        self.maxEdit = QLineEdit()
        self.testshow_btn = QPushButton('查看贴图大小')
        self.testshow_btn.clicked.connect(lambda :self.testshow_btn_click())
        self.Tools_btn = QPushButton('工具')
        self.Tools_btn.clicked.connect(lambda:self.tools_btn_clicked())
        self.grid_size = QGridLayout()
        self.grid_size.addWidget(self.minLabel,1,0)
        self.grid_size.addWidget(self.minEdit,1,1)
        self.grid_size.addWidget(self.maxLabel,2,0)
        self.grid_size.addWidget(self.maxEdit,2,1)
        self.grid_size.addWidget(self.testshow_btn,3,0,1,2)
        self.grid_size.addWidget(self.Tools_btn,0,0,1,2)
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
        self.start_btn.clicked.connect(lambda:self.open_Aug_img_btn())
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
    
    def testshow_btn_click(self):
        # 查看图片大小
        self.write_ini()

    def write_ini(self):
        config = ConfigParser()
        config.read('config.ini')
        # config.add_section('imageSize')
        config.set('imageSize','max',self.maxEdit.text())
        config.set('imageSize','min',self.minEdit.text())
        
        # config.add_section('label')
        if self.isCustomCheckBox.isChecked() == True:
            config.set('label','isCustom',"1")
        else:
            config.set('label','isCustom',"0")
        config.set('label','custom',self.customEdit.text())
        config.write(open('config.ini','w+'))

    def res_init(self):
        # 资源初始化
        # pwd = os.getcwd()
        # print(f'pwd={pwd}')
        util.check_dir('data')

        # 读取config.ini
        config = ConfigParser()
        config.read("config.ini")
        self.maxEdit.setText(config.get("imageSize","max"))
        self.minEdit.setText(config.get("imageSize","min"))
        if config.getint('label','isCustom') == 0:
            self.isCustomCheckBox.setChecked(False)
        else:
            self.isCustomCheckBox.setChecked(True)
        self.customEdit.setText(config.get('label','custom'))

    def open_train_btn(self):
        # 设置背景图片
        dir_name = QFileDialog.getExistingDirectory(self,"请选择背景图片路径")
        bak_list = []
        if dir_name != '':
            files = os.listdir(dir_name)
            for file_path in files:
                if os.path.splitext(file_path)[1] == '.jpg':
                    bak_list.append(os.path.join(dir_name,file_path))
            bak_list.sort()
            print(bak_list)
            self.writeTxt('data/train.txt',bak_list)

    def open_small_btn(self):
        # 设置前景图片
        dir_name = QFileDialog.getExistingDirectory(self, "选择前景图片文件夹")
        files_list = []
        if dir_name != '':
            files = os.listdir(dir_name)
            for file_path in files:
                if os.path.splitext(file_path)[1] == '.jpg':
                    files_list.append(os.path.join(dir_name, file_path))
            files_list.sort()
            print(files_list)
            self.writeTxt('data/small.txt',files_list)


    def advanced_Setting(self):
        # 高级设置
        awidget = advancedWidget()
        awidget.exec_()

    def tools_btn_clicked(self):
        # 工具
        dlg = ToolsWidget.ToolsQDialog()
        dlg.exec_()

    def open_Aug_img_btn(self):
        # 合成图片
        self.write_ini()

    def writeTxt(self,file_name,text_list):
        with open(file_name,'w',encoding='utf-8') as f:
            for text in text_list:
                f.write(text+'\n')
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cwidget = MainWidget()
    cwidget.setWindowFlags(Qt.WindowCloseButtonHint)
    cwidget.show()
    sys.exit(app.exec_())