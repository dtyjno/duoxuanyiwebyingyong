import threading
import logging
from typing import Dict, Tuple

class ThreadManager:
    def __init__(self):
        self.threads: Dict[str, Tuple[threading.Thread, threading.Event]] = {}
        # 结构: {线程名: (线程对象, 停止事件)}

    def start_thread(self, target, name: str, args=()):
        """为每个线程创建独立的Event并启动"""
        if name in self.threads:
            logging.warning(f"Thread {name} already exists!")
            return

        # 创建线程专属的Event
        stop_event = threading.Event()
        try:
            # 创建线程，传递独立的stop_event
            t = threading.Thread(
                name=name,
                target=self.thread_wrapper,
                args=(target.run, stop_event) + args,
                daemon=False  # 设置为非守护线程    
            )
            t.start()
            self.threads[name] = (t, stop_event)
            logging.info(f"Started {name} (Thread ID: {t.ident})")
        except Exception as e:
            logging.error(f"Failed to start {name}: {str(e)}")
            self.safe_shutdown()

    def thread_wrapper(self, target_func, stop_event, *args):
        """包装器函数，传递独立stop_event"""
        try:
            target_func(*args, stop_event=stop_event)
        except Exception as e:
            logging.error(f"Thread error: {str(e)}", exc_info=True)
        finally:
            logging.info(f"Thread {threading.current_thread().name} exited.")

    def stop_thread(self, name: str, timeout=5):
        """停止单个线程"""
        if name not in self.threads:
            logging.warning(f"Thread {name} does not exist!")
            return

        t, stop_event = self.threads[name]
        stop_event.set()  # 触发该线程的停止事件
        t.join(timeout=timeout)
        if t.is_alive():
            logging.warning(f"Thread {name} did not exit within {timeout}s!")
        else:
            del self.threads[name]  # 移除已停止的线程记录

    def stop_all(self, timeout=5):
        """停止所有线程"""
        for name in list(self.threads.keys()):  # 避免迭代时修改字典
            self.stop_thread(name, timeout=timeout)

    def safe_shutdown(self):
        """安全关闭所有线程"""
        self.stop_all()
        logging.info("All threads stopped.")

class ExampleTask:
    def run(self, arg1, arg2, stop_event=None):
        """示例任务函数，接收独立的stop_event"""
        while not stop_event.is_set():
            logging.info(f"Processing {arg1}, {arg2}...")
            # 使用事件等待代替time.sleep，及时响应停止
            stop_event.wait(1)  # 每隔1秒检查一次
        logging.info(f"Task {arg1}-{arg2} received stop signal.")


if __name__ == "__main__":
    manager = ThreadManager()
    task1 = ExampleTask()
    task2 = ExampleTask()

    # 启动两个独立线程
    manager.start_thread(target=task1, name="Worker-1", args=("A", "X"))
    manager.start_thread(target=task2, name="Worker-2", args=("B", "Y"))

    # 运行一段时间后停止Worker-1
    import time
    time.sleep(3)
    manager.stop_thread("Worker-1")

    # 继续运行一段时间后停止所有线程
    time.sleep(2)
    manager.stop_all()
