import requests
from pprint import pprint
from geopy.geocoders import Nominatim 
import sys
import io, os
import json
import folium
from PyQt5 import QtGui, QtWidgets, QtCore, QtWebEngineWidgets
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QFont
import time, threading

app_id = 'Your_ID'
app_key = 'Your_KEY'
auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"

class controller_MainWindow(QtWidgets.QWidget):
    ### 用於整個控制邏輯的init函式
    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        self.setWindowTitle('旅遊轉乘規劃幫手')
        self.resize(1300, 990)

        # 設置標題欄顏色和字體顏色
        self.setStyleSheet("""
            QWidget {
                background-color: rgb(229, 248, 198);
            }
        """)
        
        self.goto_home() 
        self.show_map([[22.638901, 120.302505]])   
        self.arr = ['']*5
        
    def check(self, cb, i):
        dic = {3:'高鐵',4:'台鐵', 5:'公車', 6:'捷運', 7:'輕軌'}
        if cb.isChecked():
            for key, value in dic.items():
                 if value == cb.text():
                    self.arr[i] = key
        else:
            self.arr[i] = ''        
       
    ### UI主頁
    def goto_home(self):
        print("UI : goto_home")
        self.origin = None
        self.destination = None

        self.title = QtWidgets.QLabel(self)
        self.title.setText('旅遊轉乘幫手')
        self.title.setGeometry(0, 0, 1300, 58)
        self.title.setAlignment(QtCore.Qt.AlignCenter) 
        self.title.setStyleSheet("""
        background-color: rgb(149, 188, 118);
        color: white;
        font-weight: bold;
        font-size: 20px; 
        """)
    
        ### 輸入框
        self.l1 = QtWidgets.QLabel(self)
        self.l1.setText('START')
        self.l1.setGeometry(50, 60, 100, 30)
        self.l1.setStyleSheet("color: black; font-weight: bold;")
        self.input_1 = QtWidgets.QLineEdit(self)   # 第一個出發點
        self.input_1.setGeometry(50,90,250,50)
        self.input_1.setStyleSheet("border: 2px solid black;border-radius: 10px;padding: 0 8px;background: white;selection-background-color: lightblue;font-weight: bold;")

        self.l2 = QtWidgets.QLabel(self)
        self.l2.setText('DESTINATION')
        self.l2.setGeometry(360, 60, 150, 30)
        self.l2.setStyleSheet("color: black; font-weight: bold;")
        self.input_2 = QtWidgets.QLineEdit(self)   # 第二個抵達景點
        self.input_2.setGeometry(360,90,250,50)
        self.input_2.setStyleSheet("border: 2px solid black;border-radius: 10px;padding: 0 8px;background: white;selection-background-color: lightblue;font-weight: bold;")

        ### 出發日期時間
        self.label = QtWidgets.QLabel(self)
        self.label.setText('預計出發時間')
        self.label.setGeometry(50, 160, 100, 30)
        self.label.setStyleSheet("color: black; font-weight: bold;")
    
        self.dp= QtWidgets.QDateEdit(self)
        self.dp.setGeometry(160,160,100,30)
        self.dp.setDisplayFormat('yyyy/MM/dd')
        self.dp.setDate(QtCore.QDate().currentDate())
        self.dp.setStyleSheet("background-color: white; font-weight: bold")

        self.time_depart = QtWidgets.QTimeEdit(self)
        self.time_depart.setGeometry(260,160,100,30)
        self.time_depart.setTime(QtCore.QTime.currentTime())
        self.time_depart.setStyleSheet("background-color: white; font-weight: bold")
       

        ### 抵達日期時間
        self.label2 = QtWidgets.QLabel(self)
        self.label2.setText('預計抵達時間')
        self.label2.setGeometry(50, 220, 100, 30)
        self.label2.setStyleSheet("color: black; font-weight: bold;")
     
        self.ar = QtWidgets.QDateEdit(self)
        self.ar.setGeometry(160,220,100,30)
        self.ar.setDisplayFormat('yyyy/MM/dd')
        self.ar.setDate(QtCore.QDate().currentDate())
        self.ar.setStyleSheet("background-color: white; font-weight: bold")


        self.time_arrival = QtWidgets.QTimeEdit(self)
        self.time_arrival.setGeometry(260,220,100,30)
        self.time_arrival.setTime(QtCore.QTime.currentTime())
        self.time_arrival.setStyleSheet("background-color: white; font-weight: bold")

        ### 偏好選擇
        self.label3 = QtWidgets.QLabel(self)
        self.label3.setText('價格/時間期望')
        self.label3.setGeometry(50, 320, 100, 30)
        self.label3.setStyleSheet("color: black; font-weight: bold;")
        self.slider = QtWidgets.QSlider(self)
        self.slider.setGeometry(170,325,220,22) 
        self.slider.setRange(0, 1)
        self.slider.setOrientation(1)
        

        self.label4 = QtWidgets.QLabel(self)
        self.label4.setText('最便宜')
        self.label4.setGeometry(170, 280, 70, 30)
        self.label4.setStyleSheet("""
        background-color: green;
        color: white;
        font-weight: bold;
        border: 2px solid green;
        border-radius: 10px; 
        padding: 5px; 
        """)

        self.label5 = QtWidgets.QLabel(self)
        self.label5.setText('時間最短')
        self.label5.setGeometry(310, 280, 85, 30)
        self.label5.setStyleSheet("""
        background-color: green;
        color: white;
        font-weight: bold;
        border: 2px solid green;
        border-radius: 10px; 
        padding: 5px; 
        """)

        ### 偏好大眾運輸(3:高鐵,4:台鐵, 5: 公車, 6: 捷運, 7: 輕軌)
        self.rb_3 = QtWidgets.QCheckBox(self)  
        self.rb_3.setGeometry(450,160,100,30)
        self.rb_3.setText('高鐵')
        self.rb_3.clicked.connect(lambda:self.check(self.rb_3, 0))
        self.rb_3.setStyleSheet("""
            QCheckBox {font-weight: bold;}
            QCheckBox::indicator {width: 20px;height: 20px;}
            QCheckBox::indicator:unchecked {border: 2px solid gray;border-radius: 5px;background-color: white;}
            QCheckBox::indicator:checked {border: 2px solid gray;border-radius: 5px;background-color: rgb(179, 218, 148);}""")

        self.rb_4 = QtWidgets.QCheckBox(self)  
        self.rb_4.setGeometry(450,190,100,30)
        self.rb_4.setText('台鐵')
        self.rb_4.clicked.connect(lambda:self.check(self.rb_4, 1))
        self.rb_4.setStyleSheet("""
            QCheckBox {font-weight: bold;}
            QCheckBox::indicator {width: 20px;height: 20px;}
            QCheckBox::indicator:unchecked {border: 2px solid gray;border-radius: 5px;background-color: white;}
            QCheckBox::indicator:checked {border: 2px solid gray;border-radius: 5px;background-color: rgb(179, 218, 148);}""")

        self.rb_5 = QtWidgets.QCheckBox(self)  
        self.rb_5.setGeometry(450,220,100,30)
        self.rb_5.setText('公車')
        self.rb_5.clicked.connect(lambda:self.check(self.rb_5, 2))
        self.rb_5.setStyleSheet("""
            QCheckBox {font-weight: bold;}
            QCheckBox::indicator {width: 20px;height: 20px;}
            QCheckBox::indicator:unchecked {border: 2px solid gray;border-radius: 5px;background-color: white;}
            QCheckBox::indicator:checked {border: 2px solid gray;border-radius: 5px;background-color: rgb(179, 218, 148);}""")

        self.rb_6 = QtWidgets.QCheckBox(self)  
        self.rb_6.setGeometry(450,250,100,30)
        self.rb_6.setText('捷運')
        self.rb_6.clicked.connect(lambda:self.check(self.rb_6, 3))
        self.rb_6.setStyleSheet("""
            QCheckBox {font-weight: bold;}
            QCheckBox::indicator {width: 20px;height: 20px;}
            QCheckBox::indicator:unchecked {border: 2px solid gray;border-radius: 5px;background-color: white;}
            QCheckBox::indicator:checked {border: 2px solid gray;border-radius: 5px;background-color: rgb(179, 218, 148);}""")

        self.rb_7 = QtWidgets.QCheckBox(self)  
        self.rb_7.setGeometry(450,280,100,30)
        self.rb_7.setText('輕軌')
        self.rb_7.clicked.connect(lambda:self.check(self.rb_7, 4))
        self.rb_7.setStyleSheet("""
            QCheckBox {font-weight: bold;}
            QCheckBox::indicator {width: 20px;height: 20px;}
            QCheckBox::indicator:unchecked {border: 2px solid gray;border-radius: 5px;background-color: white;}
            QCheckBox::indicator:checked {border: 2px solid gray;border-radius: 5px;background-color: rgb(179, 218, 148);}""")

        ### 搜尋按鈕
        self.btn = QtWidgets.QPushButton(self)
        self.btn.setGeometry(50,375,120,40)
        self.btn.setText('Go')
        font = QFont('Arial', 14, QFont.Bold)
        self.btn.setFont(font)
        self.btn.setStyleSheet("QPushButton { background-color: white; color: black;  border: 2px solid black; border-radius: 10px; } QPushButton:hover {background-color: rgb(149, 188, 118);}")
        self.btn.clicked.connect(self.search) 
       

        ### 路徑選項
        self.c1 = QtWidgets.QPushButton(self)
        self.c1.setGeometry(750,70,500,120)
        self.c1.setText('Route 1')
        self.c1.setStyleSheet("QPushButton { text-align: center;font-size: 14px;font-weight: bold; background-color: rgb(199, 238, 178); color: black;  border-radius: 10px; }QPushButton:pressed {background-color: rgb(149, 188, 118);padding-left: 12px; padding-top: 12px;}")

        self.c2 = QtWidgets.QPushButton(self)
        self.c2.setGeometry(750,195,500,120)
        self.c2.setText('Route 2')
        self.c2.setStyleSheet("QPushButton { text-align: center;font-size: 14px;font-weight: bold; background-color: rgb(199, 238, 178); color: black;  border-radius: 10px; }QPushButton:pressed {background-color: rgb(149, 188, 118);padding-left: 12px; padding-top: 12px;}")

        self.c3 = QtWidgets.QPushButton(self)
        self.c3.setGeometry(750,320,500,120)
        self.c3.setText('Route 3')
        self.c3.setStyleSheet("QPushButton { text-align: center;font-size: 14px;font-weight: bold; background-color: rgb(199, 238, 178); color: black;  border-radius: 10px; }QPushButton:pressed {background-color: rgb(149, 188, 118);padding-left: 12px; padding-top: 12px;}")

    def show_map(self, coordinate):
        ### Map
        self.m = folium.Map(
        	zoom_start=15,
        	location=coordinate[0]
        )
    
        #畫路徑
        if len(coordinate)!=0:
            self.m.add_child(folium.PolyLine(locations=coordinate,weight=5))
            #公車上下車站牌
            for i in range(len(bs)):
                folium.Marker(location=bs[i],
                              icon=folium.Icon(icon='bus',color='green',prefix='fa')).add_to(self.m)
            #輕軌
            for i in range(len(lt)):
                folium.Marker(location=lt[i],
                              icon=folium.Icon(icon='subway',color='green',prefix='fa')).add_to(self.m)
            #捷運
            for i in range(len(mt)):
                folium.Marker(location=mt[i],
                              icon=folium.Icon(icon='subway',color='green',prefix='fa')).add_to(self.m)
            #火車
            for i in range(len(ta)):
                folium.Marker(location=ta[i],
                              icon=folium.Icon(icon='train',color='green',prefix='fa')).add_to(self.m)
            #高鐵
            for i in range(len(hr)):
                folium.Marker(location=hr[i],
                              icon=folium.Icon(icon='train',color='green',prefix='fa')).add_to(self.m)
        
        #標記附近餐廳
        if len(related)!=0:
            key_list = list(restaurants.keys())
            val_list = list(restaurants.values())
            for i in range(len(key_list)):
                folium.Marker(location=val_list[i][0],
                              popup=folium.Popup('<a href="{}" target="_blank"><h4><b>{}</h4></b></a><li>地址: {}</li><li>電話: {}</li><li>營業時間: {}</li><li>簡介: {}</li>'.format(val_list[i][2],key_list[i],val_list[i][1],val_list[i][3],val_list[i][4],val_list[i][5]),max_width=300),
                              icon=folium.Icon(icon='star',color='orange')).add_to(self.m)

        #標記附近景點
        if len(related)!=0:
            #print('附近景點: ',related)
            key_list = list(related.keys())
            val_list = list(related.values())
            for i in range(len(key_list)):
                img = '<img src="{}" width="300" height="200">'.format(val_list[i][4])
                html = "<div>{}<br><br><ul><h4><b>{}</h4></b><li>地址: {}</li><li>開放時間: {}</li><li>簡介: {}</li></ul></div>".format(img,key_list[i],val_list[i][1],val_list[i][2],val_list[i][3])
                folium.Marker(location=val_list[i][0],
                              popup=folium.Popup(html,max_width=300),
                              icon=folium.Icon(color='red')).add_to(self.m)

            #標記出發點
            folium.Marker(location=coordinate[0],
                          icon=folium.Icon(icon='male', 
                                           color='green',
                                           prefix='fa')).add_to(self.m)
   
            #標記抵達景點
            img = '<img src="{}" width="300" height="200">'.format(self.info[0][4])
            html = "<div>{}<br><br><ul><h4><b>{}</h4></b><li>地址: {}</li><li>營業時間: {}</li><li>簡介: {}</li></ul></div>".format(img,self.info[0][0],self.info[0][1],self.info[0][2],self.info[0][3])
            folium.Marker(location=[round(float(x),5) for x in self.info[1].split(',')],
                          popup=folium.Popup(html,max_width=300),
                          icon=folium.Icon(icon='flag', 
                                           color='green')).add_to(self.m)
  
        self.m.save('map.html')

        # 建立網頁顯示元件
        view = QtWebEngineWidgets.QWebEngineView(self)  
        view.setGeometry(20,445,1260,545) 
        view.load(QtCore.QUrl.fromLocalFile(os.path.abspath('map.html')))
        view.show()
        view.reload()

    def search(self):
        related.clear()
        restaurants.clear()
        bs.clear()
        mt.clear()
        lt.clear()
        self.c1.setText('')
        self.c2.setText('')
        self.c3.setText('')
        self.transit = ','.join([str(i) for i in self.arr if i])
        self.depart = self.dp.date().toString("yyyy-MM-dd")+"T"+self.time_depart.time().toString()
        self.arrival = self.ar.date().toString("yyyy-MM-dd")+"T"+self.time_arrival.time().toString()
        self.gc = str(self.slider.value())
        data_response = response(self.input_1.text(),self.input_2.text(),self.gc,self.transit,self.depart,self.arrival)
        data_response.get_IP()
        self.info = data_response.get_attraction()
        self.text = data_response.get_route()

        if self.text[0] == '':
            QtWidgets.QMessageBox.warning(None, 'Critical MessageBox', '無最佳路徑，請重新輸入地點!')
        else: 
            self.c1.setText(self.text[0][0])
            self.c1.clicked.connect(lambda:self.c1.setText(self.text[0][2]))
            self.c1.clicked.connect(self.checked) 
            self.c1.clicked.connect(lambda:self.show_map(self.text[0][1]))
           
            if self.text[1] != '':
                self.c2.setText(self.text[1][0])
                self.c2.clicked.connect(lambda:self.c2.setText(self.text[1][2])) 
                self.c2.clicked.connect(self.checked2) 
                self.c2.clicked.connect(lambda:self.show_map(self.text[1][1]))
                
            if self.text[2] != '':
                self.c3.setText(self.text[2][0])
                self.c3.clicked.connect(lambda:self.c3.setText(self.text[2][2]))
                self.c3.clicked.connect(self.checked3) 
                self.c3.clicked.connect(lambda:self.show_map(self.text[2][1]))
                
        data_response.get_nearby()
            
        print("Done")

    def checked(self):
                if len(self.text[0][1]) > 6:
                    self.c1.setStyleSheet("QPushButton{text-align: center;font-size: 11px;font-weight: bold; background-color: rgb(199, 238, 178); color: black;border-radius: 10px;} QPushButton:pressed {background-color: rgb(149, 188, 118);padding-left: 12px; padding-top: 12px;}")
                if self.text[0][3]:
                    bs.clear()
                    bus(self.text[0][3][0][0],self.text[0][3][0][1],self.text[0][3][0][2],self.text[0][3][0][3])
                if self.text[0][5]:
                    lt.clear()
                    lrt(self.text[0][5][0][0],self.text[0][5][0][1],self.text[0][5][0][2],self.text[0][5][0][3])
                if self.text[0][6]:
                    hr.clear()
                    hsr(self.text[0][6][0][0],self.text[0][6][0][1],self.text[0][6][0][2],self.text[0][6][0][3])
                if self.text[0][4]:
                    mt.clear()
                    mrt(self.text[0][4][0][0],self.text[0][4][0][1],self.text[0][4][0][2],self.text[0][4][0][3])
                if self.text[0][7]:
                    ta.clear()
                    tra(self.text[0][7][0][0],self.text[0][7][0][1],self.text[0][7][0][2],self.text[0][7][0][3])
              
    def checked2(self):
                if len(self.text[1][1]) > 6:
                    self.c2.setStyleSheet("QPushButton{text-align: center;font-size: 11px;font-weight: bold; background-color: rgb(199, 238, 178); color: black;border-radius: 10px;} QPushButton:pressed {background-color: rgb(149, 188, 118);padding-left: 12px; padding-top: 12px;}")
                if self.text[1][3]:
                    bs.clear()
                    bus(self.text[1][3][0][0],self.text[1][3][0][1],self.text[1][3][0][2],self.text[1][3][0][3])
                if self.text[1][5]:
                    lt.clear()
                    lrt(self.text[1][5][0][0],self.text[1][5][0][1],self.text[1][5][0][2],self.text[1][5][0][3])
                if self.text[1][6]:
                    hr.clear()
                    hsr(self.text[1][6][0][0],self.text[1][6][0][1],self.text[1][6][0][2],self.text[1][6][0][3])
                if self.text[1][4]:
                    mt.clear()
                    mrt(self.text[1][4][0][0],self.text[1][4][0][1],self.text[1][4][0][2],self.text[1][4][0][3])
                if self.text[1][7]:
                    ta.clear()
                    tra(self.text[1][7][0][0],self.text[1][7][0][1],self.text[1][7][0][2],self.text[1][7][0][3])
    def checked3(self):
                if len(self.text[2][1]) > 6:
                    self.c3.setStyleSheet("QPushButton{text-align: center;font-size: 11px;font-weight: bold; background-color: rgb(199, 238, 178); color: black;border-radius: 10px;} QPushButton:pressed {background-color: rgb(149, 188, 118);padding-left: 12px; padding-top: 12px;}")
                if self.text[2][3]:
                    bs.clear()
                    bus(self.text[2][3][0][0],self.text[2][3][0][1],self.text[2][3][0][2],self.text[2][3][0][3])
                if self.text[2][5]:
                    lt.clear()
                    lrt(self.text[2][5][0][0],self.text[2][5][0][1],self.text[2][5][0][2],self.text[2][5][0][3])
                if self.text[2][6]:
                    hr.clear()
                    hsr(self.text[2][6][0][0],self.text[2][6][0][1],self.text[2][6][0][2],self.text[2][6][0][3])
                if self.text[2][4]:
                    mt.clear()
                    mrt(self.text[2][4][0][0],self.text[2][4][0][1],self.text[2][4][0][2],self.text[2][4][0][3])
                if self.text[2][7]:
                    ta.clear()
                    tra(self.text[2][7][0][0],self.text[2][7][0][1],self.text[2][7][0][2],self.text[2][7][0][3])

