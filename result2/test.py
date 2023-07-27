#!/usr/bin/python
# -*- coding:utf8 -*-
import cv2
import numpy as np
import time


class identifyPic():
    def __init__(self):
        self.cap = cv2.VideoCapture("http://192.168.31.70:8080/stream?topic=/camera/rgb/image_raw")
        # 读取模板图像
        self.template_A = cv2.imread("alphabet/A/image1.jpg", cv2.IMREAD_GRAYSCALE)
        self.template_B = cv2.imread("alphabet/B/image1.jpg", cv2.IMREAD_GRAYSCALE)
        self.template_C = cv2.imread("alphabet/C/image1.jpg", cv2.IMREAD_GRAYSCALE)

    def template_matching(self, image_gray, template, threshold):
        res = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(res >= threshold)
        return list(zip(*locations[::-1]))


    def getPic(self):
        cap=self.cap
        template_A = self.template_A
        template_B = self.template_B
        template_C = self.template_C

        # 开始用摄像头读数据，返回hx为true则表示读成功，frame为读的图像
        hx, image = cap.read()

        # 如果hx为Flase表示开启摄像头失败，那么就输出"read vido error"并退出程序
        if hx is False:
            # 打印报错
            print('read video error')
            # 退出程序
            exit(0)

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 设置匹配阈值
        threshold = 0.8


        # 模板匹配
        locations_A = self.template_matching(image_gray, template_A, threshold)
        locations_B = self.template_matching(image_gray, template_B, threshold)
        locations_C = self.template_matching(image_gray, template_C, threshold)

        try:
            xA = locations_A[0][0]
            yA = locations_A[0][1]
            xB = locations_B[0][0]
            yB = locations_B[0][1]
            xC = locations_C[0][0]
            yC = locations_C[0][1]
            xMax = max([xA, xB, xC])
            xMin = min([xA, xB, xC])
            yMax = max([yA, yB, yC])
            yMin = min([yA, yB, yC])

            xA = 1 if xA > (xMax + xMin) / 2 else 0
            xB = 1 if xB > (xMax + xMin) / 2 else 0
            xC = 1 if xC > (xMax + xMin) / 2 else 0

            yA = 1 if yA > (yMax + yMin) / 2 else 0
            yB = 1 if yB > (yMax + yMin) / 2 else 0
            yC = 1 if yC > (yMax + yMin) / 2 else 0

            lA = xA + 2 * yA
            lB = xB + 2 * yB
            lC = xC + 2 * yC

            locateList = ["0"] * 4
            locateList[lA] = "A"
            locateList[lB] = "B"
            locateList[lC] = "C"

            locateResult=""
            for i in range(4):
                locateResult += ""+i+":"+locateList[i]

            print(locateResult)

            # 绘制结果
            w, h = template_A.shape[::-1]
            for loc in locations_A:
                cv2.rectangle(image, loc, (loc[0] + w, loc[1] + h), (0, 0, 255), 2)
                cv2.putText(image, 'A', (loc[0], loc[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            w, h = template_B.shape[::-1]
            for loc in locations_B:
                cv2.rectangle(image, loc, (loc[0] + w, loc[1] + h), (0, 255, 0), 2)
                cv2.putText(image, 'B', (loc[0], loc[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            w, h = template_C.shape[::-1]
            for loc in locations_C:
                cv2.rectangle(image, loc, (loc[0] + w, loc[1] + h), (255, 0, 0), 2)
                cv2.putText(image, 'C', (loc[0], loc[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # 显示结果
            cv2.imshow('Detected Letters', image)
        except IndexError:
            print("get picture error")
            locateResult = "E"
        cv2.imshow('Detected Letters', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return locateResult

if __name__ =="__main__":
    obj = identifyPic()
    obj.getPic()
