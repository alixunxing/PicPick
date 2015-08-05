"""
@Create: 2015/7/8
@author: Tang Yu-Jia
"""
from __future__ import division
import cv2
import numpy as np
import math
import os

class CBoxMerge:
    def _init_(self):
        pass
        
    def BBoxMerge(self, bboxesRaw, overlap=0.9):
        bboxes = list()
        flag   = [True]*len(bboxesRaw) # True - no need merge
                                       # False - need merge
        for i in range(len(bboxesRaw)-1):
            if flag[i] == True:
                for j in range(i+1,len(bboxesRaw)):
                    if flag[j] == True:
                        if self.isIn(bboxesRaw[i],bboxesRaw[j],overlap) == 1:
                            flag[i] = False
                            break
                        elif self.isIn(bboxesRaw[i],bboxesRaw[j],overlap) == 2:
                            flag[j] = False
                            continue
                        elif self.isIn(bboxesRaw[i],bboxesRaw[j],overlap) == None:
                            continue
                        else:
                            assert True
            if flag[i] == True:
                bboxes.append(bboxesRaw[i])
        return bboxes
        
    def isIn(self, bbox1, bbox2, overlap):
    
        startX = max(bbox1[0],bbox2[0])
        startY = max(bbox1[1],bbox2[1])
        endX   = min(bbox1[0]+bbox1[2],bbox2[0]+bbox2[2])
        endY   = min(bbox1[1]+bbox1[3],bbox2[1]+bbox2[3])
        
        if startX < endX and startY < endY:
            area = (endX - startX)*(endY - startY)
            area1= bbox1[2]*bbox1[3]
            area2= bbox2[2]*bbox2[3]
            if area/area1 > overlap or area/area2 > overlap:
                return 1 if area/area1 > area/area2 else 2    # 1 - b1 in b2
                                                              # 2 - b2 in b1
            else:
                return None
        else:
            return None