class Auth():

    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        content_type = 'application/x-www-form-urlencoded'
        grant_type = 'client_credentials'

        return{
            'content-type' : content_type,
            'grant_type' : grant_type,
            'client_id' : self.app_id,
            'client_secret' : self.app_key
        }

class data():

    def __init__(self, app_id, app_key, auth_response):
        self.app_id = app_id
        self.app_key = app_key
        self.auth_response = auth_response

    def get_data_header(self):
        auth_JSON = json.loads(self.auth_response.text)
        access_token = auth_JSON.get('access_token')

        return{
            'authorization': 'Bearer ' + access_token,
            'Accept-Encoding': 'gzip'
        }

class routes():

    def __init__(self, path, start, end, time, price):
        self.path = path
        self.start = start
        self.end = end
        self.price = price
        self.time = time

    def get_info(self):
        words = "Start time : {}\nArrive time : {}\nTravel time : {} min\nTotal price : NT${}".format(self.start,self.end,self.time,self.price)
        output = ''
        point = []
        buses = []
        mrts = []
        lrts = []
        hsrs = []
        tras = []
        for step in self.path:
                types = step['type']
                #print(types)
                if types == 'transit':
                    self.category = step['transport']['category']
                    self.trans = step['transport']['name']
                    self.duration = int(step['travelSummary']['duration']/60)
                    self.a = step['arrival']['place']['name']
                    self.a_t = step['arrival']['time']
                    self.a_l = step['arrival']['place']['location']
                    self.d = step['departure']['place']['name']
                    self.d_t = step['departure']['time']
                    self.d_l = step['departure']['place']['location']
                    word = "{} {} : {} -> {} {} 抵達".format(self.category,self.trans,self.d,self.a,self.d_t)

                    if self.category == 'Bus':
                        buses.append([self.trans, self.d,self.d_l,self.a_l,self.d_t,self.a_t])
                        word = "{} {} : {} -> {}\n {} ~ {}".format(self.category,self.trans,self.d,self.a,self.d_t,self.a_t)
                    elif  self.category == 'MRT':
                        mrts.append([self.trans, self.d,self.d_l,self.a_l,self.d_t,self.a_t])
                    elif  self.category == 'LRT':
                        lrts.append([self.trans, self.d,self.d_l,self.a_l,self.d_t,self.a_t])
                    elif  self.category == 'HSR':
                        hsrs.append([self.trans, self.d,self.d_l,self.a_l,self.d_t,self.a_t])
                    else:
                        tras.append([self.trans, self.d,self.d_l,self.a_l,self.d_t,self.a_t])
              
                elif types == 'pedestrian':
                    self.length = int(step['travelSummary']['length'])
                    self.a_l = step['arrival']['place']['location']
                    self.d_l = step['departure']['place']['location']
                    if step['travelSummary']['duration'] < 60:
                        self.duration = int(step['travelSummary']['duration'])
                        word = "步行{}秒 ({}m)".format(self.duration,self.length)
                    else:
                        self.duration = int(step['travelSummary']['duration']/60)
                        word = "步行{}分鐘 ({}m)".format(self.duration,self.length)

                elif types == 'pedestrian-station':
                    self.atime = step['arrival']['time']
                    self.dtime = step['departure']['time']
                    self.a_l = step['arrival']['place']['location']
                    self.d_l = step['departure']['place']['location']
                    word = '步行到車站 {}分鐘'.format(int(step['travelSummary']['duration']/60))

                else:
                    self.atime = step['arrival']['time']
                    self.dtime = step['departure']['time']
                    word = '等候 {} 分鐘...'.format(int(step['travelSummary']['duration']/60))
              
                point.append([self.d_l['lat'],self.d_l['lng']])
                point.append([self.a_l['lat'],self.a_l['lng']])
                
                output += word + '\n'

        if output.endswith('\n'):
            output = output.rstrip('\n')

        return words, point, output, buses, mrts, lrts, hsrs, tras


