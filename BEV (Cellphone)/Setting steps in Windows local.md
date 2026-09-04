第一次建立環境

cd "你存放的資料夾路徑"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip  (如果不能安裝，連線外網，一次就可以了)
python -m pip install opencv-python
python bev.py


若要離開虛擬環境

deactivate

之後再次使用這個專案

cd "你存放的資料夾路徑"
.\.venv\Scripts\Activate.ps1
python bev.py



執行Steps:
1. 在路徑下執行  python bev.py
2. 執行過程中再分別對跳出的圖片 點出定位點 
範例內容如下

   請依序點擊「左右兩張白紙」的 4 個內側角：
     1. 左面白紙的【右上角】(靠近棋盤格)
     2. 右面白紙的【左上角】(靠近棋盤格)
     3. 右面白紙的【左下角】(靠近橘盒)
     4. 左面白紙的【右下角】(靠近橘盒)

3. 點出定位點後，會產生完整的合成圖 seamless_bev_output.jpg
4. Done

