# Báo cáo Tổng hợp Kết quả Thực nghiệm eBPF vs Iptables trên Kubernetes (K3s)

> **Cấu hình thực nghiệm:** K3s single-node (`worker-2`, 4 vCPU / 4 GB RAM) + Máy sinh tải ngoài cụm (`worker-1`, 2 vCPU / 2 GB RAM), lưu lượng External-to-Service qua NodePort `30080`. Mỗi kịch bản thực hiện lặp **3 lần đo độc lập (n=3)** để lấy giá trị trung bình (Mean) và độ lệch chuẩn (Std).

---

## 1. Kịch bản 1: Hiệu năng Cơ bản (L4 Throughput & L7 Latency ở 2.000 RPS)

| Chỉ số | Calico (iptables) Mean ± Std | Cilium (eBPF) Mean ± Std | Mức cải thiện (Cilium vs Calico) |
|---|---|---|---|
| **L4 Throughput (`iperf3`)** | 94.08 ± 0.23 Mbps | **96.99 ± 0.15 Mbps** | **+3.1%** |
| **L7 Latency p50 (`wrk2`)** | 3.74 ± 0.06 ms | **3.51 ± 0.04 ms** | **-6.2%** |
| **L7 Latency p90 (`wrk2`)** | 9.66 ± 0.21 ms | **7.13 ± 0.10 ms** | **-26.3%** |
| **L7 Tail Latency p99 (`wrk2`)** | 57.43 ± 1.40 ms | **27.23 ± 0.67 ms** | **-52.6%** |
| **L7 Latency p99.9 (`wrk2`)** | 168.62 ± 3.40 ms | **66.89 ± 1.61 ms** | **-60.3%** |

---

## 2. Kịch bản 2: Khả năng Mở rộng & Thời gian Lập trình Rule (50 → 1.500 Services)

| Quy mô Services | Calico CPS (RPS) | Cilium CPS (RPS) | Calico p99 (ms) | Cilium p99 (ms) | Thời gian nạp rule Calico vs Cilium |
|---|---|---|---|---|---|
| **50 rules** | 2917.7 ± 12.3 | **2984.2 ± 3.4** | 84.6 ms | **41.4 ms** | 0.35s vs **0.05s** |
| **500 rules** | 2685.2 ± 16.3 | **2975.1 ± 3.9** | 246.4 ms | **43.1 ms** | 1.85s vs **0.12s** |
| **1000 rules** | 2375.4 ± 16.9 | **2964.5 ± 4.3** | 584.3 ms | **45.3 ms** | 4.35s vs **0.21s** |
| **1500 rules** | 2034.3 ± 21.1 | **2952.0 ± 4.5** | 1146.7 ms | **47.6 ms** | 7.86s vs **0.31s** |

- **Phân tích $O(N)$ vs $O(1)$:** Khi tăng từ 50 lên 1.500 rules, thông lượng CPS của **Calico giảm 30.3%** và p99 tăng vọt gấp **13.5 lần** do phải duyệt tuần tự chuỗi `KUBE-SERVICES` và khóa `xtables.lock` khi chạy `iptables-restore`. Ngược lại, **Cilium eBPF** giữ thông lượng ổn định gần như tuyệt đối (**giảm chỉ 1.1%**) nhờ tra cứu bảng băm BPF Maps $O(1)$ và cập nhật nguyên tử.

---

## 3. Kịch bản 3A & 3B: Tải Bão hòa, Ngắt mềm SoftIRQ & Chi phí Giám sát Hubble

| Chỉ số đo (400 conn, target 20.000 RPS) | Calico (iptables) | Cilium (Hubble OFF) | Cilium (Hubble ON) |
|---|---|---|---|
| **Thông lượng bão hòa (RPS)** | 7301.3 ± 47.2 | **9642.3 ± 51.9** (**+32.1%**) | 9438.2 ± 42.7 (giảm **2.1%**) |
| **Độ trễ p99 (ms)** | 264.2 ms | **168.4 ms** | 176.2 ms |
| **CPU Busy trên Worker-2 (%)** | 85.5% | **66.9%** (tiết kiệm **18.6%**) | 71.2% (+4.3%) |
| **SoftIRQ `NET_RX` (/giây)** | 4134 /s | **2582 /s** (**-37.5%**) | 2633 /s |
| **RAM tiêu thụ (MB)** | 1345 MB | 1410 MB | 1505 MB (+95 MB) |
| **Socket timeouts** | 10–14 timeouts | **0** | **0** |

- **Kết luận 3A:** eBPF giúp loại bỏ đường đi dài qua Netfilter hooks, giảm **37.5%** tần suất ngắt mềm `SoftIRQ NET_RX` và tiết kiệm **18.6%** CPU, giúp thông lượng cực đại tăng **+32.1%** không có lỗi timeout.
- **Kết luận 3B:** Bật Cilium Hubble Relay trích xuất luồng L3/L4 qua eBPF Ring Buffer chỉ tốn thêm **+4.3% CPU**, **+95 MB RAM** và làm giảm thông lượng rất thấp (**2.1%**), phù hợp cho giám sát Production thời gian thực.
