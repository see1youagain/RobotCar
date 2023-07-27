import time
from threading import Thread,Lock

class roadPlan():
    def __init__(self) -> None:
        # 初始值均为 1
        self.A = 1
        self.B = 1
        self.C = 1
        self.flag = 0  # 取药成功为1，否则为0
        self.lock=Lock()#互斥锁
        # 记录上次更新时间的时间戳
        self.last_update_A = time.time()
        self.last_update_B = time.time()
        self.last_update_C = time.time()
        #记录取药的顺序
        self.window = []
        #记录送药到哪个区域的顺序
        self.num = []
        self.peisong_dict = {}
        # 放这合不合适
        self.new_dict = {}
        self.running = True
        self.t = 0


    '''==============================线程函数部分======================================='''
    def update_values(self):
        # A=self.A
        # B=self.B
        # C=self.C
        last_update_A=self.last_update_A 
        last_update_B=self.last_update_B
        last_update_C=self.last_update_C
        self.running = True
        while self.running:
            # 获取当前时间戳
            current_time = time.time()

            # 如果距离上次更新 A 的时间已经超过 2 分钟，则将 A 的值加 1
            if current_time - last_update_A >= 2 * 60:
                self.A += 1
                last_update_A = current_time

            # 如果距离上次更新 B 的时间已经超过 1 分钟，则将 B 的值加 1
            if current_time - last_update_B >= 1 * 60:
                self.B += 1
                last_update_B = current_time

            # 如果距离上次更新 C 的时间已经超过 40 秒，则将 C 的值加 1
            if current_time - last_update_C >= 40:
                self.C += 1
                last_update_C = current_time
            time.sleep(4)
            # 输出当前 A、B、C 的值以及时间戳
            print(f"A: {self.A}, B: {self.B}, C: {self.C}, Time: {current_time}")
        # while not self.running:
        #     time.sleep(1)


    '''============================================初始化开始计数线程============================================'''
    def init(self):
        self.t = Thread(target=self.update_values)
        self.t.start()
        # t.join([900])


    def toggle_thread(self):
        self.running = not self.running
        if not self.running:
            self.t.join()
        # self.t.join()


    def parse_string(self , input_str):
        A=self.A
        B=self.B
        C=self.C
        # 将字符串以 | 分割成列表
        str_list = input_str.split('|')

        # 将列表中的每个元素以 : 分割成键值对，存入字典中
        result_dict = {}

        for item in str_list:
            key, value = item.split(':')
            result_dict[key] = value
        quyao_to_num = {'A': 1, 'C': 0, 'B': 2, '1': 6, '2': 5, '3': 4, '4': 3}
        keys1 = [key for key, value in result_dict.items() if value == 'A']  # 得到A要送的几个地方# 使用列表推导式筛选出值为 A 的键
        # print(keys1)
        keys2 = [key for key, value in result_dict.items() if value == 'C']
        keys3 = [key for key, value in result_dict.items() if value == 'B']
        # 找出目前堆积大于3的药品
        if C > 3 or B > 3 or A > 3:
            if A > 3 and len(keys1) != 0:
                print('有{}个A要送'.format(len(keys1)))
                # print('这是第 %d 次循环' % (i + 1))
                if '2' in keys1:
                    self.window.append(quyao_to_num['A'])
                    self.num.append(quyao_to_num['2'])
                    keys1.remove('2')
                elif '1' in keys1:
                    self.window.append(quyao_to_num['A'])
                    self.num.append(quyao_to_num['1'])
                    keys1.remove('1')
                elif '4' in keys1:
                    self.window.append(quyao_to_num['A'])
                    self.num.append(quyao_to_num['4'])
                    keys1.remove('4')
                elif '3' in keys1:
                    self.window.append(quyao_to_num['A'])
                    self.num.append(quyao_to_num['3'])
                    keys1.remove('3')
            # 判断 C 是否大于 3
            if C > 3 and len(keys2) != 0:
                for i in range(len(keys2)):
                    # print('这是第 %d 次循环' % (i + 1))
                    if '2' in keys2:
                        self.window.append(quyao_to_num['C'])
                        self.num.append(quyao_to_num['2'])
                        keys2.remove('2')
                    elif '1' in keys2:
                        self.window.append(quyao_to_num['C'])
                        self.num.append(quyao_to_num['1'])
                        keys2.remove('1')
                    elif '4' in keys2:
                        self.window.append(quyao_to_num['C'])
                        self.num.append(quyao_to_num['4'])
                        keys2.remove('4')
                    elif '3' in keys2:
                        self.window.append(quyao_to_num['C'])
                        self.num.append(quyao_to_num['3'])
                        keys2.remove('3')
            # 判断 B 是否大于 3
            if B > 3 and len(keys3) != 0:
                # print('这是第 %d 次循环' % (n + 1))
                if '2' in keys3:
                    self.window.append(quyao_to_num['B'])
                    self.num.append(quyao_to_num['2'])
                    keys3.remove('2')
                elif '1' in keys3:
                    self.window.append(quyao_to_num['B'])
                    self.num.append(quyao_to_num['1'])
                    keys3.remove('1')
                elif '4' in keys3:
                    self.window.append(quyao_to_num['B'])
                    self.num.append(quyao_to_num['4'])
                    keys3.remove('4')
                elif '3' in keys3:
                    self.window.append(quyao_to_num['B'])
                    self.num.append(quyao_to_num['3'])
                    keys3.remove('3')

        if len(keys1) != 0:
            print('有{}个A要送'.format(len(keys1)))
            for i in range(len(keys1)):
                # print('这是第 %d 次循环' % (i + 1))
                if '2' in keys1:
                    self.window.append(quyao_to_num['A'])
                    self.num.append(quyao_to_num['2'])
                    keys1.remove('2')
                elif '1' in keys1:
                    self.window.append(quyao_to_num['A'])
                    self.num.append(quyao_to_num['1'])
                    keys1.remove('1')
                elif '4' in keys1:
                    self.window.append(quyao_to_num['A'])
                    self.num.append(quyao_to_num['4'])
                    keys1.remove('4')
                elif '3' in keys1:
                    self.window.append(quyao_to_num['A'])
                    self.num.append(quyao_to_num['3'])
                    keys1.remove('3')
        if len(keys2) != 0:
            if keys2:
                print('有{}个C要送'.format(len(keys2)))
            for i in range(len(keys2)):
                # print('这是第 %d 次循环' % (i + 1))
                if '2' in keys2:
                    self.window.append(quyao_to_num['C'])
                    self.num.append(quyao_to_num['2'])
                    keys2.remove('2')
                elif '1' in keys2:
                    self.window.append(quyao_to_num['C'])
                    self.num.append(quyao_to_num['1'])
                    keys2.remove('1')

                elif '4' in keys2:
                    self.window.append(quyao_to_num['C'])
                    self.num.append(quyao_to_num['4'])
                    keys2.remove('4')
                elif '3' in keys2:
                    self.window.append(quyao_to_num['C'])
                    self.num.append(quyao_to_num['3'])
                    keys2.remove('3')
        if len(keys3) != 0:
            # while B != 0:
            if keys3:
                print('有{}个B要送'.format(len(keys3)))
            for n in range(len(keys3)):
                # print('这是第 %d 次循环' % (n + 1))
                if '2' in keys3:
                    self.window.append(quyao_to_num['B'])
                    self.num.append(quyao_to_num['2'])
                    keys3.remove('2')
                elif '1' in keys3:
                    self.window.append(quyao_to_num['B'])
                    self.num.append(quyao_to_num['1'])
                    keys3.remove('1')
                elif '4' in keys3:
                    self.window.append(quyao_to_num['B'])
                    self.num.append(quyao_to_num['4'])
                    keys3.remove('4')
                elif '3' in keys3:
                    self.window.append(quyao_to_num['B'])
                    self.num.append(quyao_to_num['3'])
                    keys3.remove('3')

        print(self.window)
        print(self.num)
        #print(dict(list(zip(self.window, self.num))))
    def arrivedTask(self):
        self.flag=1


