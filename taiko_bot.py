import cv2
import numpy as np
import pyautogui
from mss import mss
import keyboard
import time
import statistics

print("このシステムは「むずかしい」のみで対応します")
print("一部のゲームは対応しません")
print("「可」を多めに「良」を少なめに人間が操作しているかのようにします")

TIMING_ADJUSTMENT_PIXELS = 15

COOLDOWN = 0.01

LARGE_NOTE_MULTIPLIER = 1

TARGET_X_ABSOLUTE = 618; ROI_LEFT = 586; ROI_TOP = 351
THRESHOLD_MULTIPLIER_RED = 1.5; THRESHOLD_MULTIPLIER_BLUE = 1
DEBUG_MODE = False
ROI_WIDTH, ROI_HEIGHT = 550, 100
DRUM_ROLL_THRESHOLD_MULTIPLIER = 1.3
HIT_ZONE_WIDTH = 40

LOWER_RED = np.array([0, 130, 130]); UPPER_RED = np.array([10, 255, 255])
LOWER_BLUE = np.array([85, 80, 80]); UPPER_BLUE = np.array([100, 255, 255])
LOWER_YELLOW = np.array([25, 130, 130]); UPPER_YELLOW = np.array([35, 255, 255])
LOWER_ORANGE = np.array([5, 150, 150]); UPPER_ORANGE = np.array([15, 255, 255])

TARGET_X_RELATIVE = TARGET_X_ABSOLUTE - ROI_LEFT

def get_pixel_count(sct, monitor):
    img_bgra = sct.grab(monitor)
    hsv = cv2.cvtColor(cv2.cvtColor(np.array(img_bgra), cv2.COLOR_BGRA2BGR), cv2.COLOR_BGR2HSV)
    return {
        "red": cv2.countNonZero(cv2.inRange(hsv, LOWER_RED, UPPER_RED)),
        "blue": cv2.countNonZero(cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)),
        "yellow": cv2.countNonZero(cv2.inRange(hsv, LOWER_YELLOW, UPPER_YELLOW)),
        "orange": cv2.countNonZero(cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE))
    }

def run_calibration(sct, monitor):
    print("="*60 + "\n>>> 自動キャリブレーションを開始します <<<\n" + "="*60)
    print("【重要】3秒後、PC画面を【曲が始まる前の、音符が流れていないゲーム画面】にしてください。")
    time.sleep(3)
    print("\n測定中...")
    baselines = {"red": [], "blue": [], "yellow": [], "orange": []}
    for _ in range(30):
        pixels = get_pixel_count(sct, monitor)
        for color in baselines: baselines[color].append(pixels[color])
        time.sleep(0.01)
    
    final_baselines = {color: max(values) + 10 for color, values in baselines.items()}
    print("\nキャリブレーション完了！")
    print("このシステムは「むずかしい」のみで対応します")
    print("一部のゲームは対応しません")
    print("「可」を多めに「良」を少なめに人間が操作しているかのようにします")
    print(f"  基準 => 赤:{final_baselines['red']} 青:{final_baselines['blue']} 黄:{final_baselines['yellow']} 橙:{final_baselines['orange']}\n" + "="*60)
    return final_baselines

def main():
    hit_zone_left = ROI_LEFT + (TARGET_X_RELATIVE - HIT_ZONE_WIDTH // 2) + TIMING_ADJUSTMENT_PIXELS
    hit_zone_monitor = {"top": ROI_TOP, "left": hit_zone_left, "width": HIT_ZONE_WIDTH, "height": ROI_HEIGHT}
    
    try:
        with mss() as sct:
            baselines = run_calibration(sct, hit_zone_monitor)
            hit_thresholds = {
                "red": baselines["red"] * THRESHOLD_MULTIPLIER_RED, "red_large": baselines["red"] * LARGE_NOTE_MULTIPLIER,
                "blue": baselines["blue"] * THRESHOLD_MULTIPLIER_BLUE, "blue_large": baselines["blue"] * LARGE_NOTE_MULTIPLIER,
                "roll": max(baselines["yellow"], baselines["orange"]) * DRUM_ROLL_THRESHOLD_MULTIPLIER
            }

            if DEBUG_MODE: print("\n★★★ パーフェクト・チューニング版 デバッグモード ★★★")
            else: print("\n自動演奏を開始します。終了するには 'q' キーを長押ししてください。")

            last_hit_time = 0
            is_rolling = False
            roll_keys = ['f', 'j']
            key_index = 0

            while not keyboard.is_pressed('q'):
                pixels = get_pixel_count(sct, hit_zone_monitor)
                current_time = time.time()
                
                is_roll_note_present = pixels["yellow"] > hit_thresholds["roll"] or pixels["orange"] > hit_thresholds["roll"]

                if is_roll_note_present:
                    is_rolling = True
                    pyautogui.press(roll_keys[key_index])
                    key_index = 1 - key_index
                    if DEBUG_MODE: print("ROLLING! ROLLING! ROLLING! ROLLING! ROLLING! ROLLING!", end='\r')
                    continue
                
                if not is_roll_note_present and is_rolling:
                    is_rolling = False
                    last_hit_time = current_time

                if not is_rolling and (current_time - last_hit_time > COOLDOWN):
                    if pixels["red"] > hit_thresholds["red_large"]: pyautogui.press(['f', 'j']); last_hit_time = current_time
                    elif pixels["red"] > hit_thresholds["red"]: pyautogui.press('f'); last_hit_time = current_time
                    elif pixels["blue"] > hit_thresholds["blue_large"]: pyautogui.press(['d', 'k']); last_hit_time = current_time
                    elif pixels["blue"] > hit_thresholds["blue"]: pyautogui.press('d'); last_hit_time = current_time

                if DEBUG_MODE and not is_rolling:
                    r_hit = "大!" if pixels["red"] > hit_thresholds['red_large'] else ("良!" if pixels["red"] > hit_thresholds['red'] else "---")
                    b_hit = "大!" if pixels["blue"] > hit_thresholds['blue_large'] else ("良!" if pixels["blue"] > hit_thresholds['blue'] else "---")
                    print(f"赤: 現在 {pixels['red']:<4} [{r_hit}] | 青: 現在 {pixels['blue']:<4} [{b_hit}]", end='\r')
                    
    finally:
        print("\nプログラムが停止しました。")

if __name__ == "__main__":
    main()