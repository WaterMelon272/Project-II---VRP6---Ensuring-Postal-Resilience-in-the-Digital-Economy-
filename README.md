# TCPVRP — Hệ thống Tối ưu hóa Lộ trình Thu gom và Giao hàng có Ràng buộc Thời gian

Một hệ thống quản lý logistics trên nền tảng web nhằm giải quyết Bài toán Định tuyến Phương tiện (VRP) với các ràng buộc về khung thời gian (time windows), điểm lấy-giao hàng (pickup-delivery), và dữ liệu mạng lưới giao thông thực tế. Hệ thống sử dụng Thuật toán Di truyền (Genetic Algorithm) ở backend được cung cấp qua máy chủ FastAPI và giao diện frontend React/TypeScript để quản lý tương tác đơn hàng và phương tiện.

---

## Tính năng nổi bật

- **Thuật toán Di truyền (Genetic Algorithm solver)** — Tối ưu hóa lộ trình cho nhiều phương tiện, nhiều chuyến đi dưới các ràng buộc về trọng lượng, thể tích, khung thời gian, hàng hóa không tương thích và khoảng cách.
- **Định tuyến trên đường thực tế (Real road routing)** — Truy xuất thời gian di chuyển và khoảng cách thực tế từ một phiên bản OSRM; tự động chuyển sang ước tính theo đường chim bay khi không có kết nối.
- **Giao diện bản đồ tương tác (Interactive map UI)** — Thêm/sửa đơn hàng và xe, trực quan hóa lộ trình trực tiếp trên bản đồ Leaflet.
- **Kéo thả để chỉnh sửa lộ trình (Drag-and-drop route editing)** — Sắp xếp lại thứ tự các điểm dừng thủ công và tính toán lại chi phí ngay lập tức.
- **Cập nhật tiến độ theo thời gian thực (Live progress streaming)** — Sử dụng Server-Sent Events (SSE) để đẩy tiến độ tối ưu hóa từ server lên trình duyệt theo thời gian thực.
- **Mô phỏng hành trình (Route simulation)** — Thanh trượt thời gian (time-slider) giúp tạo hiệu ứng hoạt hình cho quá trình giao hàng trong ngày.

---

## Cấu trúc Dự án

## Project Structure

TCPVRP/
├── vrp_project/          # Backend Python
│   ├── main.py           # Ứng dụng FastAPI & các API endpoints
│   ├── schemas.py        # Các model Pydantic cho request/response
│   ├── requirements.txt  # Các thư viện Python cần thiết
│   └── vrp/
│       ├── core/         # Định nghĩa bài toán, cấu trúc giải pháp và hàm đánh giá chi phí
│       ├── solvers/      # Thuật toán GA_TCPVRP và các thuật toán thay thế
│       ├── data/         # Load dữ liệu đầu vào
│       ├── utils/        # Các hàm hỗ trợ hiển thị
│       └── experiments/  # Script chạy các kịch bản kiểm thử hàng loạt
│
└── vrp-frontend/         # Frontend React + TypeScript
├── src/
│   ├── App.tsx        # Component gốc và quản lý state
│   ├── MapView.tsx    # Bản đồ Leaflet với các layer lộ trình/đơn hàng
│   └── components/   # Các panel quản lý: Xe, Đơn hàng, Kết quả, Bảng điều khiển mô phỏng
├── package.json
└── vite.config.ts

---
## Yêu cầu Hệ thống

| Công cụ | Phiên bản tối thiểu | Ghi chú |
|------|----------------|-------|
| Python | 3.10+ | Dành cho Backend |
| Node.js | 18+ | Dành cho Frontend |
| npm | 9+ | Trình quản lý gói cho Frontend |
| OSRM | Bất kỳ | Tùy chọn — cung cấp thời gian/khoảng cách thực tế. Backend sẽ tự fallback về đường chim bay nếu không có. |

---

## Hướng dẫn Cài đặt

### 1. Backend

```powershell
cd vrp_project

# Tạo và kích hoạt môi trường ảo (virtual environment)
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1   # Windows PowerShell
# source .venv/bin/activate    # macOS / Linux

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# Khởi chạy API server
python main.py

Server sẽ chạy tại địa chỉ http://127.0.0.1:8000.

Để chạy với chế độ auto-reload trong quá trình code:
uvicorn main:app --reload --host 127.0.0.1 --port 8000

### 2. Frontend


cd vrp-frontend

# Cài đặt các gói phụ thuộc
npm install

# Khởi chạy development server
npm run dev

Ứng dụng sẽ mở tại địa chỉ http://localhost:5173.

### 2. OSRM (tùy chọn)
Theo mặc định, backend sẽ gọi API OSRM tại http://router.project-osrm.org. Đối với môi trường offline hoặc production, bạn nên chạy một instance OSRM nội bộ và cập nhật biến OSRM_BASE_URL trong file vrp_project/main.py.

## Hướng dẫn sử dụng

1. Mở trình duyệt và truy cập http://localhost:5173.

2. Thêm phương tiện trong bảng quản lý Xe — thiết lập tải trọng, chi phí/km, tỷ lệ làm thêm giờ và khung giờ hoạt động.

3. Thêm đơn hàng bằng cách click trực tiếp trên bản đồ hoặc dùng bảng quản lý Đơn hàng — xác định tọa độ lấy/giao, khung giờ yêu cầu, khối lượng, thể tích và loại hàng hóa.

4. Click nút "Chạy thuật toán" để bắt đầu quá trình tối ưu.

    - Thanh tiến trình sẽ cập nhật liên tục khi thuật toán GA đang chạy (mặc định giới hạn trong 10 giây).

    - Kết quả sẽ hiện ra dưới dạng các đường màu sắc trên bản đồ và bảng chỉ đường chi tiết trong bảng Kết quả.

5. Kéo thả các điểm dừng trong một lộ trình để sắp xếp lại theo ý muốn, sau đó click "Tính toán lại" để cập nhật chi phí mới.

6. Sử dụng thanh trượt mô phỏng để xem hoạt ảnh xe di chuyển thực hiện các nhiệm vụ giao nhận theo thời gian.

## Tài liệu API
Tất cả các endpoint được cung cấp bởi backend FastAPI tại http://127.0.0.1:8000.

## Tổng quan Thuật toán

Trình giải cốt lõi (vrp/solvers/ga_tcpvrp.py) là một Thuật toán Di truyền được thiết kế riêng cho bài toán VRP nhiều chuyến, lấy-giao hàng:

Cấu trúc nhiễm sắc thể (Chromosome) — mã hóa mức độ ưu tiên của lộ trình, số điểm dừng trên mỗi lộ trình, và việc gán đơn hàng cho xe.

Khởi tạo tham lam (Greedy initialization) — chèn hàng xóm gần nhất (nearest-neighbour) kết hợp với các phép gán hạt giống thỏa mãn ràng buộc.

Hàm thích nghi (Fitness function) — cực tiểu hóa tổng chi phí (khoảng cách × đơn giá) cộng với các điều khoản phạt khi vi phạm khung thời gian, vượt tải hoặc quá giờ.

Thông số cấu hình — kích thước quần thể 100, tối đa 500 thế hệ, thời gian chạy tối đa (wall-clock) 10 giây.

Kho bưu chính mặc định (Depot): Bưu điện Trung tâm Hà Nội (21.0245°N, 105.8412°E).
