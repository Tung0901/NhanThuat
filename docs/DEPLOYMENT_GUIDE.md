# HƯỚNG DẪN TRIỂN KHAI DOANH NGHIỆP • NHÂN THUẬT PLATFORM
*Tài liệu hướng dẫn vận hành & triển khai On-Premise, Docker & Cloud VPS*

---

## 1. Yêu Cầu Hệ Thống (System Requirements)

- **CPU:** Tối thiểu 1 vCPU (Khuyến nghị 2 vCPU).
- **RAM:** Tối thiểu 1 GB RAM (Khuyến nghị 2 GB RAM).
- **Disk:** Tối thiểu 2 GB dung lượng trống.
- **Hệ điều hành:** Linux (Ubuntu 22.04 LTS, Debian 12, RHEL 9), macOS, hoặc Windows Server.
- **Python:** Python 3.10+ (Đã bao gồm `sqlite3` chuẩn).
- **Môi trường:** 100% Offline-capable (Không bắt buộc kết nối Internet ngoài).

---

## 2. Phương Án 1: Triển Khai Nhanh Qua Docker & Docker Compose (Khuyến Nghị)

### Bước 1: Khởi động hệ thống
```bash
# Clone repository
git clone https://github.com/Tung0901/NhanThuat.git
cd NhanThuat

# Khởi động dịch vụ nền bằng Docker Compose
docker-compose up -d --build
```

### Bước 2: Kiểm tra trạng thái
```bash
# Kiểm tra log vận hành
docker-compose logs -f

# Kiểm tra probe sức khỏe (Healthcheck)
curl http://127.0.0.1:8000/health
```

Giao diện Web Dashboard sẽ tự động khả dụng tại: `http://localhost:8000/`

---

## 3. Phương Án 2: Triển Khai Trực Tiếp Trên Linux VPS (Systemd & Nginx)

### Bước 1: Thiết lập môi trường Python ảo
```bash
cd /opt/NhanThuat
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Bước 2: Tạo Systemd Service File `/etc/systemd/system/nhanthuat.service`
```ini
[Unit]
Description=NhanThuat BusinessOS API Gateway
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/NhanThuat
Environment="PATH=/opt/NhanThuat/.venv/bin"
Environment="PORT=8000"
Environment="HOST=127.0.0.1"
ExecStart=/opt/NhanThuat/.venv/bin/python scripts/run_web_dashboard.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Kích hoạt dịch vụ:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nhanthuat.service
```

### Bước 3: Cấu hình Reverse Proxy Nginx có SSL
```nginx
server {
    listen 80;
    server_name nhanthuat.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name nhanthuat.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/nhanthuat.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nhanthuat.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 4. Phương Án 3: Triển Khai Miễn Phí / Tự Động Trên Render / Railway

1. Tạo Web Service mới trên **Render.com**.
2. Chọn **Build Type:** Docker hoặc Python.
3. Cấu hình biến môi trường:
   - `PORT`: `8000`
   - `PYTHONUNBUFFERED`: `1`
4. **Health Check Path:** `/health`
5. Nhấn **Deploy**.

---

## 5. Tích Hợp SDK Doanh Nghiệp (Client Integration)

### Python Integration
```python
from sdk.python.nhan_thuat_sdk import NhanThuatClient

# 1. Chế độ in-process trực tiếp (Zero Network / Air-Gapped)
client = NhanThuatClient(mode="local")

# 2. Hoặc kết nối qua REST API Gateway
# client = NhanThuatClient(base_url="https://nhanthuat.yourdomain.com", mode="http")

# Triệu tập Hội đồng Cố vấn 5 trường phái
result = client.deliberate_council("Đối tác nợ 5 tỷ quá hạn 90 ngày dọa đơn phương thanh lý hợp đồng")
print("Đồng thuận cao nhất:", result["deliberation"]["decision_matrix"]["highest_consensus"])
```

### TypeScript / Node.js Integration
```typescript
import { NhanThuatClient } from "@nhan-thuat/sdk";

const client = new NhanThuatClient({ baseUrl: "https://nhanthuat.yourdomain.com" });

async function run() {
  const res = await client.deliberateCouncil("Công trình Nhà Bè chậm tiến độ do vật tư");
  console.log("Phương án A:", res.deliberation.decision_matrix.plan_a_primary);
}
run();
```
