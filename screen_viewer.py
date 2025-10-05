import tkinter as tk
from PIL import Image, ImageTk
from PIL.Image import Resampling
from screeninfo import get_monitors

class Screen:
    def __init__(self, monitor_index: int = 0, bg: str = "black"):
        """在 init 中选定显示器，并创建全屏 Tk 窗口与 Canvas。"""
        self.root = tk.Tk()
        self.root.configure(bg=bg)
        self.root.overrideredirect(True)     # 无边框
        self.root.bind("<Escape>", lambda e: self.close())

        # 选择目标显示器几何信息
        if get_monitors:
            mons = get_monitors()
        else:
            mons = []

        if not mons:
            x, y = 0, 0
            w = self.root.winfo_screenwidth()
            h = self.root.winfo_screenheight()
        else:
            m = mons[min(max(0, monitor_index), len(mons) - 1)]
            x, y, w, h = m.x, m.y, m.width, m.height

        self.geom = (x, y, w, h)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.canvas = tk.Canvas(self.root, width=w, height=h,
                                highlightthickness=0, bg=bg)
        self.canvas.pack(fill="both", expand=True)

        self._tkimg = None  # 保存引用，防止 GC

    def show_image(self, img_path: str) -> bool:
        """只做渲染，不进入 mainloop，返回是否成功显示。"""
        try:
            x, y, w, h = self.geom
            pil = Image.open(img_path).convert("RGB")
            in_w, in_h = pil.size
            scale = min(w / in_w, h / in_h)
            new_size = (max(1, int(in_w * scale)), max(1, int(in_h * scale)))
            out = pil.resize(new_size, Resampling.LANCZOS)

            self.canvas.delete("all")
            self._tkimg = ImageTk.PhotoImage(out)
            self.canvas.create_image(w // 2, h // 2, image=self._tkimg, anchor="center")

            print(f"[INFO] 成功显示: {img_path}")
            print(f"       原始尺寸: {in_w}x{in_h}, 显示尺寸: {new_size[0]}x{new_size[1]}")
            return True
        except Exception as e:
            print(f"[ERROR] 显示失败: {img_path}, 错误: {e}")
            return False

    def start(self):
        """进入事件循环（只进一次）"""
        self.root.mainloop()

    def close(self):
        try:
            self.root.destroy()
        except Exception:
            pass


