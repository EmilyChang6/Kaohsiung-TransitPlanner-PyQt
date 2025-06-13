# Kaohsiung-TransitPlanner-PyQt
## 旅遊轉乘規劃幫手
以高雄市觀光景點為標的，為使用者提供從起點到迄點所需的各項運輸服務資訊，使用者可以選擇欲搭乘的公共運輸工具，並規劃適合的轉乘計劃。
### Method & Library
程式介面:
* PyQt5
* Folium map

旅遊轉乘規劃模組:
* Geopy - 座標轉換
* TDX API
1. 公共運輸旅運規劃功能模組 - 推薦路徑  
   https://tdx.transportdata.tw/api-service/swagger/maas/4513f9d6-caae-4cf7-a50c-e7887bec804e#/Routing/getRoutes 
3. 觀光資訊/觀光資訊資料庫開放資料 - 景點資訊/鄰近500m內景點和餐廳資訊  
   https://tdx.transportdata.tw/api-service/swagger/basic/cd0226cf-6292-4c35-8a0d-b595f0b15352#/Tourism/TourismApi_ScenicSpot_2240_1
5. 公共運輸 - 公車/軌道  
   https://tdx.transportdata.tw/api-service/swagger/basic/2998e851-81d0-40f5-b26d-77e2f5ac4118#/CityBus/CityBusApi_EstimatedTimeOfArrival_2032_1
### DEMO  
https://www.youtube.com/watch?v=qT_pkAfkHXU
