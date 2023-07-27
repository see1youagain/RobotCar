#!/usr/bin/python
# -*- coding:utf8 -*-
import cv2
import numpy as np
import time
import os

class IdentifyPic():
    def __init__(self):
        # 读取模板图像
        template_A = []
        template_B = []
        template_C = []
        folder_pathA = 'D:/RobotCar/result1/alphabet/A'
        filesA = os.listdir(folder_pathA)
        folder_pathB = 'D:/RobotCar/result1/alphabet/B'
        filesB = os.listdir(folder_pathB)
        folder_pathC = 'D:/RobotCar/result1/alphabet/C'
        filesC = os.listdir(folder_pathC)

        jpg_filesA = [file for file in filesA if file.lower().endswith('.jpg')]
        for jpg_file in jpg_filesA:
            file_path = os.path.join(folder_pathA, jpg_file)
            # 在这里处理图片，例如显示图片
            template_A.append(cv2.imread(file_path, cv2.IMREAD_GRAYSCALE))

        jpg_filesB = [file for file in filesB if file.lower().endswith('.jpg')]
        for jpg_file in jpg_filesB:
            file_path = os.path.join(folder_pathB, jpg_file)
            # 在这里处理图片，例如显示图片
            template_B.append(cv2.imread(file_path, cv2.IMREAD_GRAYSCALE))

        jpg_filesC = [file for file in filesC if file.lower().endswith('.jpg')]
        for jpg_file in jpg_filesC:
            file_path = os.path.join(folder_pathC, jpg_file)
            # 在这里处理图片，例如显示图片
            template_C.append(cv2.imread(file_path, cv2.IMREAD_GRAYSCALE))


        self.template_A=template_A
        self.template_B=template_B
        self.template_C=template_C


    def template_matching(self, image_gray, template, threshold):
        res = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(res >= threshold)
        return list(zip(*locations[::-1]))


    def getPic(self):
        cap=cv2.VideoCapture("http://192.168.8.44:8080/stream?topic=/camera/rgb/image_raw")

        # 开始用摄像头读数据，返回hx为true则表示读成功，frame为读的图像
        hx, image = cap.read()

        # 如果hx为Flase表示开启摄像头失败，那么就输出"read vido error"并退出程序
        if hx is False:
            # 打印报错
            print('read video error')
            # 退出程序
            exit(0)
        aera1_crop = image
        cv2.imshow('Detected Letters', image)
        cv2.imshow('aera1_crop', aera1_crop)
        cv2.imwrite("D:/RobotCar/result1/alphabet/num9.jpg", aera1_crop)
        return "False"

if __name__ == "__main__":
    obj =  IdentifyPic()
    result=obj.getPic()
    print(""+result)
