"""
@Create: 2015/7/8
@author: Tang Yu-Jia
"""
import os
import cv2

class CCheckGt:
    def __init__(self, CheckPathDict):
        self.CheckPathDict = CheckPathDict
        self.startX = self.startY = -1
        self.endX = self.endY = -1
        self.width = self.height = 0

        self.LabelSet = list() # candidate Label set

        self.isChoose = False # Is opened choose mode?
        self.isDelete = False # Is opened delete mode?
        self.isLabel  = False # Is opened labeling mode?
        self.isLabelNum = [False]*3 # Which label is to choose? Currentlly, one can only choose 3 kinds of labels...

        self.isAppRect = False # Is a Rect appended into list right now?

        self.roiPointList = list() # start point and end point
        self.maskList     = list() # len(mask) == len(roiPointList)
        self.labelList    = list() # read labels in posGt

        self.ChangeLabel = list() # labels to be changed

        self.color_blue  = (255, 0, 0)
        self.color_green = (0, 255, 0)
        self.color_red   = (0, 0, 255)
   
    def InputInfo(self, imgName, txtName, state, SavePathDict, VisualParamDict, label, LabelSet):
        '''
        the 'clean' image without any drawing and the image title(a.k. the state) is inputted by this function
        '''
        self.imgName = imgName
        self.txtName = txtName
        self.state = state
        self.SavePathDict = SavePathDict
        self.lineThickness = VisualParamDict['LineThickness']
        self.label = label
        self.LabelSet = LabelSet

    def InitVar(self):
        self.roiPointList = list()
        self.maskList     = list()
        self.labelList    = list()

    def Check(self):
        self.img = cv2.imread(self.imgName)
        self.hgt, self.wid, c = self.img.shape
        self.imgCurrent = self.img.copy()
        with open(self.txtName, 'r') as fin:
            lines = fin.readlines()
            assert lines

        self.LinesToRoiList(lines)
        self.DrawRoiList(self.roiPointList, self.maskList, self.labelList)
        cv2.imshow(self.state, self.imgCurrent)

        cv2.setMouseCallback(self.state, self.OnMouse)
        while True:
            keyInput = cv2.waitKey(0)
            if keyInput == ord('d'): # Delete mode
                self.isDelete = True
                self.isChoose = False
                self.isLabel  = False
                self.imgCurrent = self.img.copy()
                self.DrawRoiList(self.roiPointList, self.maskList, self.labelList)
                cv2.putText(self.imgCurrent, 'Delete Mode', (0,30), 1, 3, self.color_red, self.lineThickness)
                cv2.imshow(self.state, self.imgCurrent)
            elif keyInput == 9: # Tab, choose mode
                self.isDelete = False
                self.isChoose = True
                self.isLabel  = False
                self.imgCurrent = self.img.copy()
                self.DrawRoiList(self.roiPointList, self.maskList, self.labelList)
                cv2.putText(self.imgCurrent, 'Choose Mode', (0,30), 1, 3, self.color_red, self.lineThickness)
                cv2.imshow(self.state, self.imgCurrent)
            elif keyInput == ord('l'): # Tab, choose mode
                self.isDelete = False
                self.isChoose = False
                self.isLabel  = True
                self.imgCurrent = self.img.copy()
                self.DrawRoiList(self.roiPointList, self.maskList, self.labelList)
                cv2.putText(self.imgCurrent, 'Label Mode', (0,30), 1, 3, self.color_red, self.lineThickness)
                for i, label in enumerate(self.LabelSet):
                    cv2.putText(self.imgCurrent, str(i+1)+':'+label, (0,30*(i+2)), 1, 2, self.color_green, self.lineThickness)
                cv2.imshow(self.state, self.imgCurrent)
            elif keyInput == ord('1'):
                self.isLabelNum[0] = True
                self.isLabelNum[1] = False
                self.isLabelNum[2] = False
            elif keyInput == ord('2'):
                self.isLabelNum[1] = True
                self.isLabelNum[0] = False
                self.isLabelNum[2] = False
            elif keyInput == ord('3'):
                self.isLabelNum[2] = True
                self.isLabelNum[0] = False
                self.isLabelNum[1] = False
            elif keyInput == 27:
                flag = 'exit'
                break
            elif keyInput == ord(' '):
                flag = 'next'
                break
            elif keyInput == ord('b'):
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
        for line in lines[1:]:
            line = line.split()
            self.labelList.append(line[0])
            self.roiPointList.append([int(line[1]), int(line[2]), int(line[1])+int(line[3]), int(line[2])+int(line[4])])
            self.maskList.append(int(line[-2]))
        
    def OnMouse(self, event, x, y, flags, param):
        """
        input 'd' to get into delete mode, one can choose bbox to delete
        input 'tab' to get into choose mode, one can draw object or mask
        input 'l' to get into labeling mode, one can relabel object
        """
        if self.isChoose:
            if event == cv2.EVENT_LBUTTONDOWN:
                self.startX = x
                self.startY = y
            elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
                self.isAppRect = True
                self.imgTmp = self.imgCurrent.copy()
                self.endX = x
                self.endY = y
                cv2.circle(self.imgTmp,(int((self.endX-self.startX)/2+self.startX), int((self.endY-self.startY)/2+self.startY)),self.lineThickness,self.color_green,-1)
                cv2.rectangle(self.imgTmp,(self.startX,self.startY),(self.endX, self.endY),self.color_green,self.lineThickness)
                cv2.imshow(self.state, self.imgTmp)
            elif event == cv2.EVENT_LBUTTONUP:
                if self.isAppRect and self.startX != self.endX and self.startY !=self.endY:
                    ###### if drawing started from the right-bottom, swap(startPoint, endPoint)
                    self.SwapXY()
                    self.roiPointList.append([self.startX, self.startY, self.endX, self.endY])
                    self.maskList.append(0)
                    self.labelList.append(self.label)
                    cv2.putText(self.imgTmp, self.label, (self.startX, self.startY), 1, 1, self.color_red, self.lineThickness)
                    cv2.imshow(self.state, self.imgTmp)
                    self.imgCurrent = self.imgTmp.copy()
                    self.isAppRect = False

                    # self.isChoose = False

            if event == cv2.EVENT_RBUTTONDOWN:
                self.startX = x
                self.startY = y
            elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON:
                self.isAppRect = True
                self.imgTmp = self.imgCurrent.copy()
                self.endX = x
                self.endY = y
                cv2.circle(self.imgTmp,(int((self.endX-self.startX)/2+self.startX), int((self.endY-self.startY)/2+self.startY)),self.lineThickness,self.color_blue,-1)
                cv2.rectangle(self.imgTmp,(self.startX,self.startY),(self.endX, self.endY), self.color_blue,self.lineThickness)
                cv2.imshow(self.state, self.imgTmp)
            elif event == cv2.EVENT_RBUTTONUP:
                if self.isAppRect and self.startX != self.endX and self.startY !=self.endY:
                    ###### if drawing started from the right-bottom, swap(startPoint, endPoint)
                    self.SwapXY()
                    self.roiPointList.append([self.startX, self.startY, self.endX, self.endY])
                    self.maskList.append(1)
                    self.labelList.append(self.label)
                    cv2.putText(self.imgTmp, self.label, (self.startX, self.startY), 1, 1, self.color_red, self.lineThickness)
                    cv2.imshow(self.state, self.imgTmp)
                    self.imgCurrent = self.imgTmp.copy()
                    self.isAppRect = False
                    # self.isChoose = False
        elif self.isDelete:
            if event == cv2.EVENT_LBUTTONDOWN:
                for i, roi in enumerate(self.roiPointList):
                    startX = roi[0]
                    startY = roi[1]
                    endX = roi[2]
                    endY = roi[3]
                    if startX<=x<=endX and startY<=y<=endY:
                        cv2.circle(self.imgCurrent, (startX+(endX-startX)/2, startY+(endY-startY)/2), self.lineThickness, self.color_red, -1)
                        cv2.rectangle(self.imgCurrent, (startX,startY), (endX,endY), self.color_red, self.lineThickness)
                        self.roiPointList.pop(i)
                        self.maskList.pop(i)
                        self.labelList.pop(i)
                        cv2.putText(self.imgCurrent, 'Delete Mode', (0,30), 1, 3, self.color_red, self.lineThickness)
                        cv2.imshow(self.state, self.imgCurrent)
            elif event == cv2.EVENT_LBUTTONUP:
                # self.isDelete = False
                self.imgCurrent = self.img.copy()
                self.DrawRoiList(self.roiPointList, self.maskList, self.labelList)
                cv2.putText(self.imgCurrent, 'Delete Mode', (0,30), 1, 3, self.color_red, self.lineThickness)
                cv2.imshow(self.state, self.imgCurrent)
        elif self.isLabel:
            if self.isLabelNum[0]:
                self.imgCurrent = self.img.copy()
                self.DrawRoiList(self.roiPointList, self.maskList, self.labelList)
                cv2.putText(self.imgCurrent, 'Label Mode', (0,30), 1, 3, self.color_red, self.lineThickness)
                for i, label in enumerate(self.LabelSet):
                    if i==0:
                        cv2.putText(self.imgCurrent, str(i+1)+':'+label, (0,30*(i+2)), 1, 2, self.color_red, self.lineThickness)
                        #self.isLabelNum[0] = False
                    else:
                        cv2.putText(self.imgCurrent, str(i+1)+':'+label, (0,30*(i+2)), 1, 2, self.color_green, self.lineThickness)
                cv2.imshow(self.state, self.imgCurrent)
            elif self.isLabelNum[1]:
                self.imgCurrent = self.img.copy()
                self.DrawRoiList(self.roiPointList, self.maskList, self.labelList)
                cv2.putText(self.imgCurrent, 'Label Mode', (0,30), 1, 3, self.color_red, self.lineThickness)
                for i, label in enumerate(self.LabelSet):
                    if i==1:
                        cv2.putText(self.imgCurrent, str(i+1)+':'+label, (0,30*(i+2)), 1, 2, self.color_red, self.lineThickness)
                        #self.isLabelNum[1] = False
                    else:
                        cv2.putText(self.imgCurrent, str(i+1)+':'+label, (0,30*(i+2)), 1, 2, self.color_green, self.lineThickness)
                cv2.imshow(self.state, self.imgCurrent)
            elif self.isLabelNum[2]:
                self.imgCurrent = self.img.copy()
                self.DrawRoiList(self.roiPointList, self.maskList, self.labelList)
                cv2.putText(self.imgCurrent, 'Label Mode', (0,30), 1, 3, self.color_red, self.lineThickness)
                for i, label in enumerate(self.LabelSet):
                    if i==2:
                        cv2.putText(self.imgCurrent, str(i+1)+':'+label, (0,30*(i+2)), 1, 2, self.color_red, self.lineThickness)
                        #self.isLabelNum[2] = False
                    else:
                        cv2.putText(self.imgCurrent, str(i+1)+':'+label, (0,30*(i+2)), 1, 2, self.color_green, self.lineThickness)
                cv2.imshow(self.state, self.imgCurrent)
                           
            if (event == cv2.EVENT_LBUTTONDOWN) and (True in self.isLabelNum):
                for i, roi in enumerate(self.roiPointList):
                    startX = roi[0]
                    startY = roi[1]
                    endX = roi[2]
                    endY = roi[3]
                    if startX<=x<=endX and startY<=y<=endY:
                        self.ChangeLabel.append(i)
                        cv2.circle(self.imgCurrent, (startX+(endX-startX)/2, startY+(endY-startY)/2), self.lineThickness, self.color_red, -1)
                        cv2.rectangle(self.imgCurrent, (startX,startY), (endX,endY), self.color_red, self.lineThickness)
                        cv2.imshow(self.state, self.imgCurrent)
            elif event == cv2.EVENT_LBUTTONUP and (True in self.isLabelNum):
                # self.isDelete = False
                for i in self.ChangeLabel:
                    CurrentLabelIdx = self.isLabelNum.index(True)
                    self.labelList[i] = self.LabelSet[CurrentLabelIdx]
                self.ChangeLabel = []
                self.imgCurrent = self.img.copy()
                self.DrawRoiList(self.roiPointList, self.maskList, self.labelList)
                cv2.imshow(self.state, self.imgCurrent)

           
    def DrawRoiList(self, roiPointList = list(), maskList = list(), labelList = list()):
        """
        draw all roiPoints with their labels, including objects and masks
        """
        for idx, roiPoint in enumerate(roiPointList):
            if maskList:
                if maskList[idx] == 0:
                    cv2.circle(self.imgCurrent,(int((roiPoint[2]-roiPoint[0])/2+roiPoint[0]), int((roiPoint[3]-roiPoint[1])/2+ roiPoint[1])),self.lineThickness,self.color_green,-1)
                    cv2.rectangle(self.imgCurrent,(roiPoint[0], roiPoint[1]),(roiPoint[2],roiPoint[3]),self.color_green,self.lineThickness)
                    cv2.putText(self.imgCurrent, labelList[idx], (roiPoint[0], roiPoint[1]), 1, 1, self.color_red, self.lineThickness)
                elif maskList[idx] == 1:
                    cv2.circle(self.imgCurrent,(int((roiPoint[2]-roiPoint[0])/2+roiPoint[0]), int((roiPoint[3]-roiPoint[1])/2+roiPoint[1])),self.lineThickness,self.color_blue,-1)
                    cv2.rectangle(self.imgCurrent,(roiPoint[0],roiPoint[1]),(roiPoint[2],roiPoint[3]),self.color_blue,self.lineThickness)
                    cv2.putText(self.imgCurrent, labelList[idx], (roiPoint[0], roiPoint[1]), 1, 1, self.color_red, self.lineThickness)

    def Save(self, rectList):
        """
        Save object, ground truth and whole image.
        """
        ###rectList maybe scaled by W/H, so need to reinput it
        ###save whole image
        imgPath = os.path.join(self.SavePathDict['imgPath'], self.imgName)
        cv2.imwrite(imgPath, self.img)
        txtPath = os.path.join(self.SavePathDict['txtPath'], os.path.splitext(os.path.basename(self.imgName))[0]+'.txt')
        fOut = open(txtPath,'a')
        fOut.close()
        fOut = open(txtPath,'w')
        fOut.write('% bbGt version=3'+'\n')

        objNum = 1
        for idx, mask in enumerate(self.maskList):
            rect = rectList[idx]
            ###save objects
            if mask ==0:
                objectImg = self.img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
                cv2.imwrite(os.path.join(self.SavePathDict['objPath'], os.path.splitext(os.path.basename(self.imgName))[0]+'_'+str(objNum)+'.png'), objectImg)
                objNum += 1
            ###save labeled ground truth
            fOut.write(('%s %d %d %d %d 0 0 0 0 0 %d 0\n') % (self.labelList[idx],rect[0],rect[1],rect[2],rect[3],mask))
        
        fOut.close()
        
    def SwapXY(self):
        if 0 <=self.startX < self.wid-1 and 0<= self.endX<self.wid-1 and 0<= self.startY < self.hgt-1 and 0<= self.endY<self.hgt-1:
            if self.startX > self.endX:
                self.startX, self.endX = self.endX, self.startX
            if self.startY > self.endY:
                self.startY, self.endY = self.endY, self.startY
        elif self.endX < 0:       
             self.endX = 0
             self.startX, self.endX = self.endX, self.startX
             if self.endY < 0:
                self.endY = 0
             if self.startY > self.endY:
                self.startY, self.endY = self.endY, self.startY
        elif self.endX > self.wid - 1:
             self.endX = self.wid - 1
             if self.endY < 0:
                self.endY = 0
             if self.startY > self.endY:
                self.startY, self.endY = self.endY, self.startY
        if self.endY < 0:
           self.endY = 0
           self.startY, self.endY = self.endY, self.startY
           if self.endX < 0:
              self.endX = 0
           if self.startX > self.endX:
              self.startX, self.endX = self.endX, self.startX
        elif self.endY > self.hgt - 1:
             self.endY = self.hgt - 1
             if self.endX > self.wid - 1:
                self.endX = self.wid - 1
             if self.startX > self.endX:
                self.startX, self.endX = self.endX, self.startX