class response():

    def __init__(self, origin, destination, gc, transit, depart, arrival):
        self.origin = origin
        self.destination = destination
        self.gc = gc
        self.transit = transit
        self.depart = depart
        self.arrival = arrival

    def get_IP(self):
        #輸入地點
        geolocator = Nominatim(user_agent="MyApp")
        l1 = geolocator.geocode(self.origin)
        l2 = geolocator.geocode(self.destination)
        self.oIP = '{}, {}'.format(float(l1.latitude), float(l1.longitude))
        self.dIP = '{}, {}'.format(float(l2.latitude), float(l2.longitude))
        #print(self.oIP,self.dIP)
        #GPS
        #response = requests.get('https://ipinfo.io')
        #data = response.json()
        #loc = data['loc'].split(',')
        #self.now = '{}, {}'.format(float(loc[0]), float(loc[1]))
        #print(self.now)

    def get_attraction(self):
        d = data(app_id, app_key, auth_response)
        attraction_url = "https://tdx.transportdata.tw/api/basic/v2/Tourism/ScenicSpot/Kaohsiung?%24filter=startswith%28ScenicSpotName%2C%27{}%27%29&%24top=3&%24format=JSON".format(self.destination)
        data_response = requests.get(attraction_url, headers=d.get_data_header()).json()
        if len(data_response)!=0:
            self.scenicSpotName = data_response[0]['ScenicSpotName']
            self.address = data_response[0]['Address']
            self.description = data_response[0]['Description']
            self.openTime = data_response[0]['OpenTime']
            self.site = '{}, {}'.format(data_response[0]['Position']['PositionLat'], data_response[0]['Position']['PositionLon'])
            self.pic = data_response[0]['Picture']['PictureUrl1']
            info = [self.scenicSpotName,self.address,self.openTime,self.description,self.pic]
        else:
            info = [self.destination,'無','無','無','無']
            self.site = None

        return info, self.site

    def get_restaurant(self):
        rest_url = 'https://tdx.transportdata.tw/api/basic/v2/Tourism/Restaurant/Kaohsiung?%24filter=RestaurantName%20eq%20%%27{}%27%&%24top=30&%24format=JSON'.format(self.restaurants_at)
        rest_response = requests.get(rest_url, headers=d.get_data_header()).json()
        if len(rest_response)!=0:
            self.restaurantName = rest_response[0]['RestaurantName']
            self.ads = rest_response[0]['Address']
            self.des = rest_response[0]['Description']
            self.open = rest_response[0]['OpenTime']
            self.phone = rest_response[0]["Phone"]
            self.web = rest_response[0]["WebsiteUrl"]
            info2 = [self.restaurantName,self.ads,self.web,self.phone,self.open,self.des]
        else:
            info2 = [self.restaurants_at,'無','無','無','無']

        return info2
        
    def get_nearby(self):
        for place in [self.site,self.oIP]:
            nearby_url = 'https://tdx.transportdata.tw/api/tourism/service/odata/V2/Tourism/Nearby?X={}&Y={}&Distance=500'.format(place.split(',')[1],place.split(',')[0])
            nearby_response = requests.get(nearby_url, headers=d.get_data_header()).json()
            #pprint(nearby_response)
            #景點
            for i in range(len(nearby_response["RelatedAttractions"])):
                self.destination =  nearby_response["RelatedAttractions"][i]["AttractionName"]
                self.related_att = self.get_attraction()
                self.related_loc = [nearby_response["RelatedAttractions"][i]['PositionLat'], nearby_response["RelatedAttractions"][i]['PositionLon']]
                listofnearbyA(self.destination,self.related_loc,self.related_att)
            #餐廳
            for j in range(len(nearby_response["RelatedRestaurants"])):
                self.restaurants_at =  nearby_response["RelatedRestaurants"][j]["RestaurantName"]
                self.related_rest = self.get_restaurant()
                self.restaurants_loc = [nearby_response["RelatedRestaurants"][j]['PositionLat'], nearby_response["RelatedRestaurants"][j]['PositionLon']]
                listofnearbyR(self.restaurants_at,self.restaurants_loc,self.related_rest) 

      
    def get_route(self):
        route_url = "https://tdx.transportdata.tw/api/maas/routing?origin={}&destination={}&gc={}&top=3&transit={}&transfer_time=15%2C60&depart={}&arrival={}&first_mile_mode=0&first_mile_time=10&last_mile_mode=0&last_mile_time=10".format(self.oIP,self.site,self.gc,self.transit,self.depart,self.arrival)
        data_response2 = requests.get(route_url, headers=d.get_data_header()).json()
        #pprint(data_response2)
        
        #生成三條路徑
        self.route = ['']*3
        texts = ['']*3

        for i in range(len(data_response2['data']['routes'])):
            if  'total_price' not in data_response2['data']['routes'][i]:
                prices = 'null'
            else:
                prices = data_response2['data']['routes'][i]['total_price']
            
            self.route[i] = routes(data_response2['data']['routes'][i]['sections'],data_response2['data']['routes'][i]['start_time'],data_response2['data']['routes'][i]['end_time'],int(data_response2['data']['routes'][i]['travel_time']/60),prices)
            texts[i] = self.route[i].get_info()

        return texts

