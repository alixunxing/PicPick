"""
@Create: 2015/7/8
@author: Tang Yu-Jia
"""
import cv2

class CCheckGt:
    def __init__(self, CheckPathDict):
        self.CheckPathDict = CheckPathDict
        self.startX = self.startY = -1
        self.endX = self.endY = -1
        self.width = self.height = 0
        self.isChoose = False # Is opened choose mode?
        self.isDelete = False # Is opened delete mode?
        self.isAppRect = False # Is a Rect appended into list right now?
        self.roiPointList = list() # start point and end point
        self.maskList = list() # len(mask) == len(roiPointList)
        self.color_blue  = (255, 0, 0)
        self.color_green = (0, 255, 0)
        self.color_red   = (0, 0, 255)
        self.roiPointList = list()
        self.maskList = list()
   
    def InputInfo(self, imgName, txtName, state, VisualParamDict):
        '''
        the 'clean' image without any drawing and the image title(a.k. the state) is inputted by this function
        '''
        self.imgName = imgName
        self.txtName = txtName
        self.state = state
        self.lineThickness = VisualParamDict['LineThickness']

    def InitVar(self):
        self.roiPointList  = list()
        self.maskList = list()

    def Check(self):
        self.img = cv2.imread(self.imgName)
        self.imgCurrent = self.img.copy()
        with open(self.txtName, 'r') as fin:
            lines = fin.readlines()
            assert lines

        self.LinesToRoiList(lines)
        self.DrawRoiList(self.roiPointList, self.maskList)
        cv2.imshow(self.state, self.imgCurrent)

        cv2.setMouseCallback(self.state, self.OnMouse)
        while True:
            keyInput = cv2.waitKey(0)
            if keyInput == ord('d'): # Delete mode
                self.isDelete = True
                self.isChoose = False
            if keyInput == 9: # Tab mode
                self.isDelete = False
                self.isChoose = True
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
        for line in lines[1:]:
            line = line.split()
            self.label = line[0]
            self.roiPointList.append([int(line[1]), int(line[2]), int(line[1])+int(line[3]), int(line[2])+int(line[4])])
            self.maskList.append(int(line[-2]))
        
    def OnMouse(self, event, x, y, flags, param):
        """
        input 'd' to get into delete mode, one can choose bbox to delete
        input 'tab' to get into choose mode, one can draw object or mask
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
                    self.imgCurrent = self.imgTmp.copy()
                    ###### if drawing started from the right-bottom, swap(startPoint, endPoint)
                    if self.startX > self.endX:
                        self.startX, self.endX = self.endX, self.startX
                        self.startY, self.endY = self.endY, self.startY
                    self.roiPointList.append([self.startX, self.startY, self.endX, self.endY])
                    self.maskList.append(0)
                    self.isAppRect = False
                    self.isChoose = False
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
                    self.imgCurrent = self.imgTmp.copy()
                    ###### if drawing started from the right-bottom, swap(startPoint, endPoint)
                    if self.startX > self.endX:
                        self.startX,self.endX = self.endX,self.startX
                        self.startY,self.endY = self.endY,self.startY
                    self.roiPointList.append([self.startX, self.startY, self.endX, self.endY])
                    self.maskList.append(1)
                    self.isAppRect = False
                    self.isChoose = False
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
                        cv2.imshow(self.state, self.imgCurrent)
            elif event == cv2.EVENT_LBUTTONUP:
                self.isDelete = False
                self.imgCurrent = self.img.copy()
                self.DrawRoiList(self.roiPointList, self.maskList)
                cv2.imshow(self.state, self.imgCurrent)
           
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
        for idx, mask in enumerate(self.maskList):
            rect = rectList[idx]
            ###save objects
            if mask ==0:
                objectImg = self.img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
                cv2.imwrite(os.path.join(self.SavePathDict['objPath'], os.path.splitext(self.imgName)[0]+'_'+str(objNum)+'.png'), objectImg)
                objNum += 1
            ###save labeled ground truth
            fOut.write(('%s %d %d %d %d 0 0 0 0 0 %d 0\n') % (self.label,rect[0],rect[1],rect[2],rect[3],mask))
        
        fOut.close()