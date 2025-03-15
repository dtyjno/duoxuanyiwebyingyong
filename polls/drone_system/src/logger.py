# 可视化延迟时间监控
from rich.live import Live
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import BarColumn, Progress
from rich.color import Color
import time
import threading
import numpy as np
import colorsys

class EnhancedDelayLogger:
    def __init__(self):
        self.console = Console()
        self.delay_data = []
        self.lock = threading.Lock()
        self._running = threading.Event()
        self._running.set()
        threading.Thread(target=self.start_monitoring, daemon=True).start()

    def log_delay(self, timestamp, delay):
        with self.lock:
            self.delay_data.append((timestamp, delay))
            if len(self.delay_data) > 20:  # 保留最近20条记录
                self.delay_data.pop(0)

    def _get_stats(self):
        with self.lock:
            delays = [d[1] for d in self.delay_data]
            return {
                "current": delays[-1] if delays else 0,
                "average": np.mean(delays) if delays else 0,
                "max": max(delays) if delays else 0,
                "min": min(delays) if delays else 0,
                "std": np.std(delays) if len(delays)>1 else 0
            }

    def _colorize_delay(self, delay):
        """根据延迟值返回颜色化的文本"""
        if delay < 0.1:
            return Text(f"{delay:.4f}", style="bold green")
        elif 0.1 <= delay < 0.5:
            return Text(f"{delay:.4f}", style="bold yellow")
        else:
            return Text(f"{delay:.4f}", style="bold red")

    def _generate_main_panel(self):
        stats = self._get_stats()
        
        # 创建动态标题
        title_text = Text("网络延迟监控 ")
        title_text.append("●", style="bold green" if stats["current"] < 0.1 else "bold red")
        
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="right")
        
        # 统计信息表格
        stats_table = Table(box=None, show_header=False)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value")
        stats_table.add_row("当前延迟", self._colorize_delay(stats["current"]))
        stats_table.add_row("平均延迟", f"{stats['average']:.4f}")
        stats_table.add_row("最大延迟", f"{stats['max']:.4f}")
        stats_table.add_row("标准差", f"{stats['std']:.4f}")
        
        # 延迟趋势图
        trend = Text("\n".join(
            "█" * int(30 * d[1]) + " " * (30 - int(30 * d[1])) 
            for d in self.delay_data[-5:]
        ), style="blue")
        
        # # 进度条
        # progress = Progress(
        #     BarColumn(bar_width=40, complete_style="rgb(50,200,50)", finished_style="rgb(100,255,100)"),
        #     transient=True
        # )
        # task = progress.add_task("", total=1.0)
        # progress.update(task, completed=stats["current"])
        
        grid.add_row(stats_table, trend)
        
        return Panel(
            grid,
            # progress,
            title=title_text,
            subtitle=f"更新于 {time.strftime('%H:%M:%S')}",
            style=self._get_panel_style(stats["current"])
        )

    def _get_panel_style(self, current_delay):
        """根据当前延迟动态调整面板样式"""
        hue = 120 - min(current_delay * 120, 120)  # 从绿到红的色相变化
        r, g, b = colorsys.hsv_to_rgb(hue / 360, 0.8, 0.8)
        # border_color = Color.from_rgb(int(r * 255), int(g * 255), int(b * 255))
        hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
        return f"bold {hex_color}"

    def start_monitoring(self):
        with Live(refresh_per_second=4, console=self.console) as live:
            while self._running.is_set():
                try:
                    live.update(self._generate_main_panel())
                    time.sleep(0.25)
                except KeyboardInterrupt:
                    self.stop()

    def stop(self):
        self._running.clear()

# 使用示例
if __name__ == "__main__":
    logger = EnhancedDelayLogger()

    # 模拟延迟数据生成
    def generate_test_data():
        base_delay = 0.05
        while True:
            current_delay = abs(base_delay + np.random.normal(0, 0.1))
            logger.log_delay(time.time(), current_delay) # 记录延迟
            time.sleep(0.3)

    # threading.Thread(target=generate_test_data, daemon=True).start()
    # logger.start_monitoring()
    while True:
        try:
            generate_test_data()
        except KeyboardInterrupt:
            logger.stop()
            break
        # logger.log_delay(time.time(), np.random.random())
