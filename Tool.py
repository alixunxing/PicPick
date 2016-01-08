# -*- coding: utf-8 -*-
"""
@Create: 2015/7/8
@author: Tang Yu-Jia
"""
import os
import shutil
import xml.etree.cElementTree as xmlParser

class CTool:
    def FolderEmpty(self, path):
        """
        功能：清空存储路径文件，如果存储路径不存在则创建。
        """
        isPathExist = lambda path: os.path.exists(path)

        objPath = os.path.join(path, 'obj')
        if not isPathExist(objPath):
            os.makedirs(objPath)

        imgPath = os.path.join(path, 'pos')
        if not isPathExist(imgPath):
            os.makedirs(imgPath)

        txtPath = os.path.join(path, 'posGt')
        if not isPathExist(txtPath):
            os.makedirs(txtPath)
        
        fileList = os.listdir(objPath) + os.listdir(imgPath) + os.listdir(txtPath)
        
        if fileList:
            keyInput = raw_input(('Do you want to clean %s\\, %s\\ and %s\\? (y/n)') % (objPath,imgPath,txtPath))
            if keyInput == 'y' or keyInput == 'Y': 
                shutil.rmtree(objPath)
                os.makedirs(objPath)
                shutil.rmtree(imgPath)
                os.makedirs(imgPath)
                shutil.rmtree(txtPath)
                os.makedirs(txtPath)
            elif keyInput == 'n' or keyInput == 'N':
                pass
            else:
                print 'Wrong input'
                assert False

        return objPath, imgPath, txtPath

    def ConfigReader(self):
        '''
        功能：读取配置文档，初始化参数。
        '''
        root = xmlParser.parse('config.xml')

        def GeneralParamReader():
            GeneralNode = root.find('General_Parameters')
            mode        = GeneralNode.find('Mode').text
            srcFormat   = GeneralNode.find('SrcFormat').text
            label       = GeneralNode.find('Label').text

            def ScaleParamReader():
                ScaleNode       = GeneralNode.find('Scale_Parameters')
                scaleby         = ScaleNode.find('ScaleBy').text
                IsNeedWHRatio   = ScaleNode.find('IsNeedWHRatio').text
                WHRatioNode     = ScaleNode.find('WHRatio')
                wRatio          = WHRatioNode.attrib.get('wRatio')
                hRatio          = WHRatioNode.attrib.get('hRatio')
                WHRatio         = (float(wRatio), float(hRatio))
                ScaleParamDict  = {'ScaleBy':scaleby, 'IsNeedWHRatio':int(IsNeedWHRatio), 'WHRatio':WHRatio}
                return ScaleParamDict
        
            def VisualParamReader():
                VisualNode      = GeneralNode.find('Visual_Parameters')
                lineThickNode   = VisualNode.find('LineThickness')
                LineThickness   = lineThickNode.attrib.get('thickness')
                resolutionNode  = VisualNode.find('Resolution')
                resolutionWid   = resolutionNode.attrib.get('width')
                resolutionHgt   = resolutionNode.attrib.get('height')
                VisualParamDict = {'LineThickness':int(LineThickness), 'resolutionWid':int(resolutionWid), 'resolutionHgt':int(resolutionHgt)}
                return VisualParamDict

            return mode, srcFormat, label, ScaleParamReader(), VisualParamReader()

        def VideoParamReader():
            VideoNode           = root.find('Video_Parameters')
            VideoJumpFrameNode  = VideoNode.find('VideoJumpFrame')
            VideoJumpFrame      = VideoJumpFrameNode.attrib.get('frame')
            VideoSrc            = VideoNode.find('VideoSrc').text
            return int(VideoJumpFrame), VideoSrc

        def PictureParamReader():
            PictureNode = root.find('Picture_Parameters')
            PictureSrc  = PictureNode.find('PictureSrc').text
            return PictureSrc

        def CheckParamReader():
            CheckNode = root.find('Check_Parameters')
            LabelSet  = CheckNode.find('LabelSet').text
            return LabelSet.split()

        def SavePathReader():
            SavePath = root.find('SavePath').text
            objPath, imgPath, txtPath = self.FolderEmpty(SavePath)
            SavePathDict = {'objPath':objPath, 'imgPath':imgPath, 'txtPath':txtPath}
            return SavePathDict

        def CheckPathReader():
            CheckPath     = root.find('CheckPath').text
            objPath       = os.path.join(CheckPath, 'obj')
            imgPath       = os.path.join(CheckPath, 'pos')
            txtPath       = os.path.join(CheckPath, 'posGt')
            CheckPathDict = {'objPath':objPath, 'imgPath':imgPath, 'txtPath':txtPath}
            return CheckPathDict

        return GeneralParamReader(), VideoParamReader(), PictureParamReader(), CheckParamReader(), SavePathReader(), CheckPathReader()