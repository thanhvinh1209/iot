import matplotlib.pyplot as plt
from datetime import datetime
import os
import sys

# Đảm bảo Terminal hiển thị được ký tự tiếng Việt Unicode trên mọi hệ điều hành
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Đường dẫn file log
LOG_FILENAME = "log.txt"
# Đường dẫn file lưu biểu đồ ảnh
CHART_FILENAME = "chart.png"

def generate_sample_data():
    """
    Sinh dữ liệu mẫu nếu chưa có file log.txt để người dùng chạy thử đồ thị ngay lập tức.
    """
    print(f"Không tìm thấy file {LOG_FILENAME}. Tự động tạo dữ liệu mẫu để vẽ đồ thị...")
    sample_lines = [
        "2026-06-22 08-00-00 24oC 55%",
        "2026-06-22 08-10-00 25oC 56%",
        "2026-06-22 08-20-00 26oC 58%",
        "2026-06-22 08-30-00 28oC 60%",
        "2026-06-22 08-40-00 27oC 62%",
        "2026-06-22 08-50-00 29oC 65%",
        "2026-06-22 09-00-00 30oC 63%",
        "2026-06-22 09-10-00 31oC 60%",
        "2026-06-22 09-20-00 29oC 59%",
        "2026-06-22 09-30-00 28oC 58%",
    ]
    with open(LOG_FILENAME, "w", encoding="utf-8") as f:
        for line in sample_lines:
            f.write(line + "\n")

def parse_log_file():
    """
    Đọc và phân tích cú pháp dữ liệu từ file log.txt.
    Trả về: (timestamps, temperatures, humidities)
    """
    if not os.path.exists(LOG_FILENAME):
        generate_sample_data()

    timestamps = []
    temperatures = []
    humidities = []

    with open(LOG_FILENAME, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                # Định dạng dòng log: yyyy-mm-dd hh-mm-ss xxoC xx%
                # Ví dụ: 2026-06-22 08-35-00 25oC 60%
                parts = line.split()
                if len(parts) < 4:
                    print(f"Cảnh báo: Bỏ qua dòng {idx} không đúng định dạng: '{line}'")
                    continue
                
                # Ghép ngày và giờ để chuyển thành đối tượng datetime
                dt_str = f"{parts[0]} {parts[1]}"
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H-%M-%S")
                
                # Trích xuất số từ "xxoC" và "xx%"
                temp = float(parts[2].replace("oC", ""))
                humi = float(parts[3].replace("%", ""))
                
                timestamps.append(dt)
                temperatures.append(temp)
                humidities.append(humi)
            except Exception as e:
                print(f"Lỗi khi phân tích dòng {idx}: '{line}' -> {e}")
                continue

    return timestamps, temperatures, humidities

def plot_and_save_data():
    """
    Vẽ đồ thị đường biểu diễn nhiệt độ và độ ẩm với trục Y kép (twin Y axis)
    và lưu đồ thị thành file ảnh.
    """
    timestamps, temperatures, humidities = parse_log_file()
    
    if not timestamps:
        print("Lỗi: Không tìm thấy dữ liệu hợp lệ trong file log để vẽ đồ thị.")
        return

    # Thiết lập giao diện đồ thị phong cách hiện đại và chuyên nghiệp
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
    
    # Tạo Figure và Axes chính
    fig, ax1 = plt.subplots(figsize=(11, 6))

    # Vẽ đường Nhiệt độ (Trục Y bên trái - màu đỏ cam)
    color_temp = '#e74c3c'
    ax1.set_xlabel('Thời gian (yyyy-mm-dd hh-mm-ss)', fontweight='bold', labelpad=10)
    ax1.set_ylabel('Nhiệt độ (°C)', color=color_temp, fontweight='bold', labelpad=10)
    line1, = ax1.plot(timestamps, temperatures, color=color_temp, marker='o', 
                      linewidth=2, markersize=5, label='Nhiệt độ (°C)')
    ax1.tick_params(axis='y', labelcolor=color_temp)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Tạo trục Y thứ hai cho Độ ẩm (Trục Y bên phải - màu xanh dương)
    ax2 = ax1.twinx()
    color_humi = '#3498db'
    ax2.set_ylabel('Độ ẩm (%)', color=color_humi, fontweight='bold', labelpad=10)
    line2, = ax2.plot(timestamps, humidities, color=color_humi, marker='s', 
                      linewidth=2, markersize=5, linestyle='--', label='Độ ẩm (%)')
    ax2.tick_params(axis='y', labelcolor=color_humi)

    # Tiêu đề biểu đồ
    plt.title('Đồ thị Giám sát Nhiệt độ & Độ ẩm theo thời gian thực (DHT11)', 
              fontsize=14, fontweight='bold', pad=20)

    # Gom hai chú thích (legend) làm một
    lines = [line1, line2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', edgecolor='none')

    # Định dạng hiển thị ngày giờ trên trục X tự động giãn cách đẹp mắt
    fig.autofmt_xdate()
    plt.tight_layout()

    # Lưu đồ thị thành file ảnh png để đưa lên GitHub
    plt.savefig(CHART_FILENAME, dpi=300)
    print(f"Đã lưu biểu đồ thành công vào: {CHART_FILENAME}")

    # Hiển thị đồ thị ra màn hình cửa sổ (Nếu chạy trong môi trường GUI)
    print("Đang hiển thị biểu đồ...")
    plt.show()

if __name__ == "__main__":
    plot_and_save_data()
