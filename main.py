import os, time
from screen_viewer import Screen
from slm_ctrl import SLM
from camera import HikCamera
from fn import collect_images

# ==== 配置（直接写死，不用 argparse）====
SCENE_DIR   = "scenes"      # 显示器图片目录
MASK_DIR    = "masks"       # SLM 掩膜目录
OUT_DIR     = "captures"    # 保存相机拍摄结果
MONITOR_IDX = 1             # 显示器索引
EXPOSURE_US = 20000.0       # 曝光时间（微秒）
TIMEOUT_MS  = 3000          # 相机超时时间（毫秒）
SETTLE_MS   = 30            # 等待稳定（毫秒）

# ==== 初始化 ====
os.makedirs(OUT_DIR, exist_ok=True)

disp_imgs = collect_images(SCENE_DIR)["images"]
slm_imgs  = collect_images(MASK_DIR)["images"]

if not disp_imgs:
    print("[ERR] 显示器目录下没有图片")
    exit(1)
if not slm_imgs:
    print("[ERR] 掩膜目录下没有图片")
    exit(1)

scr = Screen(monitor_index=MONITOR_IDX)
slm = SLM(verbose=True)
cam = HikCamera(dev_index=0)

try:
    slm.init()
    if not cam.open():
        print("[ERR] 相机打开失败")
        exit(2)

    # ==== 两层循环：每个场景 × 每个掩膜 ====
    for dpath in disp_imgs:
        scr.show_image(dpath)
        for spath in slm_imgs:
            slm.img_show(spath)
            time.sleep(SETTLE_MS/1000.0)  # 等待刷新稳定

            # 生成输出文件名
            dname = os.path.splitext(os.path.basename(dpath))[0]
            sname = os.path.splitext(os.path.basename(spath))[0]
            out_path = os.path.join(OUT_DIR, f"{dname}__{sname}.jpg")

            ok = cam.snap(out_path, exposure_us=EXPOSURE_US,
                          timeout_ms=TIMEOUT_MS, img_type="jpeg")
            print("[OK]" if ok else "[ERR]", "拍摄 ->", out_path)

    print("\n[DONE] 全部拍摄完成。")

finally:
    cam.close()
    slm.close()
    scr.close()