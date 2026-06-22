import time
from datetime import datetime
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Cố gắng import thư viện Adafruit_DHT dành cho Raspberry Pi.
# Nếu không có (ví dụ chạy trên máy tính Windows để test), tự động chuyển sang chế độ giả lập.
try:
    import Adafruit_DHT
    HAS_HARDWARE = True
except ImportError:
    HAS_HARDWARE = False
    import random

# Cấu hình chân GPIO và loại cảm biến
DHT_SENSOR = None
if HAS_HARDWARE:
    DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 20

# Tên file log đầu ra
LOG_FILENAME = "log.txt"

def read_sensor_data():
    """
    Đọc dữ liệu từ cảm biến DHT11 thật hoặc giả lập nếu chạy trên PC.
    Trả về: (nhiệt độ, độ ẩm)
    """
    if HAS_HARDWARE:
        # Đọc từ cảm biến thật trên Raspberry Pi
        # Hàm read_retry sẽ tự động thử lại nhiều lần nếu đọc thất bại
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        return temperature, humidity
    else:
        # Chế độ giả lập trên PC: sinh dữ liệu ngẫu nhiên hợp lệ
        # Nhiệt độ từ 20 đến 35 độ C, Độ ẩm từ 40% đến 80%
        temperature = random.randint(20, 35)
        humidity = random.randint(40, 80)
        # Giả lập thời gian đọc cảm biến khoảng 0.5s
        time.sleep(0.5)
        return temperature, humidity

def run_logger(interval_seconds=2):
    """
    Vòng lặp đọc dữ liệu liên tục và ghi vào file log.txt
    """
    print("=" * 60)
    if HAS_HARDWARE:
        print(f"Bắt đầu đọc cảm biến DHT11 thật trên chân GPIO {DHT_PIN}...")
    else:
        print("Không phát hiện phần cứng Raspberry Pi. Chạy ở chế độ GIẢ LẬP (Simulation Mode).")
    print(f"Dữ liệu ghi log sẽ được lưu vào file: {LOG_FILENAME}")
    print("Nhấn Ctrl+C để dừng chương trình.")
    print("=" * 60)

    try:
        while True:
            temp, humi = read_sensor_data()
            
            if temp is not None and humi is not None:
                # Lấy thời gian hệ thống theo định dạng yyyy-mm-dd hh-mm-ss
                timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                
                # Định dạng log: yyyy-mm-dd hh-mm-ss xxoC xx%
                # Lưu ý: "xxoC" sử dụng chữ o thường và C hoa như yêu cầu đề bài
                log_line = f"{timestamp} {int(temp)}oC {int(humi)}%"
                
                # In ra Terminal để theo dõi trực quan
                print(f"[LOGGED] {log_line}")
                
                # Ghi đè/Nối tiếp vào file log.txt
                with open(LOG_FILENAME, "a", encoding="utf-8") as file:
                    file.write(log_line + "\n")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Lỗi: Không thể đọc được dữ liệu từ cảm biến DHT11!")
            
            # Đợi một khoảng thời gian trước lần đọc tiếp theo
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình ghi log.")

if __name__ == "__main__":
    # Khoảng cách giữa mỗi lần ghi log mặc định là 2 giây
    run_logger(interval_seconds=2)
