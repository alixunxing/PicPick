# -*- coding: cp936 -*-
"""
@Create: 2015/7/8
@author: Tang Yu-Jia
"""
import cv2

class CPreChooseSingleObject:
    def __init__(self,):        
        self.img = None
        
        self.startX = self.startY = -1
        self.savePic = False
        self.endX = self.endY = -1
        self.centerX = self.centerY = -1
        self.width = self.height = 0
        
        
    def DrawRectangle(self,event,x,y,flags,param):
        """
        功能：鼠标响应处理函数，响应鼠标左键按下，右键按下，右键移动拖拽。
        """
        if event == cv2.EVENT_RBUTTONDOWN:
            self.startX = x
            self.startY = y
        if event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON:
            self.savePic = True
            self.changeRect = True
            copyImg = self.img.copy()
            self.endX = x
            self.endY = y
            cv2.circle(copyImg,((self.endX-self.startX)/2+self.startX, (self.endY-self.startY)/2+self.startY),2,(0,255,0),-1)
            cv2.rectangle(copyImg,(self.startX,self.startY),(self.endX, self.endY),(0,255,0),2)
            cv2.imshow('image',copyImg)
        if event == cv2.EVENT_RBUTTONUP:
            self.width = abs(self.endX - self.startX)
            self.height = abs(self.endY - self.startY)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.savePic = True
            copyImg = self.img.copy()
            self.centerX = x
            self.centerY = y
            self.startX = self.centerX - self.width/2
            self.startY = self.centerY - self.height/2
            self.endX =  self.centerX + self.width/2
            self.endY = self.centerY + self.height/2
            cv2.circle(copyImg,(x,y),2,(255,0,0),-1)
            cv2.rectangle(copyImg,(self.startX,self.startY),(self.endX,self.endY),(255,0,0),2)
            cv2.imshow('image',copyImg)
            
                
    def PicturePicPick(self,img):
        """
        功能:图片操作。
        """
        self.img = img
        cv2.setMouseCallback('image',self.DrawRectangle)
        cv2.imshow('image',self.img)
        while(1):
            keyInput = cv2.waitKey(0)
            if keyInput == 27:
                return 'exit'
            if keyInput == ord(' '):
                break
        if self.startX > self.endX:
            self.startX,self.endX = self.endX,self.startX
            self.startY,self.endY = self.endY,self.startY
        rect = [self.startX,self.startY,self.width,self.height,0]
        objectImg = self.img[self.startY:self.endY,self.startX:self.endX]
        if self.savePic == True:
            return [objectImg,rect]
            self.savePic == False
        else:
            return []

        
        
    def VideoPicPick(self,cap,currentPos):
        """
        功能：视频操作。
        """
        forwardFrameRate = 5
        CV_CAP_PROP_POS_FRAMES = 1
        CV_CAP_PROP_FRAME_COUNT = 7 
        cv2.setMouseCallback('image',self.DrawRectangle)
        cap.set(CV_CAP_PROP_POS_FRAMES,currentPos-1)
        ret,self.img = cap.read()
        while ret == True:
            saveImg = self.img.copy()
            cv2.imshow('image',self.img)                
            keyInput = cv2.waitKey(0)
            if keyInput != ord(' ') and keyInput != ord('f') and keyInput != ord('b') and keyInput != ord('d') and keyInput != 27:
                continue
            if keyInput == ord(' '):
                ret,self.img = cap.read()
            if keyInput == ord('f'):
                if cap.get(CV_CAP_PROP_POS_FRAMES)+forwardFrameRate>cap.get(CV_CAP_PROP_FRAME_COUNT):
                    return []
                for i in range(5):
                    ret,self.img = cap.read()
            if keyInput == ord('b'):
                currentPos = cap.get(CV_CAP_PROP_POS_FRAMES)
                cap.set(CV_CAP_PROP_POS_FRAMES,currentPos-forwardFrameRate-1)
                ret,self.img = cap.read()
            if keyInput == 27:
                return []
            if keyInput == ord('d'):
                self.savePic = False
            if self.startX > self.endX:
                self.startX,self.endX = self.endX,self.startX
                self.startY,self.endY = self.endY,self.startY
            rect = [self.startX,self.startY,self.width,self.height,0]
            objectImg = saveImg[self.startY:self.endY,self.startX:self.endX]
            if  self.savePic == True:
                self.savePic = False
                return [objectImg,rect,cap.get(CV_CAP_PROP_POS_FRAMES),saveImg]

        
        

            
    
            
        
            
            
        
                
            
            