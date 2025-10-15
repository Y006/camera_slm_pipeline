# Camera-SLM Pipeline

本项目用于控制 SLM（空间光调制器） 与 相机（HikCamera） 的联合实验流程，包括 PSF 拍摄、测量模式 以及 标定模式。

### 🚀 快速开始 (Quick Start)

1. 克隆仓库

   ```shell
   git clone https://github.com/Y006/camera_slm_pipeline.git
   cd camera-slm-pipeline
   ```

3. 配置参数

   修改 config.yaml 文件，一个基础的示例如下，其中没有填写的内容为选填内容，但是为了实验的可复现性应该尽可能多的填写：

   ```yaml
   project:
     id: 2025-10-15-exp001
     root_dir: "./output"
     description: ""
   
   task:
     mode: "capture_measurement"     # 可选: calibration | capture_psf | capture_measurement
     repeat: 1               # 拍摄次数
     description: ""
   
   capture_settings:
     exposure_us: 581046.0000
     monitor_idx: 2
     scale_factor: 0.27
     display_position: (0,0)   # 功能需要在代码里面修改以启用
     display_image_path: "D:/qjy/camera_slm_pipeline/data/example/分辨率测试卡.jpg"
     slm_image_path: "D:/qjy/camera_slm_pipeline/data/fza_bin_gen/FZA_bin_R25.png"
   
   physical_setup:
     object_name: ""
     brightness: ""
     sensor_mask_distance: ""
     mask_object_distance1: ""
     mask_object_distance2: ""
     point_light_brightness: 
     mask_LED-light_distance: ""
   ```

   在 `capture_settings` 和 `physical_setup` 中可以添加你自己想添加的参数，结果会存储在日志文件 `\output\run.yaml` 中。

4. 运行代码：

   ```shell
   python main.py
   ```

   运行后，根据 task.mode 不同，将进入以下模式：

   - calibration: 标定模式，仅显示，不记录数据
   - capture_psf: 拍摄 PSF 图像
   - capture_measurement: 拍摄测量图像

   输出文件及日志将写入 ./output/ 目录。
