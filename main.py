from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
from configparser import ConfigParser
import cv2
import numpy as np
from tqdm import tqdm
import json

import sys
sys.path.append('api_core')
from api_core import util
from api_core import Helpers as hp
from api_core import augment as aug
from api_core import xmlcontrol as voc_xml

classes_name = util.read_classes_txt('data/predefined_classes.txt')


class advancedWidget(QDialog):
    def __init__(self):
        super().__init__()
        # 高级设置

        self.numItem_label = QLabel('循环次数:')
        self.numItem_edit = QLineEdit()
        self.numItem_edit.setValidator(QIntValidator())
        self.imgNum_label = QLabel('贴图数量:')
        self.imgNum_edit = QLineEdit()
        self.imgNum_edit.setValidator(QIntValidator())
        self.scaleBox_label = QLabel('标签框比例(0.8~1.5):')
        self.scaleBox_edit = QLineEdit()
        self.scaleBox_edit.setValidator(QDoubleValidator())
        self.iou_label = QLabel('标签框相交系数(0~1):')
        self.iou_edit = QLineEdit()
        self.iou_edit.setValidator(QDoubleValidator())
        self.GaussianBlur_label = QLabel('高斯模糊(0或单数):')
        self.GaussianBlur_edit = QLineEdit()
        self.GaussianBlur_edit.setValidator(QIntValidator())
        self.noise_label = QLabel('高斯噪声:')
        self.noise_edit = QLineEdit()
        self.noise_edit.setValidator(QIntValidator())
        self.isSeamlessClone_check = QCheckBox('启用泊松融合')
        self.default_btn = QPushButton('恢复默认设置')
        self.default_btn.clicked.connect(lambda: self.default_click())
        self.box_btn = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.box_btn.accepted.connect(lambda: self.clicked_ok())
        self.box_btn.rejected.connect(lambda: self.dlg_close())

        # main ui
        self.main_grid = QGridLayout(self)
        self.main_grid.addWidget(self.numItem_label, 0, 0)
        self.main_grid.addWidget(self.numItem_edit, 0, 1)
        self.main_grid.addWidget(self.imgNum_label, 2, 0)
        self.main_grid.addWidget(self.imgNum_edit, 2, 1)
        self.main_grid.addWidget(self.scaleBox_label, 3, 0)
        self.main_grid.addWidget(self.scaleBox_edit, 3, 1)
        self.main_grid.addWidget(self.iou_label, 4, 0)
        self.main_grid.addWidget(self.iou_edit, 4, 1)
        self.main_grid.addWidget(self.GaussianBlur_label, 5, 0)
        self.main_grid.addWidget(self.GaussianBlur_edit, 5, 1)
        self.main_grid.addWidget(self.noise_label, 6, 0)
        self.main_grid.addWidget(self.noise_edit, 6, 1)
        self.main_grid.addWidget(self.isSeamlessClone_check, 7, 0, 1, 2)
        self.main_grid.addWidget(self.default_btn, 8, 0, 1, 2)
        self.main_grid.addWidget(self.box_btn, 9, 0, 1, 2)

        self.setWindowTitle('高级设置')

        self.res_init()

    def default_click(self):
        self.numItem_edit.setText('1')
        self.imgNum_edit.setText('1')
        self.scaleBox_edit.setText('1.1')
        self.iou_edit.setText('0')
        self.GaussianBlur_edit.setText('0')
        self.noise_edit.setText('0')
        self.isSeamlessClone_check.setChecked(True)

    def res_init(self):
        # 资源初始化
        config = ConfigParser()
        config.read("config.ini")
        self.numItem_edit.setText(config.get("advanced", "numItem"))
        self.imgNum_edit.setText(config.get("advanced", "imgNum"))
        self.scaleBox_edit.setText(config.get("advanced", "scaleBox"))
        self.iou_edit.setText(config.get("advanced", "iou"))
        self.GaussianBlur_edit.setText(config.get("advanced", "GaussianBlur"))
        self.noise_edit.setText(config.get("advanced", "noise"))
        if config.getint("advanced", "isSeamlessClone") == 1:
            self.isSeamlessClone_check.setChecked(True)
        else:
            self.isSeamlessClone_check.setChecked(False)

    def clicked_ok(self):
        config = ConfigParser()
        config.read('config.ini')
        # config.add_section('advanced')
        config.set('advanced', 'numItem', self.numItem_edit.text())
        config.set('advanced', 'imgNum', self.imgNum_edit.text())
        config.set('advanced', 'scaleBox', self.scaleBox_edit.text())
        config.set('advanced', 'iou', self.iou_edit.text())
        config.set('advanced', 'GaussianBlur', self.GaussianBlur_edit.text())
        config.set('advanced', 'noise', self.noise_edit.text())
        if self.isSeamlessClone_check.isChecked() == True:
            config.set('advanced', 'isSeamlessClone', "1")
        else:
            config.set('advanced', 'isSeamlessClone', "0")
        config.write(open('config.ini', 'w+'))

        self.close()

    def dlg_close(self):
        self.close()


