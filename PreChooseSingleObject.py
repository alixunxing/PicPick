"""
@Create: 2015/7/8
@author: Tang Yu-Jia
"""
import os
import cv2

class CPreChooseSingleObject:
    def __init__(self):        
        self.startX = self.startY = -1
        self.endX = self.endY = -1
        self.width = self.height = 0
        self.isAppRect = False # Is a Rect appended into list right now?
        self.roiPointList = list() # start point and end point
        self.maskList = list() # len(mask) == len(roiPointList)
        self.color_green = (0, 255, 0)

        self.roiPointList = list()
        self.maskList = list()
        self.saveRect = False
   
    def InputInfo(self, img, imgName, state, label, SavePathDict, VisualParamDict):
        '''
        the 'clean' image without any drawing and the image title(a.k. the state) is inputted by this function
        '''
        self.img = img
        self.imgName = imgName
        self.state = state
        self.label = label
        self.SavePathDict = SavePathDict
        self.lineThickness = VisualParamDict['LineThickness']

    def InitVar(self):
        self.roiPointList  = list()
        self.maskList = list()        
        
    def OnMouse(self,event,x,y,flags,param):
        """
        drag mouse: LButton to click object, RButton to draw pre-choose
        """
        if event == cv2.EVENT_RBUTTONDOWN:
            self.startX = x
            self.startY = y
        elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON:
            self.isAppRect = True
            self.imgTmp = self.img.copy()
            self.endX = x
            self.endY = y

            cv2.circle(self.imgTmp,(int((self.endX-self.startX)/2+self.startX), int((self.endY-self.startY)/2+self.startY)),self.lineThickness,self.color_green,-1)
            cv2.rectangle(self.imgTmp,(self.startX,self.startY),(self.endX, self.endY), self.color_green, self.lineThickness)
            cv2.imshow(self.state, self.imgTmp)
        elif event == cv2.EVENT_RBUTTONUP:
            if self.isAppRect and self.startX != self.endX and self.startY !=self.endY:
                ###### if drawing started from the right-bottom, swap(startPoint, endPoint)
                if self.startX > self.endX:
                    self.startX, self.endX = self.endX, self.startX
                    self.startY, self.endY = self.endY, self.startY
                self.roiPointList = [self.startX, self.startY, self.endX, self.endY]
                self.maskList = 0
                self.width = self.endX - self.startX
                self.height = self.endY - self.startY
                self.isAppRect = False
        if event == cv2.EVENT_LBUTTONDOWN:
            self.InitVar()
            self.imgCurrent = self.img.copy()
            self.startX = x - self.width/2
            self.startY = y - self.height/2
            self.endX = x + self.width/2
            self.endY = y + self.height/2
            cv2.circle(self.imgCurrent, (x, y), self.lineThickness, self.color_green, -1)
            cv2.rectangle(self.imgCurrent, (self.startX, self.startY), (self.endX, self.endY), self.color_green, self.lineThickness)
            cv2.imshow(self.state, self.imgCurrent)

    def PicturePicPick(self):
        """
        Pick objects on pictures!!!
        """
        self.InitVar()
        self.imgCurrent = self.img.copy()
        cv2.imshow(self.state, self.imgCurrent)

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

    def VideoPicPick(self):
        """
        Pick objects on video!!! 
        VideoPicPick has 'front' operation while PicturePicPick doesn't.
        """
        self.InitVar()
        self.imgCurrent = self.img.copy()
        cv2.imshow(self.state, self.imgCurrent)

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
            if keyInput == ord('f'):
                flag = 'front'
                break
        def Roi2Rect(roiList):
            rectList = list()
            for roi in roiList:
                rect = [roi[0], roi[1], roi[2]-roi[0]+1, roi[3]-roi[1]+1]
                rectList.append(rect)
            return rectList
        self.rectList = Roi2Rect(self.roiPointList)
        return self.rectList, self.maskList, flag

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
            else: # if maskList = [], draw init MSER results
                cv2.rectangle(self.imgChar,(roiPoint[0],roiPoint[1]),(roiPoint[2],roiPoint[3]),self.color_violet,self.lineThickness)
    
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