#用于实时更新取药之后，药物余量
    def judge(self):
        # new_dict = dict(list(zip(self.window, self.num)))
        # print(new_dict)
        # 判断是否前往取药区，若是，则相应药品减1，并将其从送货的列表中移除
        if self.flag == 1:
            
            # yao = next(key for key, value in new_dict.items() if value == self.num[0])
            yao = self.window[0]
            if yao == 1:
                self.lock.acquire()
                self.A -= 1
                self.lock.release()
            elif yao == 2:
                self.lock.acquire()
                self.B -= 1
                self.lock.release()
            elif yao ==0:
                self.lock.acquire()
                self.C -= 1
                self.lock.release()

            del self.window[0]
            del self.num[0]

            print('window剩余要送药品',self.window)
            print('num剩余配药区',self.num)
            self.flag = 0

        rWindow="False"
        rNum="False"
        if(len(self.window)!=0):
            rWindow=self.window[0]
        if(len(self.num)!=0):
            rNum=self.num[0]

        return rWindow,rNum

#示例
R=roadPlan()
R.init()#一调用就已经开始计数了
R.parse_string('1:A|2:0|3:B|4:C')
roadWindow,roadNum=R.judge()
print(f"roadWindow:{roadWindow}   roadNum:{roadNum}")


R.arrivedTask()#取药成功，前往配药区
print("任务送达")
roadWindow,roadNum=R.judge()
print(f"roadWindow:{roadWindow}   roadNum:{roadNum}")


R.arrivedTask()
print("任务送达")
roadWindow,roadNum=R.judge()
print(f"roadWindow:{roadWindow}   roadNum:{roadNum}")

R.arrivedTask()
print("任务送达")
roadWindow,roadNum=R.judge()
print(f"roadWindow:{roadWindow}   roadNum:{roadNum}")


R.toggle_thread()#线程停止函数,并释放线程



