import cv2
import numpy as np
import glob


print(cv2.__version__)

# 图像截取
# 计算三个点所形成的两个向量之间的余弦值
def angle_cos(p0, p1, p2):
    d1, d2 = (p0 - p1).astype('float'), (p2 - p1).astype('float')
    return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))


def get_number_img(img):
    # 数字框识别
    h, w, ch = img.shape  # 获取图像的大小
    squares = []
    points = []
    squares_point = []
    img = cv2.GaussianBlur(img, (3, 3), 0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bin = cv2.Canny(gray, 30, 100, apertureSize=3)
    contours, _hierarchy = cv2.findContours(
        bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.imshow('bin', bin)
    # print("轮廓数量：%d" % len(contours))
    index = 0
    img_map = []
    # 轮廓遍历
    for cnt in contours:
        cnt_len = cv2.arcLength(cnt, True)  # 计算轮廓周长
        cnt = cv2.approxPolyDP(cnt, 0.02 * cnt_len, True)  # 多边形逼近
        # 条件判断逼近边的数量是否为4，轮廓面积是否大于1000，检测轮廓是否为凸的
        if len(cnt) == 4 and cv2.contourArea(cnt) > 1400 and cv2.contourArea(cnt) < 20000 and cv2.isContourConvex(cnt):
            # 计算轮廓的中心位置
            M = cv2.moments(cnt)  # 计算轮廓的矩

            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])  # 轮廓重心
            # print(u'cnt', cnt)
            cnt = cnt.reshape(-1, 2)
            # print(u'cnt_reshape:', cnt)
            # 将轮廓数组cnt重构为两列的形式，其中-1表示该维度的长度应该由数组本身推断出来，而2表示该维度应该包含2个元素。
            # 计算四边形的四个角的角度
            max_cos = np.max(
                [angle_cos(cnt[i], cnt[(i + 1) % 4], cnt[(i + 2) % 4]) for i in range(4)])
            # 只检测矩形（cos90° = 0）
            if max_cos < 0.1:
                # 检测四边形（不限定角度范围）
                # if True:
                index = index + 1
                points.append((cx, cy))
                # cv2.circle(img, (int(10), int(10)), 3, (0, 0, 0), -1)

                # cv2.circle(img, (int(cx), int(cy)), 5, (0, 0, 0), -1)
                # cv2.putText(img, ("#%d(%d,%d)" % (index, cx, cy)), (cx, cy), font, 0.7, (255, 0, 255), 2)
                squares.append(cnt)
                # print(u'cnt', cnt)
                # cv2.circle(img, (int(cnt[0][0]), int(cnt[0][1])), 3, (0, 0, 0), -1)
                # cv2.circle(img, (int(cnt[1][0]), int(cnt[1][1])), 3, (0, 0, 0), -1)
                # cv2.circle(img, (int(cnt[2][0]), int(cnt[2][1])), 3, (0, 0, 0), -1)
                # cv2.circle(img, (int(cnt[3][0]), int(cnt[3][1])), 3, (0, 0, 0), -1)
                # cv2.drawContours(img, squares, -1, (0, 0, 255), 2)
                # # 透视矫正
                src = np.float32([[int(cnt[0][0]), int(cnt[0][1])], [int(cnt[3][0]), int(cnt[3][1])],
                                  [int(cnt[1][0]), int(cnt[1][1])],
                                  [int(cnt[2][0]), int(cnt[2][1])]])
                dst = np.float32([[0, 0], [420, 0], [0, 280], [420, 280]])
                M = cv2.getPerspectiveTransform(src, dst)
                img_map = cv2.warpPerspective(img, M, (420, 280))

    # print(img_map)
    return img, img_map


# 原图像, 旋转角度, 缩放因子
def Rotation_img(image, angle, scale):
    # 图像的宽度和高度
    height, width = image.shape[:2]
    # 计算旋转中心点
    center = (width // 2, height // 2)
    # 计算旋转矩阵
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)
    # 执行旋转操作
    rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
    return rotated_image




def img_process(image):
    # 模板图像色彩空间转换，BGR-->灰度
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 模板图像阈值处理， 灰度-->二值
    ret, image_ed = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)
    return image_ed


# =============计算匹配值函数=====================
def getMatchValue(template, image):


    # 读取模板图像
    templateImage = cv2.imread(template)
    templateImage = img_process(templateImage)
    image = img_process(image)

    shape = image.shape
    height, width = shape[:2]
    # 将模板图像调整为与待识别图像尺寸一致
    templateImage = cv2.resize(templateImage, (width, height))
    # 计算模板图像、待识别图像的模板匹配值
    result = cv2.matchTemplate(image, templateImage, cv2.TM_CCOEFF)
    # 将计算结果返回
    return result[0][0]


# 摄像头配置
cap = cv2.VideoCapture("http://192.168.8.55:8080/stream?topic=/camera/rgb/image_raw")

# 用于存储模板
templates = []
# 遍历指定目录下所有子目录及模板图像
for i in range(10):
    templates.extend(glob.glob('temps/' + str(i + 1) + '.jpg'))


# matchValue用于存储所有匹配值
matchValue = []

# main
while True:
    success, img_fir = cap.read()
    cv2.imshow("img_sec", img_fir)
    img_sec = Rotation_img(img_fir, -30, 1.2)
    img_thir, img_ed = get_number_img(img_sec)
    # cv2.imshow("img_thir", img_thir)

    # 截取到数字板
    if img_ed != []:

        # 从templates中逐个提取模板，并将其与待识别图像计算匹配值
        for template in templates:
            Value = getMatchValue(template, img_ed)
            matchValue.append(Value)

        # print(u'matchValue', matchValue)  # 测试语句

        # 获取最佳匹配值
        bestValue = max(matchValue)

        # 获取最佳匹配值对应模板编号
        i = matchValue.index(bestValue)
        # print(i)         # 测试语句：看看匹配的模板编号
        if i == 0:
            ValueOfNumber = '7541'
        if i == 1:
            ValueOfNumber = '432'
        if i == 2:
            ValueOfNumber = '7856'
        if i == 3:
            ValueOfNumber = '17659'
        if i == 4:
            ValueOfNumber = '805'
        if i == 5:
            ValueOfNumber = '423'
        if i == 6:
            ValueOfNumber = '719'
        if i == 7:
            ValueOfNumber = '8064'
        if i == 8:
            ValueOfNumber = '038'
        if i == 9:
            ValueOfNumber = '8609'
        print(u'The Number is', ValueOfNumber)
        # 清空历史值
        matchValue = []
        cv2.imshow("img_ed", img_ed)

    # 按'q'结束程序
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    pass
