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
        self.saveImg = None
        self.copyImg = None
        self.saveRect = False
        
    def InputInfo(self, imgName, txtName):
        self.imgName = imgName
        self.txtName = txtName

    def Check(self):
        pass
        
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
                cv2.imshow(self.imgName,self.copyImg)
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
                    if startX<=x<=endX and startY<=y<=endY:
                        cv2.circle(self.saveImg,(startX+(endX-startX)/2,startY+(endY-startY)/2),self.thickness,(0,0,255),-1)
                        cv2.rectangle(self.saveImg,(startX,startY),(endX,endY),(0,0,255),self.thickness)
                        self.rectParas.remove(rectPara)
                cv2.imshow(self.imgName,self.saveImg)
                    

    def ShowResult(self,img,rectParas,imgName):
        """
        功能：根据gt显示截图结果。
        """
        self.imgName=imgName
        cv2.setMouseCallback(imgName,self.DrawOrDelRectangle)
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
                cv2.imshow(imgName,self.saveImg)
            if keyInput == ord('r'):
                self.picModel = True
            if keyInput == ord(' '):               
                break
            if keyInput == 27:
                return 'exit'
            if keyInput == ord('b'):
                return 'back'
        return self.rectParas
                    
        
    def DrawRectangles(self):
        """
        功能：根据坐标参数画框。
        """
        for rectPara in self.rectParas:
            startX = rectPara[0]
            startY = rectPara[1]
            endX = rectPara[2]
            endY = rectPara[3]
            mask = rectPara[4]
            if mask == 0:
                cv2.circle(self.saveImg,(startX+(endX-startX)/2,startY + (endY-startY)/2),self.thickness,(0,255,0),-1)
                cv2.rectangle(self.saveImg,(startX,startY),(endX,endY), (0,255,0),self.thickness)
            if mask == 1:
                cv2.circle(self.saveImg,(startX+(endX-startX)/2,startY+ (endY-startY)/2),self.thickness,(255,0,0),-1)
                cv2.rectangle(self.saveImg,(startX,startY),(endX,endY), (255,0,0),self.thickness)
        
