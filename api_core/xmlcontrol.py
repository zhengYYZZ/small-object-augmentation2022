#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import os
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
import xml.etree.ElementTree as ET
from lxml import etree
import codecs

XML_EXT = '.xml'
ENCODE_METHOD = 'utf-8'

class PascalVocWriter:
# 创建并写入xml
    def __init__(self, foldername, filename, imgSize,databaseSrc='Unknown', localImgPath=None):
        self.foldername = foldername
        self.filename = filename
        self.databaseSrc = databaseSrc
        self.imgSize = imgSize
        self.boxlist = []
        self.localImgPath = localImgPath
        self.verified = False

    def prettify(self, elem):
        """
            Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf8')
        root = etree.fromstring(rough_string)
        return etree.tostring(root, pretty_print=True, encoding=ENCODE_METHOD).replace("  ".encode(), "\t".encode())
        # minidom does not support UTF-8
        '''reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t", encoding=ENCODE_METHOD)'''

    def genXML(self):
        """
            Return XML root
        """
        # Check conditions
        if self.filename is None or \
                self.foldername is None or \
                self.imgSize is None:
            return None

        top = Element('annotation')
        if self.verified:
            top.set('verified', 'yes')

        folder = SubElement(top, 'folder')
        folder.text = self.foldername

        filename = SubElement(top, 'filename')
        filename.text = self.filename

        if self.localImgPath is not None:
            localImgPath = SubElement(top, 'path')
            localImgPath.text = self.localImgPath

        source = SubElement(top, 'source')
        database = SubElement(source, 'database')
        database.text = self.databaseSrc

        size_part = SubElement(top, 'size')
        width = SubElement(size_part, 'width')
        height = SubElement(size_part, 'height')
        depth = SubElement(size_part, 'depth')
        width.text = str(self.imgSize[1])
        height.text = str(self.imgSize[0])
        if len(self.imgSize) == 3:
            depth.text = str(self.imgSize[2])
        else:
            depth.text = '1'

        segmented = SubElement(top, 'segmented')
        segmented.text = '0'
        return top

    def addBndBox(self, xmin, ymin, xmax, ymax, name, difficult):
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
        bndbox['name'] = name
        bndbox['difficult'] = difficult
        self.boxlist.append(bndbox)

    def appendObjects(self, top):
        for each_object in self.boxlist:
            object_item = SubElement(top, 'object')
            name = SubElement(object_item, 'name')
            try:
                name.text = unicode(each_object['name'])
            except NameError:
                # Py3: NameError: name 'unicode' is not defined
                name.text = each_object['name']
            pose = SubElement(object_item, 'pose')
            pose.text = "Unspecified"
            truncated = SubElement(object_item, 'truncated')
            if int(each_object['ymax']) == int(self.imgSize[0]) or (int(each_object['ymin'])== 1):
                truncated.text = "1" # max == height or min
            elif (int(each_object['xmax'])==int(self.imgSize[1])) or (int(each_object['xmin'])== 1):
                truncated.text = "1" # max == width or min
            else:
                truncated.text = "0"
            difficult = SubElement(object_item, 'difficult')
            difficult.text = str( bool(each_object['difficult']) & 1 )
            bndbox = SubElement(object_item, 'bndbox')
            xmin = SubElement(bndbox, 'xmin')
            xmin.text = str(each_object['xmin'])
            ymin = SubElement(bndbox, 'ymin')
            ymin.text = str(each_object['ymin'])
            xmax = SubElement(bndbox, 'xmax')
            xmax.text = str(each_object['xmax'])
            ymax = SubElement(bndbox, 'ymax')
            ymax.text = str(each_object['ymax'])

    def save(self, targetFile=None):
        root = self.genXML()
        self.appendObjects(root)
        out_file = None
        if targetFile is None:
            out_file = codecs.open(
                self.filename + XML_EXT, 'w', encoding=ENCODE_METHOD)
        else:
            out_file = codecs.open(targetFile, 'w', encoding=ENCODE_METHOD)

        prettifyResult = self.prettify(root)
        out_file.write(prettifyResult.decode('utf8'))
        out_file.close()


class PascalVocReader:

    def __init__(self, filepath):
        # shapes type:
        # [labbel, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        self.filepath = filepath
        self.verified = False
        try:
            self.parseXML()
        except:
            pass

    def getShapes(self):
        return self.shapes

    def addShape(self, label, bndbox, difficult):
        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)
        points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
        self.shapes.append((label, points, None, None, difficult))

    def parseXML(self):
        assert self.filepath.endswith(XML_EXT), "Unsupport file format"
        parser = etree.XMLParser(encoding=ENCODE_METHOD)
        xmltree = ElementTree.parse(self.filepath, parser=parser).getroot()
        filename = xmltree.find('filename').text
        try:
            verified = xmltree.attrib['verified']
            if verified == 'yes':
                self.verified = True
        except KeyError:
            self.verified = False

        for object_iter in xmltree.findall('object'):
            bndbox = object_iter.find("bndbox")
            label = object_iter.find('name').text
            # Add chris
            difficult = False
            if object_iter.find('difficult') is not None:
                difficult = bool(int(object_iter.find('difficult').text))
            self.addShape(label, bndbox, difficult)
        return True

def node_box(label,xmin_v,ymin_v,xmax_v,ymax_v):
    # test
    new_node = ElementTree.Element("object")
    name = ElementTree.SubElement(new_node,"name")
    name.text = label
    pose = ElementTree.SubElement(new_node,"pose")
    pose.text = 'Unspecified'
    truncated = ElementTree.SubElement(new_node, "truncated")
    truncated.text = '0'
    difficult = ElementTree.SubElement(new_node, "difficult")
    difficult.text = '1'
    bndbox = ElementTree.SubElement(new_node, "bndbox")
    xmin = ElementTree.SubElement(bndbox, "xmin")
    xmin.text = str(xmin_v)
    ymin = ElementTree.SubElement(bndbox, "ymin")
    ymin.text = str(ymin_v)
    xmax = ElementTree.SubElement(bndbox, "xmax")
    xmax.text = str(xmax_v)
    ymax = ElementTree.SubElement(bndbox, "ymax")
    ymax.text = str(ymax_v)
    return new_node

# 追加写入xml
def updata_xml_file(xml_path,box_data):
    """
    追加写入xml
    :param xml_path: xml文件位置
    :param box_data: 写入内容:[['label',x1,y1,w,h]...]
    :return:
    """
    tree = ElementTree.parse(xml_path)
    root = tree.getroot()
    for box in box_data:
        new_node = node_box(box[0],box[1],box[2],box[1]+box[3],box[2]+box[4])
        root.append(new_node)
    pretty_xml(root, '\t', '\n')
    tree.write(xml_path,xml_declaration=True, encoding="utf-8")


def pretty_xml(element, indent, newline, level=0):
    # elemnt为传进来的Elment类，参数indent用于缩进，newline用于换行
    if element:
        # 判断element是否有子元素
        if (element.text is None) or element.text.isspace():
            # 如果element的text没有内容
            element.text = newline + indent * (level + 1)
        else:
            element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)
        # else:  # 此处两行如果把注释去掉，Element的text也会另起一行
            # element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level
    temp = list(element)
    # 将element转成list
    for subelement in temp:
        if temp.index(subelement) < (len(temp) - 1):
            # 如果不是list的最后一个元素，说明下一个行是同级别元素的起始，缩进应一致
            subelement.tail = newline + indent * (level + 1)
        else:
            # 如果是list的最后一个元素， 说明下一行是母元素的结束，缩进应该少一个
            subelement.tail = newline + indent * level
        pretty_xml(subelement, indent, newline, level=level + 1)  # 对子元素进行递归操作

def convertPoints2BndBox(points):
    xmin = float('inf')
    ymin = float('inf')
    xmax = float('-inf')
    ymax = float('-inf')

    xmin = points[0]
    ymin = points[1]
    xmax = points[2]
    ymax = points[3]

    '''''''''
    for p in points:
        x = points[0]
        y = points[1]
        xmin = min(x, xmin)
        ymin = min(y, ymin)
        xmax = max(x, xmax)
        ymax = max(y, ymax)
    '''''''''
    # Martin Kersner, 2015/11/12
    # 0-valued coordinates of BB caused an error while
    # training faster-rcnn object detector.
    if xmin < 1:
        xmin = 1

    if ymin < 1:
        ymin = 1

    return int(xmin), int(ymin), int(xmax), int(ymax)

#创建并储存xml
def creat_xml(filename, shapes, imagePath, imageShape):
    """
    创建xml
    :param filename: xml file path
    :param shapes: box [['label',x1,y1,w,h]...]
    :param imagePath: img file path
    :param imageShape: img shape
    """
    imgFolderPath = os.path.dirname(imagePath)
    imgFolderName = os.path.split(imgFolderPath)[-1]
    imgFileName = os.path.basename(imagePath)
    # imgFileNameWithoutExt = os.path.splitext(imgFileName)[0]
    # Pascal format
    writer = PascalVocWriter(imgFolderName, imgFileName,
                                     imageShape, localImgPath=imagePath)

    for shape in shapes:
        label = shape[0]
        points = [shape[1], shape[2], shape[1] + shape[3], shape[2] + shape[4]]
        bndbox = convertPoints2BndBox(points)
        difficult = 1
        writer.addBndBox(bndbox[0], bndbox[1], bndbox[2], bndbox[3], label, difficult)

    writer.save(targetFile=filename)

# 读取xml
def read_xml(xml_path):
    """
    # 读取xml
    :param xml_path:xml路径
    :return:格式[[label,x1,y1,x2,y2]...]
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    size = root.find('size')
    img_w = int(size.find('width').text)
    img_h = int(size.find('height').text)

    box_list = []
    
    for obj in root.iter('object'):
        cls = obj.find('name').text
        xmlbox = obj.find('bndbox')
        box = [cls, xmlbox.find('xmin').text, xmlbox.find('ymin').text, 
                xmlbox.find('xmax').text, xmlbox.find('ymax').text]
        box_list.append(box)
    return box_list


# if __name__ == '__main__':
#     updata_xml_file("/home/online/zyx/lineGUI/ORI/0000001.xml",[['car',100,100,50,50])