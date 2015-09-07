"""
@Create: 2015/7/8
@author: Tang Yu-Jia
"""
from __future__ import division
import os
import cv2
import glob
import linecache
import xml.etree.cElementTree as xmlParser
from Tool import CTool
from CheckGt import CCheckGt
from CheckDt import CCheckDt
from FreeChoose import CFreeChoose
from CharacterPick import CCharacterPick
from PreChooseMultiObject import CPreChooseMultiObject
from PreChooseSingleObject import CPreChooseSingleObject


class CPicPick:
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
        ModeFactory = {'PreChooseSingleObject':CPreChooseSingleObject(), 'FreeChoose':CFreeChoose(), 'CharacterPick':CCharacterPick(), 'PreChooseMultiObject':CPreChooseMultiObject()}
        return ModeFactory[self.mode]

    def Check(self):
        imgNameList = glob.glob(os.path.join(self.CheckPathDict['imgPath'], '*.bmp')) + glob.glob(os.path.join(self.CheckPathDict['imgPath'], '*.png')) + glob.glob(os.path.join(self.CheckPathDict['imgPath'], '*.jpg'))
        txtNameList = glob.glob(os.path.join(self.CheckPathDict['txtPath'], '*.txt'))
        assert len(imgNameList) == len(txtNameList)
        imgNameList.sort()
        txtNameList.sort()
        self.doCheck = CCheckGt(self.CheckPathDict)
        self.CheckRecursion(0, imgNameList, txtNameList)

    def CheckRecursion(self, startIdx, imgNameList, txtNameList):
        for idx in range(len(imgNameList)):
            assert os.path.splitext(imgNameList[idx])[0] == os.path.splitext(txtNameList[idx])[0]
            state = imgNameList[idx] + '    ' + str(idx+1) + '/' + str(len(imgNameList))
            self.doCheck.InputInfo(imgNameList[idx], txtNameList[idx], state, self.VisualParamDict)
            self.doCheck.Check()
            if returnFlag == 'exit':
                cv2.destroyAllWindows()
                break
            elif returnFlag == 'back':
                if idx>0:
                    self.CheckRecursion(idx-1, imgNameList, txtNameList)
                    cv2.destroyAllWindows()
                else:
                    self.CheckRecursion(0, imgNameList, txtNameList)
            elif returnFlag == 'next':
                if self.rectList:
                    if self.ScaleParamDict['IsNeedWHRatio'] == 1:
                        self.ScalebyWH()
                    assert len(self.rectList) == len(self.maskList)
                    self.doCheck.Save(self.rectList)
                    cv2.destroyAllWindows()
            else:
                print 'Unkown keyboard input -> ', returnFlag
                assert False

    def PicPick(self):
        self.doPicPick = self.Create_Mode()

        if self.srcFormat == 'picture':
            imgNameList = glob.glob(os.path.join(self.pictureSrc, '*.bmp')) + glob.glob(os.path.join(self.pictureSrc, '*.png')) + glob.glob(os.path.join(self.pictureSrc, '*.jpg'))
            assert imgNameList
            self.PictureRecursion(0, imgNameList)
            cv2.destroyAllWindows()
        elif self.srcFormat == 'video':
            cap = cv2.VideoCapture(self.videoSrc)
            self.videoLength = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.videoName = os.path.basename(self.videoSrc)
            self.VideoRecursion(cap, 0)
        else:
            print 'Unkown source format!!!'
            assert False

    def VideoRecursion(self, cap, currentPos):
        cap.set(cv2.CAP_PROP_POS_FRAMES, currentPos)
        ret, img = cap.read()
        if ret:
            state = self.videoSrc + '    ' + str(currentPos) + '/' + str(self.videoLength)
            cv2.destroyAllWindows()
            self.Create_Window(state)
            imgName = os.path.splitext(self.videoName)[0] + '_' + str(currentPos) + '.png'
            self.doPicPick.InputInfo(img, imgName, state, self.label, self.SavePathDict, self.VisualParamDict)
            self.rectList, self.maskList, returnFlag = self.doPicPick.VideoPicPick()
            if returnFlag == 'exit':
                cap.release()
                cv2.destroyAllWindows()
                return
            elif returnFlag == 'front':
                if currentPos+self.videoJumpFrame<=self.videoLength-1:
                    self.VideoRecursion(cap, currentPos+self.videoJumpFrame)
                else:
                    self.VideoRecursion(cap, self.videoJumpFrame-1)
            elif returnFlag == 'back':
                if currentPos-self.videoJumpFrame>=0:
                    self.VideoRecursion(cap, currentPos-self.videoJumpFrame)
                else:
                    self.VideoRecursion(cap, 0)
            elif returnFlag == 'next':
                if self.rectList:
                    if self.ScaleParamDict['IsNeedWHRatio'] == 1:
                        self.ScalebyWH()
                    assert len(self.rectList) == len(self.maskList)
                    self.doPicPick.Save(self.rectList)
                self.VideoRecursion(cap, currentPos+1)
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

            self.doPicPick.InputInfo(img, imgName, state, self.label, self.SavePathDict, self.VisualParamDict)
            self.rectList, self.maskList, returnFlag = self.doPicPick.PicturePicPick()
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
                    self.doPicPick.Save(self.rectList)
                    cv2.destroyAllWindows()
            else:
                print 'Unkown keyboard input -> ', returnFlag
                assert False

