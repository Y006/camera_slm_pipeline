# =============================================================================
# 脚本用途与用法（请先阅读）
# -----------------------------------------------------------------------------
# 功能：
#   - 拍摄一张测量值：  「显示器显示图片→SLM显示掩膜→相机拍摄图片→保存图片到磁盘」
#   - 拍摄一张 PSF：    「SLM显示掩膜→相机拍摄图片→保存图片到磁盘」
#
# 需要设置的变量（见“需要修改的配置”区）：
#   - SLM_IMAGE_PATH（必填）：SLM 要显示的图片路径；路径必须存在，否则跳过本轮并报错。
#   - IMAGE_NAME（必填）：拍摄结果文件名（例如 "mea3.jpg"）；为空将报错并跳过本轮。
#   - DISPLAY_IMAGE_PATH（可选）：显示器要显示的图片路径；为空则会跳过显示器步骤，对应为拍摄 PSF。
#   - SAVE_PATH（可选）：相机拍摄结果保存目录；为空则保存到当前工作目录；非空若目录不存在会自动创建。
#
# 运行方式：
#   - 直接执行：python single_shot.py
#
# 其他说明：
#   - 图片保存使用 JPEG（MV_Image_Jpeg）。
# =============================================================================
import os
import time
import threading
from screen_viewer import Screen
from slm_ctrl import SLM
from camera import HikCamera
from MvImport.MvCameraControl_class import *

# ==== 需要修改的配置 ====
EXPOSURE_US        = 2499233.0  # 曝光时间（微秒）
MONITOR_IDX        = 2          # 选择显示器索引（从0开始），如果只有一个显示器则为0
scale_factor       = 1.0        # 缩放因子，可以修改为 0.5, 1.0 等
DISPLAY_IMAGE_PATH = r"D:\Lzy\dataset\dogvscat v2\1.png"  # 显示器图片路径（可以为空，如果为空则对应拍摄 psf）
SLM_IMAGE_PATH     = r"D:\qjy\camera_slm_pipeline\fza_patten_gen_masked_r60\FZA_256_R16.png"  # SLM图片的路径（必须提供）
IMAGE_NAME         = "demo.jpg" # 拍摄的图像名称
SAVE_PATH          = r"D:\qjy\camera_slm_pipeline\reslt_1010"  # 图片保存路径，如果为空，则默认保存到当前工作目录

# ==== 一般不需要修改的配置 ====
DEFAULT_SAVE_PATH = os.getcwd()
TIMEOUT_MS  = 3000            # 相机超时时间（毫秒）
SETTLE_MS   = 30             # 等待稳定（毫秒）

# ==== 初始化 ====
slm = SLM(verbose=True)
cam = HikCamera(dev_index=0)

def display_image():
    """在新线程中显示图片，保持显示器持续显示"""
    try:
        # 创建 Screen 对象，选择第一个显示器（默认选择第一个显示器）
        scr = Screen(monitor_index=MONITOR_IDX, bg="black")
        
        # 显示图像（请确保图像路径正确）
        if not os.path.exists(DISPLAY_IMAGE_PATH):
            print("[ERR] 显示器图片路径无效")
            return
        
        scr.show_image(DISPLAY_IMAGE_PATH, scale_factor)
        scr.start()  # 启动 Tkinter 事件循环
    except Exception as e:
        print(f"[ERROR] 显示图像时出错: {e}")

def main():
    try:
        # 初始化 SLM 和相机
        slm.init()
        if not cam.open():
            print("[ERR] 相机打开失败")
            exit(2)

        # 如果保存路径为空，则使用默认的当前目录
        if SAVE_PATH.strip() == "":
            save_path = DEFAULT_SAVE_PATH
        else:
            save_path = SAVE_PATH
            # 检查路径是否存在，不存在则创建
            if not os.path.exists(save_path):
                print(f"[INFO] 保存路径不存在，正在创建：{save_path}")
                os.makedirs(save_path)

        # 在新线程中开始显示图片
        display_thread = threading.Thread(target=display_image)
        display_thread.daemon = True  # 使线程在主程序退出时结束
        display_thread.start()

        while True:
            # 如果SLM图片路径为空，则打印错误并跳过
            if not os.path.exists(SLM_IMAGE_PATH):
                print("[ERR] SLM图片路径无效")
                continue

            # 在SLM上显示图片
            slm.img_show(SLM_IMAGE_PATH)
            time.sleep(SETTLE_MS / 1000.0)  # 等待稳定

            # 如果没有拍摄图像名称，打印错误
            if not IMAGE_NAME:
                print("[ERR] 拍摄图像名称未提供")
                continue

            # 拍摄图像并保存
            out_path = os.path.join(SAVE_PATH, IMAGE_NAME)
            os.makedirs(SAVE_PATH, exist_ok=True)
            ok = cam.snap(out_path, exposure_us=EXPOSURE_US, timeout_ms=TIMEOUT_MS, img_type=MV_Image_Jpeg)

            if ok:
                print(f"[OK] 拍摄成功，保存路径 -> {out_path}")
            else:
                print(f"[ERR] 拍摄失败，保存路径 -> {out_path}")

            break

    finally:
        if cam is not None:
            cam.close()
            print("[INFO] 相机已关闭")

        print("\n[DONE] 任务完成!\n\n")

if __name__ == "__main__":
    main()
