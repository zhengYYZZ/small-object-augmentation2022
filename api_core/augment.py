import random
import os
from configparser import ConfigParser
import cv2
import numpy as np
import Helpers as hp
import util
import xmlcontrol as voc_xml


def flip_bbox(roi):
    roi = roi[:, ::-1, :]
    return roi


def add_noise_single_channel(single):
    """
    高斯噪声
    :param single:
    :return:
    """
    diff = 255 - single.max()
    noise = np.random.normal(0, 1 + hp.r(6), single.shape)
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    noise = diff * noise
    noise = noise.astype(np.uint8)
    dst = single + noise
    return dst


def add_noise(img, sdev=0.5, avg=10):
    img[:, :, 0] = add_noise_single_channel(img[:, :, 0])
    img[:, :, 1] = add_noise_single_channel(img[:, :, 1])
    img[:, :, 2] = add_noise_single_channel(img[:, :, 2])
    return img


def save_label_txt(img_shape, img_label, save_file):
    """
    将标签信息转换为yolo格式,并保存
    :param img_shape:图片形状长宽
    :param img_label:标签
    :param save_file:保存文件名
    :return:
    """
    height, width, _ = img_shape
    height = height
    width = width
    label_file = open(save_file, 'w')
    for label in img_label:
        target_id, x1, y1, x2, y2 = label
        label_box = (float(x1), float(x2), float(y1), float(y2))
        label_yolo = util.convert((width, height), label_box)
        label_file.write(str(target_id) + " " + " ".join([str(a) for a in label_yolo]) + '\n')

def synthetic_image(bg_img_path,bg_label_path,bg_roi_points,fg_img_paths,fg_img_label):
    '''
    合成图片
    :param bg_img_path: 背景图
    :param bg_label_path: 背景图标签
    :param bg_roi_points: 感兴趣域
    :param fg_img_paths: 前景图片集
    :param fg_img_label: 贴上前景标签
    :return: 合成图片,合成图片xml_lable
    '''

    config = ConfigParser()
    config.read("config.ini")
    num = config.getint('advanced','imgnum') # 贴图前景数量
    scalebox = config.getfloat('advanced','scalebox') # 前景标签框缩放比例
    iou = config.getfloat('advanced','iou') # 相交系数
    gaussianblur = config.getint('advanced','gaussianblur')
    noise = config.getint('advanced','noise')
    isseamlessclone = config.getint('advanced','isseamlessclone')
    min_size = config.getint('imageSize','min')
    max_size = config.getint('imageSize','max')
    classes_name = util.read_classes_txt('data/predefined_classes.txt')

    bg_img = cv2.imdecode(np.fromfile(bg_img_path,dtype=np.uint8),1) # 支持中文路径
    bg_label_path = os.path.splitext(bg_img_path)[0]+'.xml'
    bg_label = voc_xml.read_xml(bg_label_path)

    for i in range(num):
        fg_file = hp.rand_list(fg_img_paths)  
        fg_img = cv2.imdecode(np.fromfile(fg_file,dtype=np.uint8),1) # 支持中文路径
        fg_img = hp.img_resize(fg_img, max_size,min_size)
        fg_img = hp.gaussian_blurImg(fg_img,gaussianblur)
        new_bboxes = util.random_add_patches_in(fg_img.shape,bg_label,bg_img.shape,bg_roi_points,classes_name.get(fg_img_label,100),scalebox,iou)

        for count,new_bbox in enumerate(new_bboxes):
            cl, bbox_left, bbox_top, bbox_right, bbox_bottom = fg_img_label, new_bbox[1], new_bbox[2], new_bbox[3], \
                                                               new_bbox[4]
            height, width, channels = fg_img.shape
            height = scalebox * height
            width = scalebox * width
            center = (int(width / 2), int(height / 2))
            mask = 255 * np.ones(fg_img.shape, fg_img.dtype)
            try:
                if count > 1:
                    fg_img = flip_bbox(fg_img)
                if isseamlessclone==1:
                    # 泊松融合
                    bg_img[bbox_top:bbox_bottom, bbox_left:bbox_right] = cv2.seamlessClone(fg_img,
                                                                                        bg_img[bbox_top:bbox_bottom,
                                                                                        bbox_left:bbox_right],
                                                                                        mask, center, cv2.NORMAL_CLONE)
                else:
                    bg_img[bbox_top:bbox_bottom, bbox_left:bbox_right] = fg_img     # 普通融合
                bg_label.append([fg_img_label, new_bbox[1], new_bbox[2], new_bbox[3],new_bbox[4]])
            except ValueError:
                print("valueError")
                continue
    return bg_img, bg_label


def synthetic_img(bg_img_path, bg_label_path, bg_roi_points, fg_img_paths, num=1):
    '''
    合成图片
    :param bg_img_path: 背景图
    :param bg_label_path: 背景图标签
    :param bg_roi_points: 感兴趣域
    :param fg_img_paths: 前景图片集
    :return: 合成图片,合成图片lable
    '''
    # bg_img = cv2.imread(bg_img_path)
    bg_img = cv2.imdecode(np.fromfile(bg_img_path,dtype=np.uint8),1) # 支持中文路径
    bg_label_yolo = util.read_label_txt(bg_label_path)
    bg_label = util.rescale_yolo_labels(bg_label_yolo, bg_img.shape)
    all_boxes = []

    for _, rescale_label in enumerate(bg_label):
        all_boxes.append(rescale_label)

    for i in range(num):
        fg_file = hp.rand_list(fg_img_paths)
        # fg_img = cv2.imread(fg_file)
        fg_img = cv2.imdecode(np.fromfile(fg_file,dtype=np.uint8),1) # 支持中文路径
        # min_size = random.randint(800,1300)
        # max_size = random.randint(2300,2800)
        #主路中远端
        # min_size = random.randint(1000,1500)
        # max_size = random.randint(1501,2000)
        min_size = 1000
        max_size = 1300
        fg_img = hp.img_resize(fg_img, max_size,min_size)  # 前景像素面积大小!!!
        # fg_img = cv2.GaussianBlur(fg_img,(3,3),0)

        fg_img = hp.gaussian_blurImg(fg_img)
        # fg_img = add_noise(fg_img)

        new_bboxes = util.random_add_patches(fg_img.shape, all_boxes, bg_img.shape, bg_roi_points, cl=8, iou_thresh=0)

        for count, new_bbox in enumerate(new_bboxes):
            cl, bbox_left, bbox_top, bbox_right, bbox_bottom = new_bbox[0], new_bbox[1], new_bbox[2], new_bbox[3], \
                                                               new_bbox[4]
            height, width, channels = fg_img.shape
            height = 1.2 * height
            width = 1.2 * width
            center = (int(width / 2), int(height / 2))
            mask = 255 * np.ones(fg_img.shape, fg_img.dtype)

            try:
                if count > 1:
                    fg_img = flip_bbox(fg_img)
                # 泊松融合
                bg_img[bbox_top:bbox_bottom, bbox_left:bbox_right] = cv2.seamlessClone(fg_img,
                                                                                       bg_img[bbox_top:bbox_bottom,
                                                                                       bbox_left:bbox_right],
                                                                                       mask, center, cv2.NORMAL_CLONE)
                # bg_img[bbox_top:bbox_bottom, bbox_left:bbox_right] = fg_img     # 普通融合
                all_boxes.append(new_bbox)
            except ValueError:
                print("valueError")
                continue
    return bg_img, all_boxes
