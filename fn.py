import os
import re
from typing import Dict, List

def collect_images(folder: str) -> Dict[str, List[str]]:
    """
    遍历文件夹及子文件夹，收集所有常见图片路径（自然排序），
    返回一个字典，并在控制台打印格式化 log 信息。
    """
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff", ".webp"}

    def _natural_key(s: str):
        return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

    if not os.path.exists(folder):
        raise FileNotFoundError(f"指定路径不存在: {folder}")

    images: List[str] = []
    for root, _, files in os.walk(folder):
        for name in files:
            _, ext = os.path.splitext(name)
            if ext.lower() in exts:
                images.append(os.path.abspath(os.path.join(root, name)))

    images.sort(key=_natural_key)

    n = len(images)
    if n == 0:
        log = f"[LOG] 在 {folder} 内未找到任何图片文件。"
    else:
        preview = images[:3] + (["..."] if n > 6 else []) + images[-3:]
        log = (
            f"[LOG] 扫描完成: 共找到 {n} 张图片\n"
            f"       目录: {folder}\n"
            f"       示例文件:\n         " + "\n         ".join(preview)
        )
    print(log)

    return {"images": images}
