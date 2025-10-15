import os
import time
import yaml
import threading
from src.screen_viewer import Screen
from src.slm_ctrl import SLM
from src.camera import HikCamera
from MvImport.MvCameraControl_class import *
from utils.auto_exp_id import next_experiment_id

CONFIG_PATH = "config.yaml"  # 可替换为实际路径
exp_id, config = next_experiment_id(CONFIG_PATH)
if not config["task"]["mode"] == "calibration":
    out_dir = os.path.join(config["project"]["root_dir"], exp_id)
    os.makedirs(out_dir, exist_ok=True)
    if config["logging"]["save_config_copy"]:
        with open(CONFIG_PATH, "r", encoding="utf-8") as src, \
            open(os.path.join(out_dir, "config_snapshot.yaml"), "w", encoding="utf-8") as dst:
            dst.write(src.read())
        snapshot_path = os.path.join(out_dir, "config_snapshot.yaml")
        os.chmod(snapshot_path, 0o444)  # 只读权限

def display_image(display_image_path, monitor_idx, scale_factor):
    """在新线程中显示图片，保持显示器持续显示"""
    try:
        # 创建 Screen 对象，选择第一个显示器（默认选择第一个显示器）
        scr = Screen(monitor_index=monitor_idx, bg="black")
        
        # 显示图像（请确保图像路径正确）
        if not os.path.exists(display_image_path):
            print("[ERR] 显示器图片路径无效")
            exit(3)
        
        scr.show_image(display_image_path, scale_factor)
        scr.start()  # 启动 Tkinter 事件循环
    except Exception as e:
        print(f"[ERROR] 显示图像时出错: {e}")

def main():
    
    if config["task"]["mode"] == "capture_psf":
        use_display = False
        use_slm     = True
        use_camera  = True
    if config["task"]["mode"] == "capture_measurement":
        use_display = True
        use_slm     = True
        use_camera  = True
    if config["task"]["mode"] == "calibration":
        use_display = True
        use_slm     = True
        use_camera  = False
    imaging_cfg = config["imaging_config"]

    try:
        if use_slm:    
            slm = SLM(verbose=True)
            settle_ms = 30
            slm.init()

        if use_camera:
            cam = HikCamera(dev_index=0)
            timeout_ms = 3000
            if not cam.open():
                print("[ERR] 相机打开失败")
                exit(2)
            
        if use_display:
            print("[INFO] 启动显示器显示线程")
            display_thread = threading.Thread(
                target=display_image,
                args=(
                    imaging_cfg["display_image_path"],
                    imaging_cfg["monitor_idx"],
                    imaging_cfg["scale_factor"]
                )
            )
            display_thread.daemon = True
            display_thread.start()

        if use_slm:
            if not os.path.exists(imaging_cfg["slm_image_path"]):
                print("[ERR] SLM图片路径无效")
                exit(4)
            slm.img_show(imaging_cfg["slm_image_path"])
            time.sleep(settle_ms / 1000.0)

        if config["task"]["mode"] == "calibration":
            print("[INFO] 进入标定模式，保持显示器和SLM显示，按 Ctrl+C 退出或等待1000秒后自动退出")
            time.sleep(10000)  # 保持足够时间用于手动对焦等操作

        if use_camera:
            if config["task"]["mode"] == "capture_psf":
                image_name = "psf"
            if config["task"]["mode"] == "capture_measurement":
                image_name = "measurement"
            out_path = os.path.join(
                out_dir,
                f"{image_name}.jpg"
            )
            ok = cam.snap(
                out_path,
                exposure_us=imaging_cfg["exposure_us"],
                timeout_ms=timeout_ms,
                img_type=MV_Image_Jpeg
            )
            if ok:
                if config["task"]["mode"] == "capture_psf":
                    print(f"[OK] PSF 拍摄成功!")
                if config["task"]["mode"] == "capture_measurement":
                    print(f"[OK] Measurement 拍摄成功!")
            else:
                print("[ERR] 拍摄失败！")

    finally:
        if use_camera:
            cam.close()

if __name__ == "__main__":
    main()
