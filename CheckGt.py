# -*- coding: cp936 -*-
"""
@Create: 2015/7/8
@author: Tang Yu-Jia
"""
import cv2
import linecache

class CCheckGt:
    def __init__(self, CheckPathDict):
        self.CheckPathDict = CheckPathDict
        self.picModel = False
        self.startX = self.startY = -1
        self.endX = self.endY = -1
        self.width = self.height = 0
        self.isAppRect = False # Is a Rect appended into list right now?
        self.roiPointList = list() # start point and end point
        self.maskList = list() # len(mask) == len(roiPointList)
        self.color_blue  = (255, 0, 0)
        self.color_green = (0, 255, 0)
        self.color_red   = (0, 0, 255)
        self.roiPointList = list()
        self.maskList = list()
        self.img = None
   
    def InputInfo(self, img, imgName, state, VisualParamDict):
        '''
        the 'clean' image without any drawing and the image title(a.k. the state) is inputted by this function
        '''
        self.img = img
        self.imgName = imgName
        self.state = state
        self.lineThickness = VisualParamDict['LineThickness']

    def InitVar(self):
        self.roiPointList  = list()
        self.maskList = list()

    def Check(self):
        self.img = cv2.imread(self.imgName)
        with open(self.txtName, 'r') as fin:
            lines = fin.readlines()

        self.LinesToRoiList(lines)
        self.DrawRoiList(self.roiPointList, self.maskList)

        cv2.setMouseCallback(self.state, self.OnMouse)
        while True:
            keyInput = cv2.waitKey(0)
            if keyInput == ord('d'):
                self.imgCurrent = self.img.copy()
                if self.roiPointList:
                    self.roiPointList.pop()
                    self.maskList.pop()
                    if self.maskList:
                        self.DrawRoiList(self.roiPointList, self.maskList)
                        cv2.imshow(self.state, self.imgCurrent)
                    else:
                        cv2.imshow(self.state, self.imgCurrent)
                else:
                    cv2.imshow(self.state, self.imgCurrent)
                keyInput = None
            if keyInput == 27:
                flag = 'exit'
                break
            if keyInput == ord(' '):
                flag = 'next'
                break
            if keyInput == ord('b'):
                flag = 'back'
                break
        def Roi2Rect(roiList):
            rectList = list()
            for roi in roiList:
                rect = [roi[0], roi[1], roi[2]-roi[0]+1, roi[3]-roi[1]+1]
                rectList.append(rect)
            return rectList
        self.rectList = Roi2Rect(self.roiPointList)
        return self.rectList, self.maskList, flag

    def LinesToRoiList(self, lines):
        self.InitVar()
        for line in lines:
            self.label = line[0]
            self.roiPointList.append([int(line[1]), int(line[2]), int(line[1])+int(line[3]), int(line[2])+int(line[4])])
            self.maskList.append(int(line[-2]))
        
    def OnMouse(self, event, x, y, flags, param):
        """
        drawing：FreeChoose
        删除模式：响应鼠标左键按下。
        """
        if self.picModel == True:
            if event == cv2.EVENT_LBUTTONDOWN:
                self.startX = x
                self.startY = y
            elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
                self.saveRect = True
                self.copyImg = self.saveImg.copy()
                self.endX = x
                self.endY = y
                cv2.circle(self.copyImg,((self.endX-self.startX)/2+self.startX,(self.endY-self.startY)/2+self.startY),self.thickness,(0,255,0),-1)
                cv2.rectangle(self.copyImg,(self.startX,self.startY),(self.endX,self.endY),(0,255,0),self.thickness)
                cv2.imshow(self.imgName,self.copyImg)
            elif event == cv2.EVENT_LBUTTONUP:
                self.saveImg = self.copyImg.copy()
                if self.saveRect == True:
                    self.rectParas.append([self.startX,self.startY,self.endX,self.endY,0])
                    self.saveRect = False
            elif event == cv2.EVENT_RBUTTONDOWN:
                self.startX = x
                self.startY = y
            elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON:
                self.copyImg = self.saveImg.copy()
                self.endX = x
                self.endY = y
                cv2.circle(self.copyImg,((self.endX-self.startX)/2+self.startX,(self.endY-self.startY)/2+self.startY),self.thickness,(255,0,0),-1)
                cv2.rectangle(self.copyImg,(self.startX,self.startY),(self.endX,self.endY),(255,0,0),self.thickness)
                cv2.imshow(self.imgName, self.copyImg)
            elif event == cv2.EVENT_RBUTTONUP:
                self.saveImg = self.copyImg.copy()
                self.rectParas.append([self.startX,self.startY,self.endX,self.endY,1])
        else:
            if event == cv2.EVENT_LBUTTONDOWN:
                for rectPara in self.rectParas:
                    startX = rectPara[0]
                    startY = rectPara[1]
                    endX = rectPara[2]
                    endY = rectPara[3]
                    if startX<= x <=endX and startY<=y<=endY:
                        cv2.circle(self.saveImg,(startX+(endX-startX)/2,startY+(endY-startY)/2),self.thickness,(0,0,255),-1)
                        cv2.rectangle(self.saveImg,(startX,startY),(endX,endY),(0,0,255), self.thickness)
                        self.rectParas.remove(rectPara)
                cv2.imshow(self.imgName, self.saveImg)
                    

    def ShowResult(self, img, rectParas, imgName):
        """
        功能：根据gt显示截图结果。
        """
        self.imgName=imgName
        cv2.setMouseCallback(imgName, self.DrawOrDelRectangle)
        self.saveImg = img.copy()
        self.rectParas = rectParas
        self.DrawRectangles()
        cv2.imshow(imgName,self.saveImg)
        while(1):
            keyInput = cv2.waitKey(0)
            if keyInput == ord('d'):
                self.picModel = False
                self.saveImg = img.copy()
                self.DrawRectangles()
                cv2.imshow(imgName, self.saveImg)
            if keyInput == ord('r'):
                self.picModel = True
            if keyInput == ord(' '):
                break
            if keyInput == 27:
                return 'exit'
            if keyInput == ord('b'):
                return 'back'
        return self.rectParas
                    
        
                
    def DrawRoiList(self, roiPointList = list(), maskList = list()):
        """
        draw all roiPoints, including objects and masks
        """
        for idx, roiPoint in enumerate(roiPointList):
            if maskList:
                if maskList[idx] == 0:
                    cv2.circle(self.imgCurrent,(int((roiPoint[2]-roiPoint[0])/2+roiPoint[0]), int((roiPoint[3]-roiPoint[1])/2+ roiPoint[1])),self.lineThickness,self.color_green,-1)
                    cv2.rectangle(self.imgCurrent,(roiPoint[0], roiPoint[1]),(roiPoint[2],roiPoint[3]),self.color_green,self.lineThickness)
                elif maskList[idx] == 1:
                    cv2.circle(self.imgCurrent,(int((roiPoint[2]-roiPoint[0])/2+roiPoint[0]), int((roiPoint[3]-roiPoint[1])/2+roiPoint[1])),self.lineThickness,self.color_blue,-1)
                    cv2.rectangle(self.imgCurrent,(roiPoint[0],roiPoint[1]),(roiPoint[2],roiPoint[3]),self.color_blue,self.lineThickness)

    def Save(self, rectList):
        """
        Save object, ground truth and whole image.
        """
        ###rectList maybe scaled by W/H, so need to reinput it
        ###save whole image
        imgPath = os.path.join(self.SavePathDict['imgPath'], self.imgName)
        cv2.imwrite(imgPath, self.img)
        txtPath = os.path.join(self.SavePathDict['txtPath'], os.path.splitext(self.imgName)[0]+'.txt')
        fOut = open(txtPath,'a')
        fOut.close()
        fOut = open(txtPath,'w')
        fOut.write('% bbGt version=3'+'\n')  

        objNum = 1
        for idx,mask in enumerate(self.maskList):
            rect = rectList[idx]
            ###save objects
            if mask ==0:
                objectImg = self.img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
                cv2.imwrite(os.path.join(self.SavePathDict['objPath'], os.path.splitext(self.imgName)[0]+'_'+str(objNum)+'.png'), objectImg)
                objNum += 1
            ###save labeled ground truth
            fOut.write(('%s %d %d %d %d 0 0 0 0 0 %d 0\n') % (self.label,rect[0],rect[1],rect[2],rect[3],mask))
        
        fOut.close()