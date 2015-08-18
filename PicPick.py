# -*- coding: cp936 -*-
"""
@Create: 2015/7/8
@author: Tang Yu-Jia
"""
from __future__ import division
import linecache
import os
import glob
import cv2
import xml.etree.cElementTree as xmlParser
from PreChooseSingleObject import CPreChooseSingleObject
from FreeChoose import CFreeChoose
from PreChooseMultiObject import CPreChooseMultiObject
from Check import CCheck
from CharacterPick import CCharacterPick
from Tool import CTool


class CPicPick:
    def __init__(self):
        self.InitParameter()

    def InitParameter(self):
        '''
        Init parameters...
        '''        
        ToolObj = CTool()
        GeneralParam, VideoParam, PictureParam, SavePath, CheckPath = ToolObj.ConfigReader()
        self.mode            = GeneralParam[0]
        self.srcFormat       = GeneralParam[1]
        self.label           = GeneralParam[2]
        self.ScaleParamDict  = GeneralParam[3]
        self.VisualParamDict = GeneralParam[4]

        self.videoJumpFrame  = VideoParam[0]
        self.videoSrc        = VideoParam[1]

        self.pictureSrc      = PictureParam
        self.SavePathDict    = SavePath
        self.CheckPathDict   = CheckPath

        self.whRatio = self.ScaleParamDict['WHRatio']

    def Create_Window(self, State):
        '''
        create window with window name and current state.
        '''
        cv2.namedWindow(State, flags=0)
        cv2.resizeWindow(State, self.VisualParamDict['resolutionWid'], self.VisualParamDict['resolutionHgt'])
        cv2.moveWindow(State, 50, 50)

    def Create_Mode(self):
        '''
        return mode object
        '''
        ModeFactory = {'PreChooseSingleObject':CPreChooseSingleObject(),'FreeChoose':CFreeChoose(),'CharacterPick':CCharacterPick(),'PreChooseMultiObject':CPreChooseMultiObject(),'Check':CCheck()}
        return ModeFactory[self.mode]
        
    def PicPick(self):
        self.doMode = self.Create_Mode()

        if self.srcFormat == 'picture':
            imgNameList = glob.glob(os.path.join(self.pictureSrc, '*.bmp')) + glob.glob(os.path.join(self.pictureSrc, '*.png'))
            assert imgNameList
            self.PictureRecursion(0, imgNameList)
            cv2.destroyAllWindows()
        elif self.srcFormat == 'video':
            cap = cv2.VideoCapture(self.videoSrc)
            self.videoLength = cap.get(CV_CAP_PROP_FRAME_COUNT)
            self.videoName = os.path.basename(self.videoSrc)
            self.VideoRecursion(cap, 0)
        else:
            print 'Unkown source format!!!'
            assert False

    def VideoRecursion(self, cap, currentPos):
        cap.set(cv2.CAP_PROP_POS_FRAMES,currentPos)
        ret, img = cap.read()
        if ret:
            state = self.videoSrc + '    ' + str(currentPos) + '/' + str(self.videoLength-1)
            cv2.destroyAllWindows()
            self.Create_Window(state)
            imgName = os.path.splitext(self.videoName)[0] + '_' + str(currentPos) + '.png'
            self.doMode.InputInfo(img, imgName, state, self.label, self.SavePathDict, self.VisualParamDict)
            self.rectList, self.maskList, returnFlag = self.doMode.VideoPicPick(cap, currentPos)
            if returnFlag == 'exit':
                return
            elif returnFlag == 'front':
                if currentPos-self.videoJumpFrame>=0:
                    self.VideoRecursion(cap, currentPos-self.videoJumpFrame)
                else:
                    self.VideoRecursion(cap, 0)
            elif returnFlag == 'back':
                if currentPos+self.videoJumpFrame<=self.videoLength-1:
                    self.VideoRecursion(cap, currentPos+self.videoJumpFrame)
                else:
                    self.VideoRecursion(cap, self.videoJumpFrame-1)
            elif returnFlag == 'next':
                if self.rectList:
                    if self.ScaleParamDict['IsNeedWHRatio'] == 1:
                        self.ScalebyWH()
                    assert len(self.rectList) == len(self.maskList)
                    self.doMode.Save(self.rectList)
                    cv2.destroyAllWindows()
            else:
                print 'Unkown keyboard input -> ', returnFlag
                assert False
        else:
            cap.release()
            cv2.destroyAllWindows()
            return

    def PictureRecursion(self, startIdx, imgNameList):
        for idx in range(startIdx, len(imgNameList)):
            state = imgNameList[idx] + '    ' + str(idx+1) + '/' + str(len(imgNameList))
            self.Create_Window(state)
            imgName = os.path.basename(imgNameList[idx])
            img = cv2.imread(os.path.join(self.pictureSrc, imgName))

            self.doMode.InputInfo(img, imgName, state, self.label, self.SavePathDict, self.VisualParamDict)
            self.rectList, self.maskList, returnFlag = self.doMode.PicturePicPick()
            if returnFlag == 'exit':
                cv2.destroyAllWindows()
                break
            elif returnFlag == 'back':
                if idx>0:
                    self.PictureRecursion(idx-1, imgNameList)
                    cv2.destroyAllWindows()
                else:
                    self.PictureRecursion(0, imgNameList)
            elif returnFlag == 'next':
                if self.rectList:
                    if self.ScaleParamDict['IsNeedWHRatio'] == 1:
                        self.ScalebyWH()
                    assert len(self.rectList) == len(self.maskList)
                    self.doMode.Save(self.rectList)
                    cv2.destroyAllWindows()
            else:
                print 'Unkown keyboard input -> ', returnFlag
                assert False

    #def Save(self, img, imgName):
    #    """
    #    Save object, ground truth and whole image.
    #    """
    #    ###save whole image
    #    cv2.imwrite(os.path.join(self.SavePathDict['imgPath'], imgName), img)
    #    fOut = open(os.path.join(self.SavePathDict['txtPath'], os.path.splitext(imgName)[0]+'.txt'),'a')
    #    fOut.close()
    #    fOut = open(os.path.join(self.SavePathDict['txtPath'], os.path.splitext(imgName)[0]+'.txt'),'w')
    #    fOut.write('% bbGt version=3'+'\n')

    #    objNum = 1
    #    for idx,mask in enumerate(self.maskList):
    #        rect = self.rectList[idx]
    #        ###save objects
    #        if mask ==0:
    #            objectImg = img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
    #            p = os.path.join(self.SavePathDict['objPath'], os.path.splitext(imgName)[0], '_', str(objNum), '.png')
    #            cv2.imwrite(os.path.join(self.SavePathDict['objPath'], os.path.splitext(imgName)[0]+'_'+str(objNum)+'.png'), objectImg)
    #            objNum += 1
    #        ###save labeled ground truth
    #        fOut.write(('%s %d %d %d %d 0 0 0 0 0 %d 0\n') % (self.label,rect[0],rect[1],rect[2],rect[3],mask))
        
    #    fOut.close()
    
    #def Save(self, img, imgName):
    #    """
    #    Save object, ground truth and whole image.
    #    """
    #    ###save whole image
    #    cv2.imwrite(os.path.join(self.SavePathDict['imgPath'], imgName), img)
    #    fOut = open(os.path.join(self.SavePathDict['txtPath'], os.path.splitext(imgName)[0]+'.txt'),'a')
    #    fOut.close()
    #    fOut = open(os.path.join(self.SavePathDict['txtPath'], os.path.splitext(imgName)[0]+'.txt'),'w')
    #    fOut.write('% bbGt version=3'+'\n')  

    #    objNum = 1
    #    for idx,mask in enumerate(self.maskList):
    #        rect = self.rectList[idx]
    #        ###save objects
    #        if mask ==0:
    #            objectImg = img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
    #            p = os.path.join(self.SavePathDict['objPath'], os.path.splitext(imgName)[0], '_', str(objNum), '.png')
    #            cv2.imwrite(os.path.join(self.SavePathDict['objPath'], os.path.splitext(imgName)[0]+'_'+str(objNum)+'.png'), objectImg)
    #            objNum += 1
    #        ###save labeled ground truth
    #        fOut.write(('%s %d %d %d %d 0 0 0 0 0 %d 0\n') % (self.label,rect[0],rect[1],rect[2],rect[3],mask))
        
    #    fOut.close()
            
    def ScalebyWH(self):
        """
        功能：以width或height为准按比例缩放截图样本。
        """
        for idx, rectList in enumerate(self.rectList):
            x = rectList[0]
            y = rectList[1]
            width = rectList[2]
            height = rectList[3]
            if self.ScaleParamDict['ScaleBy'] == 'width':
                ratio = self.whRatio[1]/self.whRatio[0]
                height = width*ratio
            elif self.ScaleParamDict['ScaleBy'] == 'height':
                ratio = self.whRatio[0]/self.whRatio[1]
                width = height*ratio
            else:
                print "Unkown 'ScaleBy' type!!!"
                assert False

            self.rectList[idx] = [x, y, width, height]
                        
    def ReadGt(self):
        """
        功能：读取gt数据并记录于rectParas列表。
        """
        rectParas = []
        gtFile = os.path.join(self.txtPath,self.imgName[:-4])+'.txt'
        fOut = open(gtFile,'r')
        lines = fOut.readlines()
        for line in lines[1:]:
            dataGt = line.split()
            startX = int(dataGt[1])
            startY = int(dataGt[2])
            endX = startX + int(dataGt[3])
            endY = startY + int(dataGt[4])
            mask = int(dataGt[10])
            rectParas.append([startX,startY,endX,endY,mask])
        fOut.close()
        return rectParas

    def VideoPick(self,mode):
        """
        功能：根据传入的模式参数对视频进行操作。
        """
        #pdb.set_trace()
        cap = cv2.VideoCapture(self.videoSrc)
        currentPos = 1
        cv2.namedWindow('image',cv2.WINDOW_NORMAL)
        while(1):
            if self.mode == 'PreChooseSingleObject':
                self.pictureParameters = mode.VideoPicPick(cap,currentPos)
                if self.pictureParameters == []:
                    break
                currentPos = self.pictureParameters[2]
                self.img = self.pictureParameters[3]      
                self.imgName = os.path.splitext(self.videoSrc.split('\\')[-1])[0]+'_'+str(int(currentPos))+'.png'
                self.ImgSaveFile()
                if self.ScaleParamDict['IsNeedWHRatio'] == 1:
                    self.ScalebyWH()
                self.ObjectSaveFile()
                self.fid.close()
            if self.mode == 'FreeChoose':
                self.img,rectParas,currentPos = mode.VideoPicPick(cap,currentPos)
                if rectParas == []:
                    break
                self.imgName = os.path.splitext(self.videoSrc.split('\\')[-1])[0]+'_'+str(int(currentPos))+'.png'
                self.ImgSaveFile()
                self.RectParasOperation(rectParas)
                self.fid.close()
            if self.mode == 'PreChooseMultiObject':
                self.img,rectParas,currentPos = mode.VideoPicPick(cap,currentPos)
                if rectParas == []:
                    break
                self.imgName = os.path.splitext(self.videoSrc.split('\\')[-1])[0]+'_'+str(int(currentPos))+'.png'
                self.ImgSaveFile()
                self.RectParasOperation(rectParas)
                self.fid.close()
        cap.release()
        cv2.destroyAllWindows()
       
       
    def RectParasOperation(self,rectParas):
        """
        功能：对传回的截图参数列表进行处理操作。
        """
        rectCount = 0
        imgName = self.imgName
        for rectPara in rectParas:
            rectCount += 1
            width = abs(rectPara[2]-rectPara[0])
            height = abs(rectPara[3]-rectPara[1])
            if rectPara[0] > rectPara[2]:
                rectPara[0],rectPara[2] = rectPara[2],rectPara[0]
                rectPara[1],rectPara[3] = rectPara[3],rectPara[1]
            rect = [rectPara[0],rectPara[1],width,height,rectPara[4]]
            objectImg = self.img[rectPara[1]:rectPara[3],rectPara[0]:rectPara[2]]
            self.imgName = os.path.splitext(imgName)[0]+'_'+str(rectCount)+'.png'
            self.pictureParameters = [objectImg,rect]
            if self.ScaleParamDict['IsNeedWHRatio'] == 1:
                self.ScalebyWH()
            self.ObjectSaveFile()