class CCharacterPick:
    ############################################################################################
    ###
    ###  self.img -> input raw image
    ###  self.imgCurrent -> current image with rectangle drawings
    ###  self.imgTmp -> when you drag mouse the dragging rectangle is drawed on self.imgTmp
    ###
    ############################################################################################
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
        self.color_violet= (211,0,148)
        self.threshold = 0.8
   
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
        self.roiPointList = list()
        self.charRoiList = list() 
        self.maskList = list()


    def InitVar(self):
        self.roiPointList  = list()
        self.maskList = list()
         
    def PicturePicPick(self):
        """
        Pick objects on pictures!!!
        """
        self.InitVar()
        self.imgCurrent = self.img.copy()
        charRectList = self.CharSegmentation(self.img)
        def Rect2Roi(rectList):
            roiList = list()
            for rect in rectList:
                roi = [rect[0], rect[1], rect[2]+rect[0]-1, rect[3]+rect[1]-1]
                roiList.append(roi)
            return roiList
        self.charRoiList = Rect2Roi(charRectList)
        self.DrawRoiList(self.charRoiList, False)
        cv2.imshow(self.state,self.imgCurrent)
        cv2.setMouseCallback(self.state, self.OnMouse)
        while True:
            keyInput = cv2.waitKey(0)
            if keyInput == ord('d'):
                if self.roiPointList:
                    self.imgCurrent = self.img.copy()
                    self.roiPointList.pop()
                    self.maskList.pop()
                    self.DrawRoiList(self.charRoiList, False)
                    self.DrawRoiList()
                cv2.imshow(self.state, self.imgCurrent)
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

    def OnMouse(self,event,x,y,flags,param):
        """
        drag mouse: LButton to draw object, RButton to draw mask, DBClick mser bbox to choose object
        """
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
            self.imgCurrent = self.imgTmp.copy()
            if self.isAppRect and self.startX != self.endX and self.startY !=self.endY:
                ###### if drawing started from the right-bottom, swap(startPoint, endPoint)
                if self.startX > self.endX:
                    self.startX,self.endX = self.endX,self.startX
                    self.startY,self.endY = self.endY,self.startY
                subImg = self.img[self.startY:self.endY, self.startX:self.endX]
                self.roiPointList.append([self.startX,self.startY,self.endX,self.endY])
                self.maskList.append(0)
                self.isAppRect = False
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
            self.imgCurrent = self.imgTmp.copy()
            if self.isAppRect and self.startX != self.endX and self.startY !=self.endY:
                ###### if drawing started from the right-bottom, swap(startPoint, endPoint)
                if self.startX > self.endX:
                    self.startX,self.endX = self.endX,self.startX
                    self.startY,self.endY = self.endY,self.startY
                self.roiPointList.append([self.startX,self.startY,self.endX,self.endY])
                self.maskList.append(1)
                self.isAppRect = False
        if event == cv2.EVENT_LBUTTONDBLCLK:
            self.imgTmp = self.imgCurrent.copy()
            for charRoi in self.charRoiList:
                startX = charRoi[0]
                startY = charRoi[1]
                endX   = charRoi[2]
                endY   = charRoi[3]
                if (startX < x < endX) and (startY < y < endY):
                    self.roiPointList.append(charRoi)
                    self.maskList.append(0)
                    cv2.circle(self.imgTmp, (int((endX-startX)/2+startX), int((endY-startY)/2+startY)), self.lineThickness, self.color_green,-1)
                    cv2.rectangle(self.imgTmp, (startX, startY),(endX, endY), self.color_green, self.lineThickness)
                    cv2.imshow(self.state, self.imgTmp)

    def DrawRoiList(self, roiPointList = list(), maskList = list()):
        """
        draw all roiPoints, including objects and masks
        """
        for idx, roiPoint in enumerate(roiPointList):
            if maskList:
                if maskList[idx] == 0:
                    cv2.circle(self.imgCurrent,(int((roiPoint[2]-roiPoint[0])/2+roiPoint[0]), int((roiPoint[3]-roiPoint[1])/2+ roiPoint[1])),self.lineThickness,self.color_green,-1)
                    cv2.rectangle(self.imgCurrent,(roiPoint[0], roiPoint[1]),(roiPoint[2],roiPoint[3]),self.color_green,3)
                elif maskList[idx] == 1:
                    cv2.circle(self.imgCurrent,(int((roiPoint[2]-roiPoint[0])/2+roiPoint[0]), int((roiPoint[3]-roiPoint[1])/2+roiPoint[1])),self.lineThickness,self.color_blue,-1)
                    cv2.rectangle(self.imgCurrent,(roiPoint[0],roiPoint[1]),(roiPoint[2],roiPoint[3]),self.color_blue,3)
            else: # if maskList = [], draw init MSER results
                cv2.rectangle(self.imgCurrent,(roiPoint[0],roiPoint[1]),(roiPoint[2],roiPoint[3]),self.color_violet,3)


    #def PicturePicPick(self, img ):
    #    """
    #    Pick objects on pictures!
    #    """
    #    cv2.setMouseCallback(self.state,self.DrawRectangle)
    #    cv2.imshow(self.state, self.img)
    #    while True:
    #        keyDict = {27:'exit', ord('b'):'back', ord(' '):'next'}
    #        keyInput = cv2.waitKey(0)
    #        flag = keyDict.get(keyInput)
    #        if flag != None:
    #            break
    #    if self.startX > self.endX:
    #        self.startX,self.endX = self.endX,self.startX
    #        self.startY,self.endY = self.endY,self.startY
    #    rect = [self.startX,self.startY,self.width,self.height,0]
    #    objectImg = self.img[self.startY:self.endY,self.startX:self.endX]
    #    if self.savePic == True:
    #        return rect, mask, flag
    #        self.savePic == False
    #    else:
    #        return []
        
    def CharSegmentation(self,subImg):
        mser = cv2.MSER_create()
        gray = cv2.cvtColor(subImg, cv2.COLOR_BGR2GRAY)

        bboxes = mser.detectRegions(gray, None)
        doMerge = CBoxMerge()
        bboxes = doMerge.BBoxMerge(bboxes, self.threshold)

        return bboxes

    #def CharSegmentation(self, img):
    #    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #    thresh = self.graythresh(imgGray)
    #    ret, imgBw = cv2.threshold(imgGray, int(255*thresh), 255, cv2.THRESH_BINARY)

    #    h, w = np.shape(imgBw)
    #    assert w==baseroiPointList[2]
    #    assert h==baseroiPointList[3]

    #    Point = (0, 0)
    #    roiPointList   = (0, 0, w, h)

    #    colSpace, colNum = self.PixelProject(Point, 'col', imgBw, roiPointList)
    #    rowSpace, rowNum = self.PixelProject(Point, 'row', imgBw, roiPointList)

    #    charPos = []
    #    textPos = []

    #    if colNum<rowNum:
    #        for col in range(len(colSpace)):
    #            rect    = (colSpace[col][0], 0, colSpace[col][1]-colSpace[col][0], h)

    #            charSpace, rowNum = self.PixelProject(Point, 'row', imgBw, rect)

    #            for char in range(len(charSpace)):
    #                pos_start = (colSpace[col][0], charSpace[char][0])
    #                pos_end   = (colSpace[col][1], charSpace[char][1])
    #                charDict   = {'pos_start':pos_start, 'pos_end':pos_end}
    #                charPos.append(charDict)

    #            pos_start = (colSpace[col][0], charSpace[0][0])
    #            pos_end   = (colSpace[col][1], charSpace[-1][1])
    #            textDict  = {'pos_start':pos_start, 'pos_end':pos_end, 'charNum':len(charPos)}
    #            textPos.append(textDict)

    #    else:
    #        for row in range(len(rowSpace)):
    #            rect = (0,rowSpace[row][0], w, rowSpace[row][1]-rowSpace[row][0]) 

    #            charSpace, rowNum = self.PixelProject(Point, 'col', imgBw, rect)

    #            for char in range(len(charSpace)):
    #                pos_start = (charSpace[char][0], rowSpace[row][0])
    #                pos_end   = (charSpace[char][1], rowSpace[row][1])
    #                charDict   = {'pos_start':pos_start, 'pos_end':pos_end}
    #                charPos.append(charDict)

    #            pos_start = (charSpace[0][0], rowSpace[row][0])
    #            pos_end   = (charSpace[-1][1], rowSpace[row][1])
    #            textDict  = {'pos_start':pos_start, 'pos_end':pos_end, 'charNum':len(charPos)}
    #            textPos.append(textDict)

    #    return charPos, textPos

    def graythresh(self,I):
        num_bins=256
        #bins = np.arange(num_bins)
        #counts=np.histogram(I,bins)
        counts=cv2.calcHist([I],[0],None,[num_bins],[0.0,255.0])

        p=counts/counts.sum()
        omega=np.cumsum(p)
        mu=np.cumsum(np.arange(1,257,1)*p.T).T
        mu_t = mu[-1]

        sigma_b_squared = (omega * mu_t - mu)**2 / (omega*(1 - omega))

        for i in range(len(sigma_b_squared)):
            if math.isnan(sigma_b_squared[i]):
                sigma_b_squared[i]=float('-Inf')

        maxval = sigma_b_squared.max()
    
        isfinite_maxval=math.isinf(maxval)
        index=[]
        if isfinite_maxval==0:
            for i in range(len(sigma_b_squared)):
                if sigma_b_squared[i]==maxval:
                    index.append(i)
            idx = sum(index)/len(index)
            level = (idx - 1) / (num_bins - 1)
        else:
            level = 0.0

        return level

    def PixelProject(self,Point,flag,imgBw,roiPointList):
        if flag == 'col':
            pixelSum = imgBw[roiPointList[1]:roiPointList[1]+roiPointList[3], roiPointList[0]:roiPointList[0]+roiPointList[2]].sum(axis=0)
            start = Point[0]
        elif flag == 'row':
            pixelSum = imgBw[roiPointList[1]:roiPointList[1]+roiPointList[3], roiPointList[0]:roiPointList[0]+roiPointList[2]].sum(axis=1)
            start = Point[1]
        else:
            assert False

        incFlag = True
        num = 0
        space = []
        for idx in range(len(pixelSum)-1):
            if pixelSum[idx]==0 and pixelSum[idx+1]>0:
                startP = start + idx + 1
                endP = start + idx
                num = num + 1
                incFlag = False
            if pixelSum[idx]>0 and pixelSum[idx+1]==0 and not incFlag:
                endP = idx
                charPos = (startP, endP)
                space.append(charPos)
                incFlag = True

        return space, num
    
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