#!/usr/bin/python
# -*- coding:utf8 -*-
import cv2
import numpy as np
import os

class IdentifyNum():
    def __init__(self):
        self.cap = cv2.VideoCapture("http://192.168.8.35:8080/stream?topic=/camera/rgb/image_raw")
        templates = []
        files=[]
        folder_paths=[]
        folder_paths.append('D:/RobotCar/result1/alphabet/Number/0')
        folder_paths.append('D:/RobotCar/result1/alphabet/Number/1')
        folder_paths.append('D:/RobotCar/result1/alphabet/Number/2')
        folder_paths.append('D:/RobotCar/result1/alphabet/Number/3')
        folder_paths.append('D:/RobotCar/result1/alphabet/Number/4')
        folder_paths.append('D:/RobotCar/result1/alphabet/Number/5')
        folder_paths.append('D:/RobotCar/result1/alphabet/Number/6')
        folder_paths.append('D:/RobotCar/result1/alphabet/Number/7')
        folder_paths.append('D:/RobotCar/result1/alphabet/Number/8')
        folder_paths.append('D:/RobotCar/result1/alphabet/Number/9')
        for folder_path in folder_paths:
            files.append(os.listdir(folder_path))

        for index,file in enumerate(files):
            template=[]
            jpg_files = [file for file in file if file.lower().endswith('.jpg')]
            for jpg_file in jpg_files:
                file_path = os.path.join(folder_paths[index], jpg_file)
                # 在这里处理图片，例如显示图片
                template.append(cv2.imread(file_path, cv2.IMREAD_GRAYSCALE))
            templates.append(template)
        self.templates = templates

    def template_matching(self, image_gray, template, threshold):
        res = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(res >= threshold)
        return list(zip(*locations[::-1]))

    def getPic(self):
        cap = self.cap
        templates = self.templates

        hx, image = cap.read()
        # hx = True
        image = cv2.imread("D:/RobotCar/result1/alphabet/Number/123.jpg")

        if hx is False:
            print('read video error')
            exit(0)

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 设置匹配阈值
        threshold = 0.8
        locations=[None]*10
        kind=0
        for itemps in range(len(templates[0])):
            # 模板匹配
            kindtmp=0
            locationstmp=[None]*10
            for inums in range(10):
                locationstmp[inums]=self.template_matching(image_gray, templates[inums][itemps], threshold)
                kindtmp += 1 if len(locationstmp)>0 else 0
            if(kindtmp>=kind):
                locations=locationstmp
        numCount=0
        for i in range(10):
            numCount += len(locations[i])
        if(kind>=1 and numCount>=2):
            # 正确识别
            x=[None]*10
            xt=[None]
            for i in range(10):
                x[i] = [row[0] for row in locations[i]]
                xt += x[i]

            xMax = max(xt)
            xMin = min(xt)

            rx=[None]*10
            persent=[None]

            for i in range(10):
                rx[i] = [round(2*(x-xMin)/(xMax-xMin)) for x in x[i]]

            locateList = ["0"] * 3
            for i in range(10):
                for index in rx[i]:
                    locateList[index] = str(i)

            locateResult = ""
            for i in range(3, -1, -1):
                locateResult += "{} ".format(locateList[i])
            locateResult = locateResult[0:-1]
            print(locateResult)
            # 绘制结果
            for num in range(10):
                w, h = templates[num][i].shape[::-1]
                for loc in locations[num]:
                    cv2.rectangle(image, loc, (loc[0] + w, loc[1] + h), (0, 0, 255), 2)
                    cv2.putText(image, 'A', (loc[0], loc[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # 显示结果
            cv2.imshow('Detected Letters', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            return locateResult
        aera1_crop = image
        cv2.imshow('Detected Letters', image)
        # cv2.imshow('aera1_crop', aera1_crop)
        cv2.imwrite("D:/RobotCar/result1/alphabet/aera12.jpg", aera1_crop)
        print("False to read Pic")

        return "False"





if __name__ == "__main__":
    obj = IdentifyNum()
    obj.getPic()