class sizeDlg(QDialog):
    def __init__(self):
        super().__init__()

        self.comboBox = QComboBox()
        self.comboBox.currentIndexChanged.connect(lambda: self.selecLabel())
        self.l_label = QLabel('备注:')
        self.l_edit = QLineEdit()
        self.max_label = QLabel('max:')
        self.max_edit = QLineEdit()
        self.max_edit.setValidator(QIntValidator())
        self.min_label = QLabel('min')
        self.min_edit = QLineEdit()
        self.min_edit.setValidator(QIntValidator())
        self.add_btn = QPushButton('添加/修改')
        self.add_btn.clicked.connect(lambda: self.add_click())
        self.delete_btn = QPushButton('删除')
        self.delete_btn.clicked.connect(lambda: self.delete_click())
        self.use_btn = QPushButton('使用该预设')
        self.use_btn.clicked.connect(lambda : self.use_click())

        self.main_gird = QGridLayout(self)
        self.main_gird.addWidget(self.comboBox,0,0,1,2)
        self.main_gird.addWidget(self.l_label,1,0)
        self.main_gird.addWidget(self.l_edit,1,1)
        self.main_gird.addWidget(self.min_label,2,0)
        self.main_gird.addWidget(self.min_edit,2,1)
        self.main_gird.addWidget(self.max_label,3,0)
        self.main_gird.addWidget(self.max_edit,3,1)
        self.main_gird.addWidget(self.add_btn,4,0)
        self.main_gird.addWidget(self.delete_btn,4,1)
        self.main_gird.addWidget(self.use_btn,5,0,1,2)

        self._data_dict = {}
        self.isUse = False
        self.res_init()

    def res_init(self):
        self._data_dict.clear()
        with open('data/YuSheSize.json','r+') as f:
            json_load = json.load(f)
            self._data_dict = json.loads(json_load)

        self.comboBox.clear()
        for key,value in self._data_dict.items():
            print(key)
            print(value)
            self.comboBox.addItem(f'{key} {value}')

    def selecLabel(self):
        # 下拉框
        combox_str = self.comboBox.currentText()
        if not combox_str == '':
            min_str = self._data_dict[combox_str.split(' ')[0]][0]
            max_str = self._data_dict[combox_str.split(' ')[0]][1]
            self.l_edit.setText(combox_str.split(' ')[0])
            self.min_edit.setText(f'{min_str}')
            self.max_edit.setText(f'{max_str}')
        else:
            self.l_edit.setText('')
            self.min_edit.setText('')
            self.max_edit.setText('')

    def add_click(self):
        label_str = self.l_edit.text()
        max_str = self.max_edit.text()
        min_str = self.min_edit.text()
        if label_str == '':
            QMessageBox.warning(self,'warning','数据不规范',QMessageBox.Ok)
            return

        self._data_dict[label_str] = [int(min_str),int(max_str)]
        with open('data/YuSheSize.json','w+') as f:
            json_str = json.dumps(self._data_dict)
            json.dump(json_str,f)
        self.res_init()

    def delete_click(self):
        label_str = self.l_edit.text()
        if label_str == '' or len(self._data_dict)==0:
            QMessageBox.warning(self,'error','无数据可删除',QMessageBox.Ok)
            return

        self._data_dict.pop(label_str)
        with open('data/YuSheSize.json','w+') as f:
            json_str = json.dumps(self._data_dict)
            json.dump(json_str,f)
        self.res_init()
    
    def use_click(self):
        self.isUse = True
        self.close()

    def is_use(self):
        return self.isUse

    def get_min_max(self):
        min_str = self.min_edit.text()
        max_str = self.max_edit.text()
        if min_str=='' or max_str=='':
            return '100','1000'
        return min_str,max_str



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
        self.gettrain_btn.clicked.connect(lambda: self.open_train_btn())
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.getsmall_btn)
        self.h_box.addWidget(self.gettrain_btn)
        self.v_group = QGroupBox('设置前景背景路径')
        self.v_group.setLayout(self.h_box)

        # 设置贴图大小
        self.minLabel = QLabel('min:')
        self.maxLabel = QLabel('max:')
        self.minEdit = QLineEdit()
        self.minEdit.setValidator(QIntValidator())
        self.maxEdit = QLineEdit()
        self.maxEdit.setValidator(QIntValidator())
        self.testshow_btn = QPushButton('查看贴图大小')
        self.testshow_btn.clicked.connect(lambda: self.testshow_btn_click())
        self.Tools_btn = QPushButton('预设前景大小')
        self.Tools_btn.clicked.connect(lambda: self.tools_btn_clicked())
        self.grid_size = QGridLayout()
        self.grid_size.addWidget(self.minLabel, 1, 0)
        self.grid_size.addWidget(self.minEdit, 1, 1)
        self.grid_size.addWidget(self.maxLabel, 2, 0)
        self.grid_size.addWidget(self.maxEdit, 2, 1)
        self.grid_size.addWidget(self.testshow_btn, 3, 0, 1, 2)
        self.grid_size.addWidget(self.Tools_btn, 0, 0, 1, 2)
        self.group_size = QGroupBox('设置前景像素大小')
        self.group_size.setLayout(self.grid_size)

        # 设置标志序号
        self.prospectLabel = QLabel('设置贴图标签:')
        self.prospectComboBox = QComboBox()
        self.prospectComboBox.currentIndexChanged.connect(lambda: self.selectionchange())
        self.customLabel = QLabel('自定义标签:')
        self.customEdit = QLineEdit()
        self.isCustomCheckBox = QCheckBox('是否使用自定义标签')
        # self.num_label = QLabel('贴图数量:')
        # self.num_SBox = QSpinBox()
        self.advancedSetting_btn = QPushButton('高级设置')
        self.advancedSetting_btn.clicked.connect(lambda: self.advanced_Setting())
        self.LabelLayout = QGridLayout()
        self.LabelLayout.addWidget(self.prospectLabel, 0, 0)
        self.LabelLayout.addWidget(self.prospectComboBox, 0, 1)
        self.LabelLayout.addWidget(self.customLabel, 1, 0)
        self.LabelLayout.addWidget(self.customEdit, 1, 1)
        # self.LabelLayout.addWidget(self.num_label,2,0)
        # self.LabelLayout.addWidget(self.num_SBox,2,1)
        self.LabelLayout.addWidget(self.isCustomCheckBox, 3, 0, 1, 2)
        self.LabelLayout.addWidget(self.advancedSetting_btn, 4, 0, 1, 2)
        self.label_group = QGroupBox('设置标签')
        self.label_group.setLayout(self.LabelLayout)

        # 开始合成
        self.start_btn = QPushButton('开始合成图片')
        self.start_btn.clicked.connect(lambda: self.open_Aug_img_btn())
        horiz1 = QSpacerItem(150, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)
        horiz2 = QSpacerItem(150, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.h_box = QHBoxLayout()
        self.h_box.addItem(horiz1)
        self.h_box.addWidget(self.start_btn)
        self.h_box.addItem(horiz2)

        # 进度条
        self.pbar = QProgressBar()

        # 布局
        self.main_grid = QGridLayout(self)
        self.main_grid.addWidget(self.v_group, 0, 0, 1, 2)
        self.main_grid.addWidget(self.group_size, 1, 0)
        # self.main_grid.addWidget(self.tools_group,0,1)
        self.main_grid.addWidget(self.label_group, 1, 1)
        self.main_grid.addWidget(self.pbar, 2, 0, 1, 2)
        self.main_grid.addLayout(self.h_box, 3, 0, 1, 2)

        # self.setFixedSize(500,300)
        self.setWindowTitle('贴图工具')

    def testshow_btn_click(self):
        # 查看图片大小
        self.write_ini()
        save_dir, bg_img_dir, bg_label_dir, fg_img_dir = self.set_path('data/train.txt', 'data/small.txt', 'save')
        box = self.draw_background_batch(bg_img_dir)
        # 读取config.ini
        config = ConfigParser()
        config.read("config.ini")
        numitem = config.getint("advanced", "numitem")
        iscustom = config.getint("label", "iscustom")
        custom = 'car'
        if iscustom == 1:
            custom = config.get("label", "custom")
        else:
            custom = self.prospectComboBox.currentText()
        for bb, bg_label in tqdm(zip(box, bg_label_dir)):
            img, _ = aug.synthetic_image(bb[0], bg_label, bb[1], fg_img_dir, custom)
            img_h, img_w, _ = img.shape
            img = cv2.resize(img,(img_w//2,img_h//2))
            cv2.imshow('test',img)
            break
        cv2.waitKey(100)

    def write_ini(self):
        config = ConfigParser()
        config.read('config.ini')
        # config.add_section('imageSize')
        config.set('imageSize', 'max', self.maxEdit.text())
        config.set('imageSize', 'min', self.minEdit.text())

        # config.add_section('label')
        if self.isCustomCheckBox.isChecked() == True:
            config.set('label', 'isCustom', "1")
        else:
            config.set('label', 'isCustom', "0")
        config.set('label', 'custom', self.customEdit.text())
        config.write(open('config.ini', 'w+'))

    def res_init(self):
        # 资源初始化
        # pwd = os.getcwd()
        # print(f'pwd={pwd}')
        util.check_dir('data')

        # 读取config.ini
        config = ConfigParser()
        config.read("config.ini")
        self.maxEdit.setText(config.get("imageSize", "max"))
        self.minEdit.setText(config.get("imageSize", "min"))
        if config.getint('label', 'isCustom') == 0:
            self.isCustomCheckBox.setChecked(False)
        else:
            self.isCustomCheckBox.setChecked(True)
        self.customEdit.setText(config.get('label', 'custom'))

        # 下拉框添加classes
        global classes_name
        for key in classes_name:
            # print(key)
            self.prospectComboBox.addItem(key)

    def selectionchange(self):
        print(f'{self.prospectComboBox.currentText()}')

    def open_train_btn(self):
        # 设置背景图片
        dir_name = QFileDialog.getExistingDirectory(self, "请选择背景图片路径")
        bak_list = []
        if dir_name != '':
            files = os.listdir(dir_name)
            for file_path in files:
                if os.path.splitext(file_path)[1] == '.jpg':
                    bak_list.append(os.path.join(dir_name, file_path))
            bak_list.sort()
            print(bak_list)
            self.writeTxt('data/train.txt', bak_list)

    def open_small_btn(self):
        # 设置前景图片
        dir_name = QFileDialog.getExistingDirectory(self, "选择前景图片文件夹")
        files_list = []
        if dir_name != '':
            files = os.listdir(dir_name)
            for file_path in files:
                # if os.path.splitext(file_path)[1] == '.jpg':
                #     files_list.append(os.path.join(dir_name, file_path))
                files_list.append(os.path.join(dir_name, file_path))
            files_list.sort()
            print(files_list)
            self.writeTxt('data/small.txt', files_list)

    def advanced_Setting(self):
        # 高级设置
        awidget = advancedWidget()
        awidget.exec_()

    def tools_btn_clicked(self):
        # 预设
        dlg = sizeDlg()
        dlg.exec_()
        if dlg.is_use():
            min_str,max_str = dlg.get_min_max()
            self.minEdit.setText(min_str)
            self.maxEdit.setText(max_str)

    def open_Aug_img_btn(self):
        # 合成图片
        self.write_ini()

        save_dir, bg_img_dir, bg_label_dir, fg_img_dir = self.set_path('data/train.txt', 'data/small.txt', 'save')
        box = self.draw_background_batch(bg_img_dir)
        i = 0
        # 读取config.ini
        config = ConfigParser()
        config.read("config.ini")
        numitem = config.getint("advanced", "numitem")
        iscustom = config.getint("label", "iscustom")
        l_count = config.getint("label","count")
        if iscustom == 1:
            custom = config.get("label", "custom")
        else:
            custom = self.prospectComboBox.currentText()

        # 创建文件夹
        save_dir_count = os.path.join(save_dir,f'{custom}_{l_count}')
        util.check_dir(save_dir_count)

        for k in range(numitem):
            for bb, bg_label in tqdm(zip(box, bg_label_dir)):
                img, label = aug.synthetic_image(bb[0], bg_label, bb[1], fg_img_dir, custom)
                label_xml_name = os.path.join(save_dir_count,
                                              os.path.basename(bb[0].replace('.jpg', '_augment' + str(i) + '.xml')))
                img_file_name = os.path.join(save_dir_count,
                                             os.path.basename(bb[0].replace('.jpg', '_augment' + str(i) + '.jpg')))
                cv2.imwrite(img_file_name, img)
                voc_xml.creat_xml(label_xml_name, label, img_file_name, img.shape)
                self.pbar.setValue(int((i+1)/(len(box)*numitem)*100))  # 更新进度条
                i += 1

                # look
                cv2.imshow('look-img',img)
                cv2.waitKey(1)
                
        l_count += 1
        if l_count == 65535:
            l_count = 0
        # 计数写入
        config2 = ConfigParser()
        config2.read('config.ini')
        config2.set("label","count",str(l_count))
        config2.write(open('config.ini','w+'))


    def set_path(self, bg='data/train.txt', fg='data/small.txt', save_path='save'):
        '''

        :param bg:
        :param fg:
        :param save_path:
        :return: save_base_dir=保存文件夹,img_dir=背景图path,labels_xml=背景图标签,small_img_dir=前景图path
        '''
        base_dir = os.getcwd()
        save_base_dir = os.path.join(base_dir, save_path)
        util.check_dir(save_base_dir)
        img_dir = [f.strip() for f in
                   open(os.path.join(base_dir, bg), encoding='utf-8').readlines()]  # 读取train.txt文件内容，背景图片
        label_xml = []
        for img_p in img_dir:
            label_xml.append(img_p.replace('.jpg', '.txt'))
        small_img_dir = [f.strip() for f in
                         open(os.path.join(base_dir, fg), encoding='utf-8').readlines()]  # 读取small.txt文件内容，前景图片
        return save_base_dir, img_dir, label_xml, small_img_dir

    def draw_background_batch(self, path_list):
        box_list = []
        box = path_list[0]
        # img = cv2.imread(box)
        img = cv2.imdecode(np.fromfile(box, dtype=np.uint8), 1)  # 支持中文路径
        img_h, img_w, _ = img.shape
        img = cv2.resize(img, (img_w // 2, img_h // 2))
        roi = hp.draw_roi(img)
        roi = roi * 2
        for back_img_path in path_list:
            box_list.append([back_img_path, roi])
        return box_list

    def writeTxt(self, file_name, text_list):
        with open(file_name, 'w', encoding='utf-8') as f:
            for text in text_list:
                f.write(text + '\n')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    cwidget = MainWidget()
    cwidget.setWindowFlags(Qt.WindowCloseButtonHint)
    cwidget.show()
    sys.exit(app.exec_())
