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
        # cap=cv2.VideoCapture("http://192.168.8.44:8080/stream?topic=/camera/rgb/image_raw")
        template_A = self.template_A
        template_B = self.template_B
        template_C = self.template_C

        # 开始用摄像头读数据，返回hx为true则表示读成功，frame为读的图像
        # hx, image = cap.read()
        hx=True
        image = cv2.imread("D:/RobotCar/myCode/alphabet/aera2.jpg")

        # 如果hx为Flase表示开启摄像头失败，那么就输出"read vido error"并退出程序
        if hx is False:
            # 打印报错
            print('read video error')
            # 退出程序
            exit(0)

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 设置匹配阈值
        threshold = 0.8

        for i in range(len(template_A)):
            # 模板匹配
            locations_A = self.template_matching(image_gray, template_A[i], threshold)
            locations_B = self.template_matching(image_gray, template_B[i], threshold)
            locations_C= self.template_matching(image_gray, template_C[i], threshold)
            if (len(locations_A) >0 and len(locations_B)>0 and len(locations_C) >0):
                break
        if(len(locations_A) + len(locations_B)  + len(locations_C) >=3):
            xA = [row[0] for row in locations_A]
            yA = [row[1] for row in locations_A]
            xB = [row[0] for row in locations_B]
            yB = [row[1] for row in locations_B]
            xC = [row[0] for row in locations_C]
            yC = [row[1] for row in locations_C]
            xMax = max(xA + xB + xC)
            xMin = min(xA + xB + xC)
            yMax = max(yA + yB + yC)
            yMin = min(yA + yB + yC)
            rxA = [1 if x > (xMax + xMin) / 2 else 0 for x in xA]
            rxB = [1 if x > (xMax + xMin) / 2 else 0 for x in xB]
            rxC = [1 if x > (xMax + xMin) / 2 else 0 for x in xC]

            ryA = [1 if x > (yMax + yMin) / 2 else 0 for x in yA]
            ryB = [1 if x > (yMax + yMin) / 2 else 0 for x in yB]
            ryC = [1 if x > (yMax + yMin) / 2 else 0 for x in yC]

            lA = [x + 2 * y for x, y in zip(rxA, ryA)]
            lB = [x + 2 * y for x, y in zip(rxB, ryB)]
            lC = [x + 2 * y for x, y in zip(rxC, ryC)]

            locateList = ["0"] * 4
            for index in lA:
                locateList[index] = "A"
            for index in lB:
                locateList[index] = "B"
            for index in lC:
                locateList[index] = "C"

            locateResult = ""
            for i in range(3, -1, -1):
                locateResult += "{}:{}|".format(i + 1, locateList[i])
            locateResult = locateResult[0:-1]

            print(locateResult)
            # aera1_crop = image
            # cv2.imshow('aera1_crop', aera1_crop)
            # cv2.imwrite("D:/RobotCar/result1/alphabet/aera12.jpg", aera1_crop)

            # 绘制结果
            w, h = template_A[i].shape[::-1]
            for loc in locations_A:
                cv2.rectangle(image, loc, (loc[0] + w, loc[1] + h), (0, 0, 255), 2)
                cv2.putText(image, 'A', (loc[0], loc[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            w, h = template_B[i].shape[::-1]
            for loc in locations_B:
                cv2.rectangle(image, loc, (loc[0] + w, loc[1] + h), (0, 255, 0), 2)
                cv2.putText(image, 'B', (loc[0], loc[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            w, h = template_C[i].shape[::-1]
            for loc in locations_C:
                cv2.rectangle(image, loc, (loc[0] + w, loc[1] + h), (255, 0, 0), 2)
                cv2.putText(image, 'C', (loc[0], loc[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # 显示结果
            cv2.imshow('Detected Letters', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            return locateResult
        # aera1_crop = image
        # cv2.imshow('Detected Letters', image)
        # cv2.imshow('aera1_crop', aera1_crop)
        # cv2.imwrite("D:/RobotCar/result1/alphabet/aera12.jpg", aera1_crop)
        print("False to read Pic")

        return "False"

if __name__ == "__main__":
    obj =  IdentifyPic()
    result=obj.getPic()
    print(""+result)