related = {}
restaurants = {}
bs = []
mt = []
lt = []
ta = []
hr = []

def listofnearbyA(name,corr,info):
    related[name] = [corr,info[0][1],info[0][2],info[0][3],info[0][4]]
            
def listofnearbyR(name,corr,info):
    restaurants[name] = [corr,info[1],info[2],info[3],info[4],info[5]]

def bus(name,stop,loc1,loc2):
        bs.append([loc1['lat'],loc1['lng']])
        bs.append([loc2['lat'],loc2['lng']])
        #bus_url = 'https://tdx.transportdata.tw/api/basic/v2/Bus/EstimatedTimeOfArrival/City/Kaohsiung/{}?%24top=30&%24format=JSON'.format(name)
        #estimate = requests.get(bus_url, headers=d.get_data_header()).json()
        #for i in range(len(estimate)):
            #if estimate[i]['StopName']['Zh_tw'] == stop:
                #pprint(estimate[i])

def mrt(name,stop,loc1,loc2):
        mt.append([loc1['lat'],loc1['lng']])
        mt.append([loc2['lat'],loc2['lng']])
    
def lrt(name,stop,loc1,loc2):
        lt.append([loc1['lat'],loc1['lng']])
        lt.append([loc2['lat'],loc2['lng']])
    
def hsr(name,stop,loc1,loc2):
        hr.append([loc1['lat'],loc1['lng']])
        hr.append([loc2['lat'],loc2['lng']])

def tra(name,stop,loc1,loc2):
        ta.append([loc1['lat'],loc1['lng']])
        ta.append([loc2['lat'],loc2['lng']])
    

if __name__ == '__main__':
        a = Auth(app_id, app_key)
        auth_response = requests.post(auth_url, a.get_auth_header())
        d = data(app_id, app_key, auth_response)
        app = QtWidgets.QApplication(sys.argv)
        window = controller_MainWindow() 
        window.show()
        sys.exit(app.exec_())
        
        

   