"""
@Create: 2015/7/8
@author: Tang Yu-Jia
"""
import cv2


class CFreeChoose:
    def __init__(self):
        self.startX = self.startY = -1
        self.savePic = False
        self.endX = self.endY = -1
        self.width = self.height = 0
        self.isAppRect = False # Is a Rect appended into list right now?
        self.roiPointList = list() # start point and end point
        self.maskList = list() # len(mask) == len(roiPointList)
        self.color_blue  = (255, 0, 0)
        self.color_green = (0, 255, 0)

        self.roiPointList = list()
        self.maskList = list()
        self.rectParas = []
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
        
    def OnMouse(self,event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.startX = x
            self.startY = y
        elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
            self.saveRect = True
            self.copyImg = self.saveImg.copy()
            self.endX = x
            self.endY = y
            cv2.circle(self.imgTmp,(int((self.endX-self.startX)/2+self.startX), int((self.endY-self.startY)/2+self.startY)),self.lineThickness,self.color_green,-1)
            cv2.rectangle(self.imgTmp,(self.startX,self.startY),(self.endX, self.endY),self.color_green,self.lineThickness)
            cv2.imshow(self.state, self.imgTmp)
        elif event == cv2.EVENT_LBUTTONUP:
            self.saveImg = self.copyImg.copy()
            if self.saveRect == True:
                self.rectParas.append([self.startX,self.startY,self.endX,self.endY,0])
                self.saveRect = False
        if event == cv2.EVENT_RBUTTONDOWN:
            self.startX = x
            self.startY = y
        elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON:
            self.copyImg = self.saveImg.copy()
            self.endX = x
            self.endY = y

            cv2.circle(self.imgTmp,(int((self.endX-self.startX)/2+self.startX), int((self.endY-self.startY)/2+self.startY)),self.lineThickness,self.color_blue,-1)
            cv2.rectangle(self.imgTmp,(self.startX,self.startY),(self.endX, self.endY), self.color_blue,self.lineThickness)
            cv2.imshow(self.state, self.imgTmp)
        elif event == cv2.EVENT_RBUTTONUP:
            self.saveImg = self.copyImg.copy()
            self.rectParas.append([self.startX,self.startY,self.endX,self.endY,1])
        
    
    def PicturePicPick(self,img,imgName):
        """
        
        """
        self.saveImg = img.copy()
        self.imgName=imgName
        self.rectParas = []
        cv2.setMouseCallback(imgName,self.DrawRectangle)
        #self.rectParas = []
        cv2.imshow(imgName,img) 
        while(1):
            keyInput = cv2.waitKey(0)
            if keyInput == 27:
                return 'exit'
            if keyInput == ord('d'):
                self.saveImg = img.copy()
                if self.rectParas != []:
                    self.rectParas.pop()
                    self.DrawRectangles()
                cv2.imshow(imgName,self.saveImg)
            if keyInput == ord(' '):
                break
            if keyInput == ord('b'):
                return 'back'
        return self.rectParas


        
    def VideoPicPick(self,cap,currentPos):
        """
        
        """
        forwardFrameRate = 5
        CV_CAP_PROP_POS_FRAMES = 1
        CV_CAP_PROP_FRAME_COUNT = 7
        cv2.setMouseCallback('image',self.DrawRectangle)
        cap.set(CV_CAP_PROP_POS_FRAMES,currentPos-1)
        self.rectParas = []
        ret,img = cap.read()
        while ret == True:
            saveImg = img.copy()
            self.saveImg = img.copy()
            cv2.imshow('image',img)
            keyInput = cv2.waitKey(0)
            if keyInput == ord(' '):
                ret,img = cap.read()
            if keyInput == ord('f'):
                if cap.get(CV_CAP_PROP_POS_FRAMES)+forwardFrameRate>cap.get(CV_CAP_PROP_FRAME_COUNT):
                    return [],[],0
                for i in range(5):
                    ret,img = cap.read()
            if keyInput == ord('b'):
                currentPos = cap.get(CV_CAP_PROP_POS_FRAMES)
                cap.set(CV_CAP_PROP_POS_FRAMES,currentPos-forwardFrameRate -1)
                ret,img = cap.read()
            if keyInput == 27:
                return [],[],0
            if keyInput == ord('d'):
                self.saveImg = img.copy()
                if self.rectParas != []:
                    self.rectParas.pop()
                    self.DrawRectangles()
                cv2.imshow('image',self.saveImg)
                while 1:
                    if self.rectParas == []:
                        break
                    keyInput = cv2.waitKey(0)
                    if keyInput != ord('d') and keyInput != ord(' '):
                        cv2.imshow('image',self.saveImg)
                    if keyInput == ord('d'):
                        self.saveImg = img.copy()
                        if self.rectParas != []:
                            self.rectParas.pop()
                            self.DrawRectangles()
                        cv2.imshow('image',self.saveImg)                       
                    if keyInput == ord(' '):
                        ret,img = cap.read()
                        break
            if self.rectParas != []:
                return saveImg,self.rectParas,cap.get(CV_CAP_PROP_POS_FRAMES)
            if cap.get(CV_CAP_PROP_POS_FRAMES)+1 > cap.get(CV_CAP_PROP_FRAME_COUNT):
                return [],[],0
                
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


            
            
        
            
        
