import cv2
import numpy as np

# --- 1. 設定畫布與目標點 ---
CANVAS_SIZE = (1000, 1000)
CENTER_BOX = {'x': 400, 'y': 400, 'w': 200, 'h': 200}

# 這裡我們將對齊點改為「左右白紙的內側邊緣」，強迫角落完美重合
dst_points_dict = {
    "Front": np.float32([[350, 250], [650, 250], [650, 350], [350, 350]]),
    "Back": np.float32([[650, 750], [350, 750], [350, 650], [650, 650]]),
    "Left": np.float32([[250, 650], [250, 350], [350, 350], [350, 650]]),
    "Right": np.float32([[750, 350], [750, 650], [650, 650], [650, 350]])
}

clicked_points = []

def click_event(event, x, y, flags, param):
    """滑鼠點擊事件處理"""
    global clicked_points
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append([x, y])
        img_copy = param.copy()
        for i, pt in enumerate(clicked_points):
            cv2.circle(img_copy, tuple(pt), 5, (0, 0, 255), -1)
            cv2.putText(img_copy, str(i+1), (pt[0]+10, pt[1]-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Click 4 corners", img_copy)

def get_points_from_image(image_name, img):
    """開啟視窗讓使用者點擊 4 個點 (自適應螢幕大小)"""
    global clicked_points
    clicked_points = []
    
    h, w = img.shape[:2]
    # 縮小圖片以適應螢幕
    target_height = 700
    scale = h / target_height
    target_width = int(w / scale)
    display_img = cv2.resize(img, (target_width, target_height))
    
    print(f"\n[{image_name} 視窗] 請依序點擊「左右兩張白紙」的 4 個內側角：")
    print("1. 左面白紙的【右上角】(靠近棋盤格)")
    print("2. 右面白紙的【左上角】(靠近棋盤格)")
    print("3. 右面白紙的【左下角】(靠近橘盒)")
    print("4. 左面白紙的【右下角】(靠近橘盒)")
    
    cv2.namedWindow("Click 4 corners", cv2.WINDOW_AUTOSIZE)
    cv2.imshow("Click 4 corners", display_img)
    cv2.setMouseCallback("Click 4 corners", click_event, display_img)
    
    while len(clicked_points) < 4:
        cv2.waitKey(10)
        
    cv2.destroyWindow("Click 4 corners")
    
    # 將座標放大回原圖比例
    src_pts = np.float32([[p[0] * scale, p[1] * scale] for p in clicked_points])
    return src_pts

def get_camera_mask(camera_name):
    """產生梯形遮罩，讓四個鏡頭在對角線完美切割，消除重疊殘影"""
    mask = np.zeros((CANVAS_SIZE[1], CANVAS_SIZE[0]), dtype=np.uint8)
    if camera_name == "Front":
        pts = np.array([[0,0], [1000,0], [600,400], [400,400]])
    elif camera_name == "Right":
        pts = np.array([[1000,0], [1000,1000], [600,600], [600,400]])
    elif camera_name == "Back":
        pts = np.array([[1000,1000], [0,1000], [400,600], [600,600]])
    elif camera_name == "Left":
        pts = np.array([[0,1000], [0,0], [400,400], [400,600]])
    cv2.fillPoly(mask, [pts], 255)
    return mask

# --- 2. 讀取影像 ---
images = {
    "Front": cv2.imread("Front.jpg"),
    "Back": cv2.imread("Back.jpg"),
    "Left": cv2.imread("Left.jpg"),
    "Right": cv2.imread("Right.jpg")
}

# --- 3. 處理與拼接 ---
final_bev = np.zeros((CANVAS_SIZE[1], CANVAS_SIZE[0], 3), dtype=np.uint8)

for name in ["Front", "Right", "Back", "Left"]:
    img = images[name]
    
    # 取得點擊座標
    src_pts = get_points_from_image(name, img)
    dst_pts = dst_points_dict[name]
    
    # 透視變換
    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(img, matrix, CANVAS_SIZE)
    
    # 套用梯形遮罩 (只保留該鏡頭負責的視角區域)
    mask = get_camera_mask(name)
    warped_masked = cv2.bitwise_and(warped, warped, mask=mask)
    
    # 直接疊加 (因為有遮罩裁切，邊界會呈現完美的對角線接合)
    final_bev = cv2.add(final_bev, warped_masked)

# --- 4. 畫出中央橘色盒子 ---
cv2.rectangle(final_bev, 
              (CENTER_BOX['x'], CENTER_BOX['y']), 
              (CENTER_BOX['x'] + CENTER_BOX['w'], CENTER_BOX['y'] + CENTER_BOX['h']), 
              (0, 102, 255), -1)

cv2.namedWindow("Final Seamless BEV", cv2.WINDOW_NORMAL)
cv2.imshow("Final Seamless BEV", final_bev)
cv2.imwrite("seamless_bev_output.jpg", final_bev)
print("\n合成成功！已儲存為 seamless_bev_output.jpg")
cv2.waitKey(0)
cv2.destroyAllWindows()
