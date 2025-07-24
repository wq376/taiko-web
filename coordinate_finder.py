# coordinate_finder.py
import pyautogui
import time
print("="*50 + "\nマウス座標 発見ツール\n" + "="*50)
print("マウスを動かすと、現在のX, Y座標がリアルタイムで表示されます。")
print("ゲーム画面の『叩く場所』と『レーンの左上』の座標を調べてください。")
print("終了するには、このウィンドウを選択して Ctrl + C を押してください。")
try:
    while True:
        x, y = pyautogui.position()
        print(f'X: {x:<4} Y: {y:<4}', end='\r')
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\n座標発見ツールを終了しました。")