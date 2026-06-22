import os
import sys
import sounddevice as sd
import wavio
from openai import OpenAI

# Đảm bảo Terminal hiển thị được ký tự tiếng Việt Unicode trên mọi hệ điều hành
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Tên file âm thanh tạm thời lưu bản ghi
AUDIO_FILENAME = "input.wav"

# Tần số lấy mẫu mặc định cho xử lý giọng nói (16 kHz)
SAMPLE_RATE = 16000
# Thời gian ghi âm (giây)
DURATION_SEC = 2

# Tên model STT.
# - Theo slide SIC (Trang 92, 101): "gpt-4o-transcribe" hoặc "gpt-4o-mini-transcribe"
# - Theo chuẩn API OpenAI mặc định: "whisper-1"
# Bạn có thể đổi tên model này tùy thuộc vào endpoint/hệ thống của giảng viên cung cấp.
MODEL_NAME = "gpt-4o-transcribe"

def record_audio(filename=AUDIO_FILENAME, duration=DURATION_SEC, samplerate=SAMPLE_RATE):
    """
    Ghi âm từ Microphone và lưu vào file WAV.
    """
    print(f"\n---> Bắt đầu ghi âm trong {duration} giây. Hãy nói ngay...")
    try:
        # Ghi âm ở chế độ mono (channels=1), định dạng số nguyên 16-bit
        audio_data = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="int16"
        )
        sd.wait()  # Chờ cho đến khi quá trình ghi âm hoàn tất
        print("---> Đã ghi âm xong!")
        
        # Lưu ra file wav
        wavio.write(filename, audio_data, samplerate, sampwidth=2)
        print(f"---> Đã lưu file ghi âm vào: {filename}")
        return True
    except Exception as e:
        print(f"\n[Lỗi] Không thể ghi âm từ micro: {e}")
        print("Vui lòng kiểm tra lại thiết bị thu âm (micro USB/micro của laptop).")
        return False

def transcribe_audio(filename=AUDIO_FILENAME):
    """
    Gửi file âm thanh đến OpenAI API để chuyển đổi giọng nói thành văn bản (STT).
    """
    # 1. Kiểm tra API Key từ biến môi trường
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n" + "="*80)
        print("[LỖI] Chưa cấu hình API Key của OpenAI!")
        print("Vui lòng thiết lập biến môi trường 'OPENAI_API_KEY' trước khi chạy chương trình.")
        print("Cách thiết lập:")
        print("  - Trên Windows (PowerShell): $env:OPENAI_API_KEY=\"sk-proj-...\"")
        print("  - Trên Linux/Raspberry Pi: export OPENAI_API_KEY=\"sk-proj-...\"")
        print("="*80 + "\n")
        return None

    # 2. Khởi tạo OpenAI Client (tự động đọc OPENAI_API_KEY từ môi trường)
    try:
        client = OpenAI()
    except Exception as e:
        print(f"\n[Lỗi] Không thể khởi tạo OpenAI Client: {e}")
        return None

    # 3. Gửi file ghi âm lên mô hình STT
    print(f"\n---> Đang gửi file '{filename}' đến OpenAI STT (Model: {MODEL_NAME})...")
    if not os.path.exists(filename):
        print(f"[Lỗi] Không tìm thấy file âm thanh '{filename}' để gửi.")
        return None

    try:
        with open(filename, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=MODEL_NAME,
                file=audio_file,
                response_format="text",
                prompt="The user will speak English commands such as 'turn on', 'turn off', or 'blink'."
            )
            # Dọn dẹp khoảng trắng
            text = response.strip()
            return text
    except Exception as e:
        print(f"\n[Lỗi] Có lỗi xảy ra trong quá trình gọi API OpenAI: {e}")
        print("Lưu ý: Nếu bạn sử dụng tài khoản OpenAI chuẩn, hãy thử đổi MODEL_NAME thành 'whisper-1'.")
        return None

def main():
    print("=" * 60)
    print("   CHƯƠNG TRÌNH SPEECH-TO-TEXT (BÀI 3 - SIC)   ")
    print("=" * 60)

    # Lựa chọn giữa ghi âm mới hoặc chạy thử file wav có sẵn
    choice = "y"
    if os.path.exists(AUDIO_FILENAME):
        try:
            choice = input(f"Phát hiện file '{AUDIO_FILENAME}' có sẵn. Bạn có muốn ghi âm ĐÈ lên không? (y/n): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nĐã hủy.")
            return

    if choice == "y":
        success = record_audio()
        if not success:
            if os.path.exists(AUDIO_FILENAME):
                print(f"Sử dụng file '{AUDIO_FILENAME}' cũ để tiếp tục thử nghiệm...")
            else:
                print("Chương trình dừng lại vì không có file âm thanh.")
                return
    else:
        print(f"Sử dụng file '{AUDIO_FILENAME}' có sẵn.")

    # Tiến hành chuyển đổi giọng nói thành văn bản
    text = transcribe_audio()
    
    if text:
        print("\n" + "=" * 60)
        print(f"Kết quả nhận dạng được (Recognized Text):")
        print(f"  --> \" {text} \"")
        print("=" * 60)
    else:
        print("\nKhông thể nhận dạng được giọng nói do lỗi API hoặc cấu hình.")

if __name__ == "__main__":
    main()
