# -*- coding: cp936 -*-
"""
@Create: 2015/7/8
@author: Tang Yu-Jia
"""
import cv2

class CPreChooseMultiObject:
    def __init__(self):
        self.startX,self.startY = -1,-1
        self.endX,self.endY = -1,-1
        self.centerX,self.centerY = -1,-1
        
        self.copyImg = None
        self.saveImg = None
        self.rectParas = []
        self.saveRect = False
    
    
    def DrawRectangle(self,event,x,y,flags,param):
        """
        功能：鼠标响应函数
        """
        if event == cv2.EVENT_RBUTTONDOWN:
            self.startX = x
            self.startY = y
        if event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON:
            self.saveRect = True
            self.copyImg = self.saveImg.copy()
            self.endX = x
            self.endY = y
            cv2.circle(self.copyImg,((self.endX-self.startX)/2+self.startX,\
            (self.endY-self.startY)/2+self.startY),2,(0,255,0),-1)
            cv2.rectangle(self.copyImg,(self.startX,self.startY),(self.endX,\
            self.endY),(0,255,0),2)
            cv2.imshow('image',self.copyImg)
        if event == cv2.EVENT_RBUTTONUP:
            self.width = abs(self.endX - self.startX)
            self.height = abs(self.endY - self.startY)
            self.saveImg = self.copyImg.copy()
            self.rectParas.append([self.startX,self.startY,self.endX,self.endY\
            ,0])
        if event == cv2.EVENT_LBUTTONDOWN:
            self.copyImg = self.saveImg.copy()
            self.centerX = x
            self.centerY = y
            self.startX = self.centerX - self.width/2
            self.startY = self.centerY - self.height/2
            self.endX =  self.centerX + self.width/2
            self.endY = self.centerY + self.height/2
            cv2.circle(self.copyImg,(x,y),2,(255,0,0),-1)
            cv2.rectangle(self.copyImg,(self.startX,self.startY),(self.endX,\
            self.endY),(255,0,0),2)
            cv2.imshow('image',self.copyImg)
        if event == cv2.EVENT_LBUTTONUP:
            self.saveImg = self.copyImg.copy()
            if self.saveRect == True:
                self.rectParas.append([self.startX,self.startY,self.endX,self.endY\
                ,0])


    def PicturePicPick(self,img):
        """
        功能：图片操作
        """
        self.saveImg = img.copy()
        cv2.setMouseCallback('image',self.DrawRectangle)
        self.rectParas = []
        cv2.imshow('image',img)
        while(1):
            keyInput = cv2.waitKey(0)
            if keyInput == ord('d'):
                self.saveImg = img.copy()
                if self.rectParas != []:
                    self.rectParas.pop()
                    self.DrawRectangles()
                cv2.imshow('image',self.saveImg)
            if keyInput == 27:
                return 'exit'
            if keyInput == ord(' '):
                break
        return self.rectParas
            
            
    def VideoPicPick(self,cap,currentPos):
        """
        功能：视频操作。
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
        
            
    def DrawRectangles(self):
        """
        功能：根据截图参数画框。
        """
        for rectPara in self.rectParas:
            if rectPara[4] == 0:
                cv2.circle(self.saveImg,((rectPara[2]-rectPara[0])\
                /2+rectPara[0],(rectPara[3]-rectPara[1])/2+\
                rectPara[1]),2,(255,0,0),-1)
                cv2.rectangle(self.saveImg,(rectPara[0],\
                rectPara[1]),(rectPara[2],rectPara[3]),(255,0,0),2)
            
            
            
            
            
            
            
            
            
            
            
            
        
