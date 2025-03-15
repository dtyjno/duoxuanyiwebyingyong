import mmap
import os
import struct
import time
import logging
from multiprocessing import Lock, Event

class SharedMemoryChannel:
    """
    高性能共享内存通信通道
    特征：
    - 支持多进程并发访问
    - 自动内存管理
    - 超时机制
    - 数据校验
    """
    def __init__(self, name='ipc_channel', mem_size=4096):
        self.name = name
        self.mem_size = mem_size
        self.lock = Lock()
        self.data_event = Event()
        self._init_shared_memory()
        self.logger = logging.getLogger('SharedMemory')

    def _init_shared_memory(self):
        """初始化共享内存区域"""
        self.file_path = f"/dev/shm/{self.name}"
        
        # 创建或打开共享内存文件
        self.fd = os.open(self.file_path, os.O_CREAT | os.O_RDWR)
        os.ftruncate(self.fd, self.mem_size)
        
        # 内存映射
        self.mmap = mmap.mmap(
            self.fd, 
            self.mem_size, 
            access=mmap.ACCESS_WRITE
        )
        
        # 初始化头信息：魔数(4B) + 数据长度(4B) + 校验和(4B)
        if self.mmap.read(12) == b'':
            header = struct.pack('III', 0xDEADBEEF, 0, 0)
            self.mmap.seek(0)
            self.mmap.write(header)
            self.mmap.flush()

    def write(self, data, timeout=5.0):
        """
        写入数据到共享内存
        :param data: 要写入的字节数据
        :param timeout: 超时时间（秒）
        """
        start_time = time.time()
        with self.lock:
            while True:
                if self._get_data_length() == 0:
                    break
                if time.time() - start_time > timeout:
                    raise TimeoutError("Write timeout")
                time.sleep(0.001)

            # 计算校验和
            checksum = self._calculate_checksum(data)
            
            # 打包头信息
            header = struct.pack('III', 
                0xDEADBEEF,       # 魔数
                len(data),        # 数据长度
                checksum          # CRC32校验
            )
            
            # 写入数据
            self.mmap.seek(0)
            self.mmap.write(header)
            self.mmap.write(data)
            self.mmap.flush()
            self.data_event.set()
            self.logger.debug(f"Wrote {len(data)} bytes")

    def read(self, timeout=5.0):
        """
        从共享内存读取数据
        :param timeout: 超时时间（秒）
        :return: 读取的字节数据
        """
        start_time = time.time()
        while not self.data_event.is_set():
            if time.time() - start_time > timeout:
                raise TimeoutError("Read timeout")
            time.sleep(0.001)

        with self.lock:
            # 读取头信息
            self.mmap.seek(0)
            header = self.mmap.read(12)
            magic, length, checksum = struct.unpack('III', header)
            
            if magic != 0xDEADBEEF:
                raise ValueError("Invalid magic number")
            
            # 读取数据
            data = self.mmap.read(length)
            
            # 校验数据
            if self._calculate_checksum(data) != checksum:
                raise ValueError("Data checksum mismatch")
            
            # 清空数据区
            self.mmap.seek(0)
            self.mmap.write(struct.pack('III', 0xDEADBEEF, 0, 0))
            self.mmap.flush()
            self.data_event.clear()
            
            self.logger.debug(f"Read {len(data)} bytes")
            return data

    def close(self):
        """清理资源"""
        self.mmap.close()
        os.close(self.fd)
        try:
            os.unlink(self.file_path)
        except FileNotFoundError:
            pass
        self.logger.info("Channel closed")

    def _get_data_length(self):
        """获取当前数据长度"""
        self.mmap.seek(4)
        return struct.unpack('I', self.mmap.read(4))[0]

    def _calculate_checksum(self, data):
        """计算CRC32校验和"""
        crc = 0
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xEDB88320
                else:
                    crc >>= 1
        return crc & 0xFFFFFFFF

if __name__ == '__main__':
    # 测试用例
    logging.basicConfig(level=logging.DEBUG)
    channel = SharedMemoryChannel()
    
    # 写入测试
    test_data = b"Hello, Shared Memory!"
    channel.write(test_data)
    
    # 读取测试
    received = channel.read()
    print(f"Received: {received.decode()}")
    
    channel.close()
