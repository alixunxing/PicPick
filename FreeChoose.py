# -*- coding: cp936 -*-
"""
@Create: 2015/7/8
@author: Tang Yu-Jia
"""
import cv2


class CFreeChoose:
    def __init__(self):
        self.startX = self.startY = -1
        self.endX = self.endY = -1

        self.copyImg = None
        self.saveImg = None
        self.rectParas = []
        self.saveRect = False

        
    def DrawRectangle(self,event,x,y,flags,param):
        """
        功能：鼠标响应处理函数，响应鼠标左键按下，左键拖拽，左键松开，右键按下，右键拖拽，右键松开。
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            self.startX = x
            self.startY = y
        elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
            self.saveRect = True
            self.copyImg = self.saveImg.copy()
            self.endX = x
            self.endY = y
            cv2.circle(self.copyImg,((self.endX-self.startX)/2+self.startX,\
            (self.endY-self.startY)/2+self.startY),3,(0,255,0),-1)
            cv2.rectangle(self.copyImg,(self.startX,self.startY),(self.endX,\
            self.endY),(0,255,0),3)
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
            cv2.circle(self.copyImg,((self.endX-self.startX)/2+self.startX,\
            (self.endY-self.startY)/2+self.startY),3,(255,0,0),-1)
            cv2.rectangle(self.copyImg,(self.startX,self.startY),(self.endX,\
            self.endY),(255,0,0),3)
            cv2.imshow(self.imgName,self.copyImg)
        elif event == cv2.EVENT_RBUTTONUP:
            self.saveImg = self.copyImg.copy()
            self.rectParas.append([self.startX,self.startY,self.endX,self.endY\
            ,1])
        
    
    def PicturePicPick(self,img,imgName):
        """
        功能：图片操作。
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
        功能：根据坐标参数画框。
        """
        for rectPara in self.rectParas:
            if rectPara[4] == 0:
                cv2.circle(self.saveImg,((rectPara[2]-rectPara[0])\
                /2+rectPara[0],(rectPara[3]-rectPara[1])/2+\
                rectPara[1]),3,(0,255,0),-1)
                cv2.rectangle(self.saveImg,(rectPara[0],\
                rectPara[1]),(rectPara[2],rectPara[3]),(0,255,0),3)
            if rectPara[4] == 1:
                cv2.circle(self.saveImg,((rectPara[2]-rectPara[0])\
                /2+rectPara[0],(rectPara[3]-rectPara[1])/2+\
                rectPara[1]),3,(255,0,0),-1)
                cv2.rectangle(self.saveImg,(rectPara[0],rectPara[1]),\
                (rectPara[2],rectPara[3]),(255,0,0),3)

            
            
        
            
        
