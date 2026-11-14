"""Generate two publication-quality technical diagrams for the eBPF vs Iptables K3s report:
1. fig_topology.png            - Cisco Packet Tracer style network topology (2 VMs + L2 Switch + Control PC)
2. fig_system_architecture.png - Layered system architecture & dual packet datapath (Calico iptables vs Cilium eBPF)
"""
import math
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, FancyArrowPatch

OUT_DIRS = [
    r"C:\Users\LOG\.gemini\antigravity\scratch\ebpf-k8s-report\images",
    r"C:\Users\LOG\.gemini\antigravity\brain\25bf54ce-0978-4062-a4f0-82e155a4ea24",
]
for d in OUT_DIRS:
    os.makedirs(d, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def save_both(fig, filename):
    paths = []
    for d in OUT_DIRS:
        p = os.path.join(d, filename)
        fig.savefig(p, dpi=220, bbox_inches="tight", facecolor="white")
        paths.append(p)
    plt.close(fig)
    return paths


def draw_arrow(ax, p_from, p_to, color="#0f172a", lw=2.0, ls="-", mscale=14, style="-|>", zorder=6, rad=0.0):
    """Consistent crisp vector arrow helper."""
    conn = f"arc3,rad={rad}" if rad != 0.0 else "arc3,rad=0"
    arr = FancyArrowPatch(
        p_from, p_to,
        connectionstyle=conn,
        arrowstyle=style,
        mutation_scale=mscale,
        color=color,
        lw=lw,
        linestyle=ls,
        zorder=zorder,
    )
    ax.add_patch(arr)
    return arr


# ==============================================================================
# HELPER ICONS (Cisco Packet Tracer Device Silhouettes)
# ==============================================================================
def draw_cisco_switch(ax, cx, cy, w=2.35, h=1.02):
    """Draw a 3D isometric-style Cisco Catalyst 2960 L2 Switch with 4 staggered white arrows."""
    dx, dy = 0.28, 0.32
    front = Polygon(
        [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2),
         (cx + w / 2, cy + h / 2 - 0.14), (cx - w / 2, cy + h / 2 - 0.14)],
        closed=True, facecolor="#0369a1", edgecolor="#0c4a6e", lw=1.8, zorder=5
    )
    ax.add_patch(front)
    top = Polygon(
        [(cx - w / 2, cy + h / 2 - 0.14), (cx + w / 2, cy + h / 2 - 0.14),
         (cx + w / 2 + dx, cy + h / 2 - 0.14 + dy), (cx - w / 2 + dx, cy + h / 2 - 0.14 + dy)],
        closed=True, facecolor="#0ea5e9", edgecolor="#0c4a6e", lw=1.6, zorder=5
    )
    ax.add_patch(top)
    side = Polygon(
        [(cx + w / 2, cy - h / 2), (cx + w / 2 + dx, cy - h / 2 + dy),
         (cx + w / 2 + dx, cy + h / 2 - 0.14 + dy), (cx + w / 2, cy + h / 2 - 0.14)],
        closed=True, facecolor="#075985", edgecolor="#0c4a6e", lw=1.6, zorder=5
    )
    ax.add_patch(side)

    tcx, tcy = cx + dx * 0.48, cy + h / 2 - 0.14 + dy * 0.50
    draw_arrow(ax, (tcx - 0.85, tcy + 0.085), (tcx + 0.02, tcy + 0.085), color="white", lw=1.6, mscale=8, style="->")
    draw_arrow(ax, (tcx + 0.85, tcy + 0.025), (tcx - 0.02, tcy + 0.025), color="white", lw=1.6, mscale=8, style="->")
    draw_arrow(ax, (tcx - 0.85, tcy - 0.035), (tcx + 0.02, tcy - 0.035), color="white", lw=1.6, mscale=8, style="->")
    draw_arrow(ax, (tcx + 0.85, tcy - 0.095), (tcx - 0.02, tcy - 0.095), color="white", lw=1.6, mscale=8, style="->")

    panel = FancyBboxPatch(
        (cx - w / 2 + 0.14, cy - h / 2 + 0.14), w - 0.28, 0.35,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        facecolor="#0f172a", edgecolor="#38bdf8", lw=0.9, zorder=6
    )
    ax.add_patch(panel)
    for i in range(8):
        px = cx - w / 2 + 0.22 + i * 0.245
        ax.add_patch(patches.Rectangle((px, cy - h / 2 + 0.20), 0.16, 0.17,
                                       facecolor="#334155", edgecolor="#94a3b8", lw=0.7, zorder=7))
        led_col = "#22c55e" if i in (0, 1, 2) else "#64748b"
        ax.add_patch(Circle((px + 0.08, cy - h / 2 + 0.42), 0.030, facecolor=led_col, edgecolor="none", zorder=7))
    return cx - w / 2, cx + w / 2 + dx


def draw_pt_workstation(ax, cx, cy):
    """Draw a Packet Tracer style PC Tower + Monitor icon."""
    mon = FancyBboxPatch((cx - 0.90, cy - 0.14), 1.04, 0.74,
                         boxstyle="round,pad=0.02,rounding_size=0.06",
                         facecolor="#1e293b", edgecolor="#0f172a", lw=1.6, zorder=5)
    ax.add_patch(mon)
    scr = FancyBboxPatch((cx - 0.82, cy - 0.05), 0.88, 0.56,
                         boxstyle="round,pad=0.01,rounding_size=0.03",
                         facecolor="#0ea5e9", edgecolor="#38bdf8", lw=1.0, zorder=6)
    ax.add_patch(scr)
    for i, lw_len in enumerate([0.62, 0.44, 0.54]):
        ax.plot([cx - 0.72, cx - 0.72 + lw_len], [cy + 0.38 - i * 0.13, cy + 0.38 - i * 0.13],
                color="#e0f2fe", lw=1.6, zorder=7)
    ax.add_patch(Polygon([(cx - 0.46, cy - 0.14), (cx - 0.30, cy - 0.14),
                          (cx - 0.22, cy - 0.30), (cx - 0.54, cy - 0.30)],
                         closed=True, facecolor="#475569", edgecolor="#0f172a", lw=1.2, zorder=5))
    ax.add_patch(FancyBboxPatch((cx - 0.64, cy - 0.35), 0.52, 0.065,
                                boxstyle="round,pad=0.01,rounding_size=0.02",
                                facecolor="#334155", edgecolor="#0f172a", lw=1.1, zorder=5))
    tower = FancyBboxPatch((cx + 0.26, cy - 0.35), 0.56, 1.00,
                           boxstyle="round,pad=0.02,rounding_size=0.05",
                           facecolor="#334155", edgecolor="#0f172a", lw=1.6, zorder=5)
    ax.add_patch(tower)
    ax.add_patch(patches.Rectangle((cx + 0.34, cy + 0.42), 0.40, 0.11, facecolor="#1e293b", edgecolor="#64748b", lw=0.8, zorder=6))
    ax.add_patch(patches.Rectangle((cx + 0.34, cy + 0.24), 0.40, 0.09, facecolor="#1e293b", edgecolor="#64748b", lw=0.8, zorder=6))
    for k in range(3):
        ax.plot([cx + 0.35, cx + 0.73], [cy - 0.09 - k * 0.08, cy - 0.09 - k * 0.08], color="#94a3b8", lw=1.1, zorder=6)
    ax.add_patch(Circle((cx + 0.54, cy + 0.08), 0.048, facecolor="#22c55e", edgecolor="#dcfce7", lw=0.7, zorder=6))


def draw_pt_server(ax, cx, cy):
    """Draw a Packet Tracer style 3D Rack/Enterprise Server icon."""
    dx, dy = 0.20, 0.20
    w, h = 0.98, 1.12
    ax.add_patch(Polygon([(cx - w / 2, cy + h / 2), (cx + w / 2, cy + h / 2),
                          (cx + w / 2 + dx, cy + h / 2 + dy), (cx - w / 2 + dx, cy + h / 2 + dy)],
                         closed=True, facecolor="#38bdf8", edgecolor="#0f172a", lw=1.4, zorder=5))
    ax.add_patch(Polygon([(cx + w / 2, cy - h / 2), (cx + w / 2 + dx, cy - h / 2 + dy),
                          (cx + w / 2 + dx, cy + h / 2 + dy), (cx + w / 2, cy + h / 2)],
                         closed=True, facecolor="#0284c7", edgecolor="#0f172a", lw=1.4, zorder=5))
    front = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                           boxstyle="round,pad=0.01,rounding_size=0.04",
                           facecolor="#1e293b", edgecolor="#0f172a", lw=1.7, zorder=5)
    ax.add_patch(front)
    ax.add_patch(patches.Rectangle((cx - w / 2 + 0.08, cy + h / 2 - 0.21), w - 0.16, 0.12,
                                   facecolor="#0ea5e9", edgecolor="#7dd3fc", lw=0.8, zorder=6))
    for ybay in [cy + 0.15, cy - 0.07, cy - 0.29]:
        ax.add_patch(patches.Rectangle((cx - w / 2 + 0.10, ybay), w - 0.20, 0.15,
                                       facecolor="#334155", edgecolor="#64748b", lw=0.9, zorder=6))
        ax.add_patch(Circle((cx + w / 2 - 0.17, ybay + 0.075), 0.034, facecolor="#22c55e", edgecolor="none", zorder=7))
        ax.plot([cx - w / 2 + 0.15, cx + 0.14], [ybay + 0.075, ybay + 0.075], color="#cbd5e1", lw=1.4, zorder=7)
    for k in range(4):
        vx = cx - 0.30 + k * 0.20
        ax.add_patch(patches.Rectangle((vx, cy - h / 2 + 0.08), 0.12, 0.09, facecolor="#475569", zorder=6))


def draw_pt_laptop(ax, cx, cy):
    """Draw a Packet Tracer style Controller Laptop / PC icon."""
    lid = FancyBboxPatch((cx - 0.54, cy), 1.08, 0.68,
                         boxstyle="round,pad=0.02,rounding_size=0.05",
                         facecolor="#1e293b", edgecolor="#0f172a", lw=1.5, zorder=5)
    ax.add_patch(lid)
    scr = FancyBboxPatch((cx - 0.46, cy + 0.07), 0.92, 0.54,
                         boxstyle="round,pad=0.01,rounding_size=0.03",
                         facecolor="#38bdf8", edgecolor="#bae6fd", lw=0.9, zorder=6)
    ax.add_patch(scr)
    ax.plot([cx - 0.34, cx - 0.14, cx + 0.06, cx + 0.32],
            [cy + 0.20, cy + 0.44, cy + 0.28, cy + 0.50], color="white", lw=2.0, zorder=7)
    base = Polygon([(cx - 0.54, cy), (cx + 0.54, cy),
                    (cx + 0.72, cy - 0.28), (cx - 0.72, cy - 0.28)],
                   closed=True, facecolor="#64748b", edgecolor="#0f172a", lw=1.5, zorder=5)
    ax.add_patch(base)
    kb = Polygon([(cx - 0.44, cy - 0.05), (cx + 0.44, cy - 0.05),
                  (cx + 0.54, cy - 0.18), (cx - 0.54, cy - 0.18)],
                 closed=True, facecolor="#1e293b", edgecolor="none", zorder=6)
    ax.add_patch(kb)


def draw_link_dot(ax, x, y, direction="right"):
    """Packet Tracer style green link status LED triangle."""
    s = 0.085
    if direction == "right":
        pts = [(x - s, y + s * 0.8), (x - s, y - s * 0.8), (x + s, y)]
    elif direction == "left":
        pts = [(x + s, y + s * 0.8), (x + s, y - s * 0.8), (x - s, y)]
    elif direction == "up":
        pts = [(x - s * 0.8, y - s), (x + s * 0.8, y - s), (x, y + s)]
    else:
        pts = [(x - s * 0.8, y + s), (x + s * 0.8, y + s), (x, y - s)]
    ax.add_patch(Polygon(pts, closed=True, facecolor="#22c55e", edgecolor="#14532d", lw=0.9, zorder=8))


# ==============================================================================
# DIAGRAM 1: CISCO PACKET TRACER STYLE NETWORK TOPOLOGY
# ==============================================================================
def make_topology():
    fig, ax = plt.subplots(figsize=(16, 10.0))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10.0)
    ax.axis("off")

    ax.add_patch(FancyBboxPatch((0.15, 0.15), 15.7, 9.7,
                                boxstyle="round,pad=0.05,rounding_size=0.18",
                                facecolor="#f8fafc", edgecolor="#cbd5e1", lw=1.5, zorder=0))
    for gx in range(1, 16):
        for gy in range(1, 10):
            ax.plot(gx, gy, ".", color="#e2e8f0", markersize=2.5, zorder=1)

    ax.add_patch(FancyBboxPatch((0.35, 9.02), 15.3, 0.68,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor="#1e3a8a", edgecolor="#172554", lw=1.2, zorder=2))
    ax.text(8.0, 9.42, "SƠ ĐỒ TOPOLOGY MẠNG THỰC NGHIỆM 2 VM (MÔ HÌNH CISCO PACKET TRACER)",
            ha="center", va="center", color="white", fontsize=13.5, fontweight="bold", zorder=3)
    ax.text(8.0, 9.15, "Mạng LAN Ethernet 1 Gbps (Subnet 192.168.10.0/24)  |  Lưu lượng External-to-Service qua L2 Ethernet Switch",
            ha="center", va="center", color="#bfdbfe", fontsize=9.8, zorder=3)

    ax.add_patch(FancyBboxPatch((0.35, 2.95), 4.65, 4.95,
                                boxstyle="round,pad=0.04,rounding_size=0.16",
                                facecolor="#fff7ed", edgecolor="#ea580c", lw=1.8, linestyle="--", zorder=2))
    ax.text(2.675, 7.66, "Máy vật lý 1 (VirtualBox Bridged Adapter)",
            ha="center", va="center", fontsize=9.5, fontweight="bold", color="#9a3412",
            bbox=dict(boxstyle="round,pad=0.24", facecolor="#ffedd5", edgecolor="#fdba74", lw=1.0), zorder=3)

    draw_pt_workstation(ax, 2.65, 6.48)

    ax.add_patch(FancyBboxPatch((0.55, 3.12), 4.25, 2.68,
                                boxstyle="round,pad=0.03,rounding_size=0.12",
                                facecolor="white", edgecolor="#fb923c", lw=1.3, zorder=4))
    ax.add_patch(FancyBboxPatch((0.55, 5.38), 4.25, 0.42,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="#ea580c", edgecolor="none", zorder=5))
    ax.text(2.675, 5.59, "VM 1: worker-1 (Load Generator — Ngoài cụm)",
            ha="center", va="center", color="white", fontsize=9.8, fontweight="bold", zorder=6)
    ax.text(2.675, 5.14, "IP: 192.168.10.20 / 24   |   NIC: eth0",
            ha="center", va="center", color="#0f172a", fontsize=9.4, fontweight="bold", zorder=6)
    ax.text(2.675, 4.82, "Cấu hình: 2 vCPU  |  2 GB RAM  |  Ubuntu 22.04 Headless",
            ha="center", va="center", color="#334155", fontsize=8.6, zorder=6)

    for px, py, pw, ph, lbl, col in [
        (0.71, 4.10, 1.88, 0.56, "iperf3 (-t 30 -P 4)\nThông lượng TCP L4", "#e0f2fe"),
        (2.74, 4.10, 1.88, 0.56, "wrk2 (Open-loop)\nĐo HTTP L7 & CPS", "#fef3c7"),
        (0.71, 3.28, 3.91, 0.58, "chrony NTP Client (Đồng bộ < 1 ms với worker-2)\n& OpenSSH Server (nhận điều phối qua Port 22)", "#f1f5f9"),
    ]:
        ax.add_patch(FancyBboxPatch((px, py), pw, ph,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=col, edgecolor="#64748b", lw=0.9, zorder=5))
        ax.text(px + pw / 2, py + ph / 2, lbl,
                ha="center", va="center", color="#0f172a", fontsize=8.1, fontweight="semibold", zorder=6)

    ax.add_patch(FancyBboxPatch((11.00, 2.95), 4.65, 4.95,
                                boxstyle="round,pad=0.04,rounding_size=0.16",
                                facecolor="#eff6ff", edgecolor="#0284c7", lw=1.8, linestyle="--", zorder=2))
    ax.text(13.325, 7.66, "Máy vật lý 2 (VirtualBox Bridged Adapter)",
            ha="center", va="center", fontsize=9.5, fontweight="bold", color="#075985",
            bbox=dict(boxstyle="round,pad=0.24", facecolor="#dbeafe", edgecolor="#7dd3fc", lw=1.0), zorder=3)

    draw_pt_server(ax, 13.25, 6.45)

    ax.add_patch(FancyBboxPatch((11.20, 3.12), 4.25, 2.68,
                                boxstyle="round,pad=0.03,rounding_size=0.12",
                                facecolor="white", edgecolor="#38bdf8", lw=1.3, zorder=4))
    ax.add_patch(FancyBboxPatch((11.20, 5.38), 4.25, 0.42,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="#0284c7", edgecolor="none", zorder=5))
    ax.text(13.325, 5.59, "VM 2: worker-2 (K3s Single-Node SUT)",
            ha="center", va="center", color="white", fontsize=9.8, fontweight="bold", zorder=6)
    ax.text(13.325, 5.14, "IP: 192.168.10.30 / 24   |   NodePort: :30080",
            ha="center", va="center", color="#0f172a", fontsize=9.4, fontweight="bold", zorder=6)
    ax.text(13.325, 4.82, "Cấu hình: 4 vCPU  |  4 GB RAM  |  Kernel >= 5.15 LTS",
            ha="center", va="center", color="#334155", fontsize=8.6, zorder=6)

    for px, py, pw, ph, lbl, col in [
        (11.36, 4.10, 1.88, 0.56, "K3s Server + Agent\n50 → 1.500 Services", "#e0f2fe"),
        (13.39, 4.10, 1.88, 0.56, "Calico VXLAN (Baseline)\nvs Cilium eBPF (Tuần tự)", "#fce7f3"),
        (11.36, 3.28, 1.88, 0.58, "Pod target-server\nnginx:alpine (:80)", "#dcfce7"),
        (13.39, 3.28, 1.88, 0.58, "Hubble Relay (K3B)\n& collect_metrics.sh", "#ede9fe"),
    ]:
        ax.add_patch(FancyBboxPatch((px, py), pw, ph,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=col, edgecolor="#64748b", lw=0.9, zorder=5))
        ax.text(px + pw / 2, py + ph / 2, lbl,
                ha="center", va="center", color="#0f172a", fontsize=8.1, fontweight="semibold", zorder=6)

    sw_x, sw_y = 7.90, 5.45
    sw_left, sw_right = draw_cisco_switch(ax, sw_x, sw_y, w=2.20, h=1.02)
    ax.add_patch(FancyBboxPatch((5.95, 4.08), 4.10, 0.72,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor="white", edgecolor="#0284c7", lw=1.3, zorder=5))
    ax.text(8.0, 4.56, "L2 Ethernet Switch (Cisco Catalyst 2960)",
            ha="center", va="center", color="#0369a1", fontsize=9.7, fontweight="bold", zorder=6)
    ax.text(8.0, 4.28, "LAN Subnet: 192.168.10.0/24 (Chuyển mạch lớp 2 — 1 Gbps)",
            ha="center", va="center", color="#334155", fontsize=8.5, zorder=6)

    draw_pt_laptop(ax, 8.0, 2.22)
    ax.add_patch(FancyBboxPatch((5.15, 0.92), 5.70, 0.90,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor="white", edgecolor="#4f46e5", lw=1.4, zorder=5))
    ax.text(8.0, 1.60, "Control & Analysis PC (Windows Host: 192.168.10.10 / 24)",
            ha="center", va="center", color="#3730a3", fontsize=9.5, fontweight="bold", zorder=6)
    ax.text(8.0, 1.32, "Điều phối thực nghiệm tự động: run_experiment.py (SSH / SFTP Port 22)",
            ha="center", va="center", color="#1e293b", fontsize=8.5, zorder=6)
    ax.text(8.0, 1.07, "Tổng hợp & vẽ biểu đồ Mean ± Std: plot.py | Terminal Recorder",
            ha="center", va="center", color="#475569", fontsize=8.3, zorder=6)

    x1_l, x1_r, y1 = 5.00, sw_left, 5.45
    ax.plot([x1_l, x1_r], [y1, y1], color="#0f172a", lw=2.4, zorder=4)
    draw_link_dot(ax, x1_l + 0.14, y1, "right")
    draw_link_dot(ax, x1_r - 0.14, y1, "left")
    ax.text(x1_l + 0.56, y1 + 0.16, "eth0 (.20)", ha="center", va="bottom", fontsize=8.0, fontweight="bold", color="#0f172a", zorder=6)
    ax.text(x1_r - 0.42, y1 + 0.16, "Gi0/1", ha="center", va="bottom", fontsize=8.0, fontweight="bold", color="#0369a1", zorder=6)

    x2_l, x2_r, y2 = sw_right, 11.00, 5.45
    ax.plot([x2_l, x2_r], [y2, y2], color="#0f172a", lw=2.4, zorder=4)
    draw_link_dot(ax, x2_l + 0.14, y2, "right")
    draw_link_dot(ax, x2_r - 0.14, y2, "left")
    ax.text(x2_l + 0.42, y2 + 0.16, "Gi0/2", ha="center", va="bottom", fontsize=8.0, fontweight="bold", color="#0369a1", zorder=6)
    ax.text(x2_r - 0.56, y2 + 0.16, "eth0 (.30)", ha="center", va="bottom", fontsize=8.0, fontweight="bold", color="#0f172a", zorder=6)

    ax.plot([8.0, 8.0], [2.92, 4.08], color="#0f172a", lw=2.4, zorder=4)
    draw_link_dot(ax, 8.0, 3.06, "up")
    draw_link_dot(ax, 8.0, 3.94, "down")
    ax.text(8.18, 3.84, "Gi0/3", ha="left", va="center", fontsize=8.1, fontweight="bold", color="#0369a1", zorder=6)
    ax.text(8.18, 3.16, "NIC (.10)", ha="left", va="center", fontsize=8.1, fontweight="bold", color="#3730a3", zorder=6)

    draw_arrow(ax, (3.25, 7.96), (12.75, 7.96), color="#dc2626", lw=2.5,
               ls=(0, (6, 3)), mscale=16, style="-|>", zorder=7, rad=-0.10)
    ax.text(8.0, 8.58, "Luồng tải thực nghiệm External-to-Service (L4 iperf3 & L7 wrk2 → 192.168.10.30:30080)",
            ha="center", va="center", fontsize=9.1, fontweight="bold", color="#991b1b",
            bbox=dict(boxstyle="round,pad=0.28", facecolor="#fee2e2", edgecolor="#ef4444", lw=1.2), zorder=8)

    draw_arrow(ax, (5.15, 1.50), (2.675, 2.93), color="#4f46e5", lw=1.9, ls=":", mscale=14, style="-|>", zorder=6, rad=-0.22)
    ax.text(3.40, 1.98, "SSH: Kích hoạt wrk2 / iperf3\nSFTP: Kéo worker1_out/",
            ha="center", va="center", fontsize=8.3, color="#312e81", fontweight="semibold",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#eef2ff", edgecolor="#818cf8", lw=1.0), zorder=7)

    draw_arrow(ax, (10.85, 1.50), (13.325, 2.93), color="#4f46e5", lw=1.9, ls=":", mscale=14, style="-|>", zorder=6, rad=0.22)
    ax.text(12.60, 1.98, "SSH: Triển khai rules & K3s\nSFTP: Kéo metrics.csv, rules.csv",
            ha="center", va="center", fontsize=8.3, color="#312e81", fontweight="semibold",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#eef2ff", edgecolor="#818cf8", lw=1.0), zorder=7)

    ax.add_patch(FancyBboxPatch((0.35, 0.28), 15.30, 0.46,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="#f1f5f9", edgecolor="#94a3b8", lw=1.0, zorder=3))
    ax.plot([0.65, 1.30], [0.51, 0.51], color="#0f172a", lw=2.5, zorder=5)
    draw_link_dot(ax, 0.975, 0.51, "right")
    ax.text(1.43, 0.51, "Cáp Ethernet Copper Straight-Through (1 Gbps) + Đèn Link Up",
            ha="left", va="center", fontsize=8.4, color="#0f172a", zorder=5)

    draw_arrow(ax, (6.45, 0.51), (7.13, 0.51), color="#dc2626", lw=2.3, ls=(0, (6, 3)), mscale=12, zorder=5)
    ax.text(7.25, 0.51, "Lưu lượng sinh tải (K1, K2, K3A, K3B)", ha="left", va="center", fontsize=8.4, color="#991b1b", zorder=5)

    draw_arrow(ax, (10.60, 0.51), (11.28, 0.51), color="#4f46e5", lw=2.0, ls=":", mscale=12, zorder=5)
    ax.text(11.40, 0.51, "Kênh điều phối SSH & thu thập SFTP (Port 22)", ha="left", va="center", fontsize=8.4, color="#312e81", zorder=5)

    return save_both(fig, "fig_topology.png")


# ==============================================================================
# HELPER MINI-ICONS FOR ARCHITECTURE DIAGRAM
# ==============================================================================
def draw_mini_icon(ax, cx, cy, kind="gauge", color="#0284c7"):
    """Draw compact vector icons for Kubernetes/Linux services."""
    if kind == "gauge":
        ax.add_patch(Circle((cx, cy), 0.16, facecolor="white", edgecolor=color, lw=1.6, zorder=7))
        ax.plot([cx, cx + 0.09], [cy, cy + 0.08], color="#dc2626", lw=1.8, zorder=8)
        ax.add_patch(Circle((cx, cy), 0.028, facecolor=color, zorder=8))
    elif kind == "stream":
        for off in [-0.065, 0.0, 0.065]:
            draw_arrow(ax, (cx - 0.15, cy + off), (cx + 0.15, cy + off), color=color, lw=1.3, mscale=7, zorder=7)
    elif kind == "clock":
        ax.add_patch(Circle((cx, cy), 0.15, facecolor="white", edgecolor=color, lw=1.5, zorder=7))
        ax.plot([cx, cx], [cy, cy + 0.09], color=color, lw=1.5, zorder=8)
        ax.plot([cx, cx + 0.08], [cy, cy], color=color, lw=1.5, zorder=8)
    elif kind == "k8s":
        ax.add_patch(Circle((cx, cy), 0.16, facecolor="#e0f2fe", edgecolor=color, lw=1.6, zorder=7))
        ax.add_patch(Circle((cx, cy), 0.055, facecolor=color, zorder=8))
        for ang in [0, 60, 120, 180, 240, 300]:
            rx, ry = 0.16 * math.cos(math.radians(ang)), 0.16 * math.sin(math.radians(ang))
            ax.plot([cx, cx + rx], [cy, cy + ry], color=color, lw=1.1, zorder=7)
    elif kind == "pod":
        pts = [(cx + 0.17 * math.cos(math.radians(60 * k + 30)),
                cy + 0.17 * math.sin(math.radians(60 * k + 30))) for k in range(6)]
        ax.add_patch(Polygon(pts, closed=True, facecolor="#dcfce7", edgecolor="#16a34a", lw=1.7, zorder=7))
        ax.text(cx, cy, "N", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#15803d", zorder=8)
    elif kind == "eye":
        ax.add_patch(patches.Ellipse((cx, cy), 0.34, 0.20, facecolor="#f3e8ff", edgecolor="#7c3aed", lw=1.6, zorder=7))
        ax.add_patch(Circle((cx, cy), 0.060, facecolor="#7c3aed", zorder=8))
    elif kind == "nic":
        ax.add_patch(FancyBboxPatch((cx - 0.16, cy - 0.12), 0.32, 0.24,
                                    boxstyle="round,pad=0.01,rounding_size=0.03",
                                    facecolor="#fef3c7", edgecolor="#d97706", lw=1.5, zorder=7))
        for p in [-0.085, -0.028, 0.028, 0.085]:
            ax.plot([cx + p, cx + p], [cy + 0.02, cy + 0.11], color="#b45309", lw=1.2, zorder=8)
    elif kind == "chart":
        ax.add_patch(FancyBboxPatch((cx - 0.16, cy - 0.13), 0.32, 0.26,
                                    boxstyle="round,pad=0.01,rounding_size=0.03",
                                    facecolor="#f1f5f9", edgecolor="#334155", lw=1.4, zorder=7))
        ax.add_patch(patches.Rectangle((cx - 0.10, cy - 0.09), 0.045, 0.09, facecolor="#0284c7", zorder=8))
        ax.add_patch(patches.Rectangle((cx - 0.022, cy - 0.09), 0.045, 0.17, facecolor="#e11d48", zorder=8))
        ax.add_patch(patches.Rectangle((cx + 0.055, cy - 0.09), 0.045, 0.13, facecolor="#16a34a", zorder=8))


# ==============================================================================
# DIAGRAM 2: LAYERED SYSTEM ARCHITECTURE & BORDER-TO-BORDER PACKET DATAPATH
# ==============================================================================
def make_system_architecture():
    fig, ax = plt.subplots(figsize=(18, 12.2))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12.2)
    ax.axis("off")

    # Outer Title Banner
    ax.add_patch(FancyBboxPatch((0.20, 11.45), 17.60, 0.62,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor="#0f172a", edgecolor="#020617", lw=1.2, zorder=2))
    ax.text(9.0, 11.83, "KIẾN TRÚC HỆ THỐNG PHÂN TẦNG & ĐỐI SÁNH LUỒNG ĐƯỜNG ĐI GÓI TIN (CALICO IPTABLES vs CILIUM eBPF)",
            ha="center", va="center", color="white", fontsize=13.0, fontweight="bold", zorder=3)
    ax.text(9.0, 11.57, "Tách biệt máy sinh tải ngoài cụm (worker-1) và nút K3s chạy tuần tự hai cơ chế Data Plane trên worker-2",
            ha="center", va="center", color="#94a3b8", fontsize=9.6, zorder=3)

    # ==========================================================================
    # LEFT NODE: worker-1 (x: 0.25 .. 5.15, y: 0.35 .. 11.25)
    # ==========================================================================
    ax.add_patch(FancyBboxPatch((0.25, 0.35), 4.90, 10.90,
                                boxstyle="round,pad=0.03,rounding_size=0.15",
                                facecolor="#fffaf5", edgecolor="#ea580c", lw=2.0, zorder=1))
    ax.add_patch(FancyBboxPatch((0.35, 10.65), 4.70, 0.50,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="#ea580c", edgecolor="none", zorder=2))
    ax.text(2.70, 10.90, "NODE 1: worker-1 (192.168.10.20) — Máy sinh tải",
            ha="center", va="center", color="white", fontsize=10.1, fontweight="bold", zorder=3)

    # --- worker-1 TẦNG 3 (y: 6.18 .. 10.45) ---
    ax.add_patch(FancyBboxPatch((0.45, 6.18), 4.50, 4.27,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor="white", edgecolor="#fdba74", lw=1.5, zorder=2))
    ax.text(2.70, 10.23, "TẦNG 3: ỨNG DỤNG SINH TẢI (USER SPACE)",
            ha="center", va="center", color="#9a3412", fontsize=9.1, fontweight="bold", zorder=3)

    w1_services = [
        (8.88, "wrk2 (HTTP Load Generator)", "K1: 2.000 RPS | K2: 3.000 CPS (close)\nK3A/B: 400 conn, 20.000 RPS (bão hòa)", "gauge", "#dc2626", "#fef2f2"),
        (7.62, "iperf3 Client (L4 TCP)", "4 luồng TCP song song trong 30s (-P 4)\nĐo băng thông cực đại tầng giao vận", "stream", "#0284c7", "#f0f9ff"),
        (6.36, "chrony (NTP Sync) & sshd", "Đồng bộ đồng hồ giữa worker-1 & worker-2\nNhận lệnh điều phối từ Control PC", "clock", "#4f46e5", "#eef2ff"),
    ]
    for y0, title, desc, icon, col, bg in w1_services:
        ax.add_patch(FancyBboxPatch((0.65, y0), 4.10, 1.00,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=bg, edgecolor=col, lw=1.2, zorder=3))
        draw_mini_icon(ax, 1.00, y0 + 0.50, icon, col)
        ax.text(1.32, y0 + 0.70, title, ha="left", va="center", color="#0f172a", fontsize=9.2, fontweight="bold", zorder=4)
        ax.text(1.32, y0 + 0.30, desc, ha="left", va="center", color="#334155", fontsize=8.0, zorder=4)

    # Border-to-border arrow: Tầng 3 bottom (6.16) -> Tầng 2 top (5.64)
    draw_arrow(ax, (2.70, 6.16), (2.70, 5.64), color="#ea580c", lw=2.3, mscale=14, zorder=6)
    ax.text(2.86, 5.90, "Socket Payload", ha="left", va="center", fontsize=8.0, fontweight="semibold", color="#9a3412", zorder=6)

    # --- worker-1 TẦNG 2 (y: 3.38 .. 5.62) ---
    ax.add_patch(FancyBboxPatch((0.45, 3.38), 4.50, 2.24,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor="#f8fafc", edgecolor="#64748b", lw=1.5, zorder=2))
    ax.text(2.70, 5.42, "TẦNG 2: NHÂN LINUX (KERNEL NETWORK STACK)",
            ha="center", va="center", color="#334155", fontsize=9.0, fontweight="bold", zorder=3)

    ax.add_patch(FancyBboxPatch((0.65, 4.58), 4.10, 0.58,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="#e2e8f0", edgecolor="#475569", lw=1.1, zorder=3))
    ax.text(2.70, 4.87, "Socket Buffer (AF_INET) & Chuỗi HTTP/TCP", ha="center", va="center", color="#0f172a", fontsize=8.7, fontweight="semibold", zorder=4)

    # Intra-layer arrow in clean whitespace (4.56 -> 4.19)
    draw_arrow(ax, (2.70, 4.56), (2.70, 4.19), color="#334155", lw=1.8, mscale=12, zorder=6)

    ax.add_patch(FancyBboxPatch((0.65, 3.56), 4.10, 0.60,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="#e2e8f0", edgecolor="#475569", lw=1.1, zorder=3))
    ax.text(2.70, 3.86, "TCP/IP Stack + nf_conntrack (tcp_tw_reuse=1)", ha="center", va="center", color="#0f172a", fontsize=8.7, fontweight="semibold", zorder=4)

    # Border-to-border arrow: Tầng 2 bottom (3.36) -> Tầng 1 top (2.84)
    draw_arrow(ax, (2.70, 3.36), (2.70, 2.84), color="#ea580c", lw=2.3, mscale=14, zorder=6)
    ax.text(2.86, 3.10, "Gói IPv4/TCP", ha="left", va="center", fontsize=8.0, fontweight="semibold", color="#9a3412", zorder=6)

    # --- worker-1 TẦNG 1 (y: 1.66 .. 2.82 — aligned horizontally with worker-2 TẦNG 2!) ---
    ax.add_patch(FancyBboxPatch((0.45, 1.66), 4.50, 1.16,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor="#fffbeb", edgecolor="#d97706", lw=1.5, zorder=2))
    ax.text(2.70, 2.63, "TẦNG 1: GIAO TIẾP MẠNG (NIC DRIVER)",
            ha="center", va="center", color="#92400e", fontsize=8.9, fontweight="bold", zorder=3)
    ax.add_patch(FancyBboxPatch((0.65, 1.78), 4.10, 0.66,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="white", edgecolor="#d97706", lw=1.1, zorder=3))
    draw_mini_icon(ax, 1.02, 2.11, "nic", "#d97706")
    ax.text(2.90, 2.24, "NIC eth0: 192.168.10.20 / 24", ha="center", va="center", fontsize=9.1, fontweight="bold", color="#0f172a", zorder=4)
    ax.text(2.90, 1.94, "Đóng khung Ethernet → Gửi tới :30080", ha="center", va="center", fontsize=8.1, color="#475569", zorder=4)

    # Footer note on worker-1
    ax.add_patch(FancyBboxPatch((0.45, 0.50), 4.50, 0.85,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="#fef2f2", edgecolor="#fca5a5", lw=1.0, zorder=2))
    ax.text(2.70, 0.925, "Vai trò tách biệt: Không chạy Pod/K3s trên worker-1\n→ Loại bỏ nhiễu tranh chấp CPU khi sinh tải",
            ha="center", va="center", fontsize=8.3, color="#991b1b", fontweight="semibold", zorder=3)

    # ==========================================================================
    # INTER-NODE PHYSICAL LINK (Strictly border-to-border: worker-1 T1 -> worker-2 T2)
    # ==========================================================================
    draw_arrow(ax, (4.97, 2.24), (6.53, 2.24), color="#dc2626", lw=2.8, mscale=16, zorder=8)
    ax.text(5.75, 2.72, "LAN 1 Gbps\nTCP / HTTP", ha="center", va="center", fontsize=8.3, fontweight="bold", color="#991b1b",
            bbox=dict(boxstyle="round,pad=0.22", facecolor="#fee2e2", edgecolor="#ef4444", lw=1.0), zorder=9)
    ax.text(5.75, 1.80, "NodePort\n:30080", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#0f172a", zorder=8)

    # ==========================================================================
    # RIGHT NODE: worker-2 (x: 6.35 .. 17.75, y: 0.35 .. 11.25)
    # ==========================================================================
    ax.add_patch(FancyBboxPatch((6.35, 0.35), 11.40, 10.90,
                                boxstyle="round,pad=0.03,rounding_size=0.15",
                                facecolor="#f8fafc", edgecolor="#0284c7", lw=2.0, zorder=1))
    ax.add_patch(FancyBboxPatch((6.45, 10.65), 11.20, 0.50,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="#0284c7", edgecolor="none", zorder=2))
    ax.text(12.05, 10.90, "NODE 2: worker-2 (192.168.10.30) — K3s Single-Node SUT (4 vCPU | 4 GB RAM | Kernel >= 5.15)",
            ha="center", va="center", color="white", fontsize=10.2, fontweight="bold", zorder=3)

    # --- TẦNG 4A: CONTROL PLANE LAYER (y: 9.42 .. 10.46) ---
    ax.add_patch(FancyBboxPatch((6.55, 9.42), 11.00, 1.04,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor="#eef2ff", edgecolor="#6366f1", lw=1.5, zorder=2))
    ax.text(12.05, 10.29, "TẦNG 4A: CONTROL PLANE & TỰ ĐỘNG HÓA RULE (USER SPACE)",
            ha="center", va="center", color="#312e81", fontsize=8.9, fontweight="bold", zorder=3)

    ax.add_patch(FancyBboxPatch((6.70, 9.52), 2.38, 0.58,
                                boxstyle="round,pad=0.02,rounding_size=0.07",
                                facecolor="#ffe4e6", edgecolor="#e11d48", lw=1.2, zorder=3))
    ax.text(7.89, 9.90, "kube-proxy (iptables)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#9f1239", zorder=4)
    ax.text(7.89, 9.64, "iptables-restore (xtables.lock)", ha="center", va="center", fontsize=7.5, color="#881337", zorder=4)

    ax.add_patch(FancyBboxPatch((9.44, 9.52), 4.92, 0.58,
                                boxstyle="round,pad=0.02,rounding_size=0.07",
                                facecolor="white", edgecolor="#4f46e5", lw=1.2, zorder=3))
    draw_mini_icon(ax, 9.72, 9.81, "k8s", "#4f46e5")
    ax.text(12.14, 9.91, "K3s Control Plane (apiserver, etcd) + generate_rules.sh",
            ha="center", va="center", fontsize=8.4, fontweight="bold", color="#1e1b4b", zorder=4)
    ax.text(12.14, 9.65, "Sinh 50 → 500 → 1.000 → 1.500 Services (Batch=50, nghỉ 4s, ổn định 60s)",
            ha="center", va="center", fontsize=7.4, color="#4338ca", zorder=4)

    ax.add_patch(FancyBboxPatch((14.72, 9.52), 2.68, 0.58,
                                boxstyle="round,pad=0.02,rounding_size=0.07",
                                facecolor="#e0f2fe", edgecolor="#0284c7", lw=1.2, zorder=3))
    ax.text(16.06, 9.90, "cilium-agent (eBPF Loader)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#075985", zorder=4)
    ax.text(16.06, 9.64, "syscall bpf() → Cập nhật nguyên tử O(1)", ha="center", va="center", fontsize=7.4, color="#0c4a6e", zorder=4)

    draw_arrow(ax, (9.42, 9.81), (9.10, 9.81), color="#e11d48", lw=1.8, mscale=11, zorder=5)
    draw_arrow(ax, (14.38, 9.81), (14.70, 9.81), color="#0284c7", lw=1.8, mscale=11, zorder=5)

    # --- TẦNG 4B: POD NAMESPACE LAYER (y: 7.78 .. 9.10, x: 7.15 .. 17.05) ---
    ax.add_patch(FancyBboxPatch((7.15, 7.78), 9.90, 1.32,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor="#f0fdf4", edgecolor="#16a34a", lw=1.5, zorder=2))
    ax.text(12.10, 8.93, "TẦNG 4B: KHÔNG GIAN ỨNG DỤNG POD & GIÁM SÁT (POD / USER SPACE)",
            ha="center", va="center", color="#166534", fontsize=8.9, fontweight="bold", zorder=3)

    ax.add_patch(FancyBboxPatch((7.35, 7.88), 6.25, 0.88,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="white", edgecolor="#15803d", lw=1.5, zorder=3))
    draw_mini_icon(ax, 7.75, 8.43, "pod", "#16a34a")
    ax.text(10.65, 8.56, "Pod: target-server (nginx:alpine — Port 80)",
            ha="center", va="center", fontsize=9.4, fontweight="bold", color="#14532d", zorder=4)
    ax.text(10.65, 8.30, "CPU Limit: 2000m  |  RAM Limit: 512Mi  |  Replicas: 1",
            ha="center", va="center", fontsize=8.0, color="#334155", zorder=4)
    ax.add_patch(FancyBboxPatch((7.85, 7.88), 5.25, 0.25,
                                boxstyle="round,pad=0.01,rounding_size=0.04",
                                facecolor="#bbf7d0", edgecolor="#16a34a", lw=1.0, zorder=4))
    ax.text(10.475, 8.005, "Giao diện veth-pod (eth0 trong Network Namespace của Pod)",
            ha="center", va="center", fontsize=7.9, fontweight="bold", color="#14532d", zorder=5)

    ax.add_patch(FancyBboxPatch((13.95, 7.88), 2.95, 0.88,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="#faf5ff", edgecolor="#7c3aed", lw=1.5, zorder=3))
    draw_mini_icon(ax, 14.30, 8.36, "eye", "#7c3aed")
    ax.text(15.65, 8.52, "Pod: Cilium Hubble Relay", ha="center", va="center", fontsize=8.9, fontweight="bold", color="#5b21b6", zorder=4)
    ax.text(15.65, 8.20, "Kịch bản 3B: Thu thập luồng\nL3/L4 thời gian thực (+4.3% CPU)",
            ha="center", va="center", fontsize=7.6, color="#6d28d9", zorder=4)

    # --- TẦNG 3: LINUX KERNEL DATA PLANE (y: 3.38 .. 7.20, x: 7.15 .. 17.05) ---
    ax.add_patch(FancyBboxPatch((7.15, 3.38), 9.90, 3.82,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor="white", edgecolor="#334155", lw=1.5, zorder=2))
    ax.text(12.10, 7.01, "TẦNG 3: TẦNG DỮ LIỆU NHÂN LINUX (KERNEL DATA PLANE — ĐỐI CHỨNG TUẦN TỰ)",
            ha="center", va="center", color="#0f172a", fontsize=9.0, fontweight="bold", zorder=3)

    # ---- PATH A: CALICO + IPTABLES (x: 7.30 .. 11.75, y: 3.50 .. 6.78) ----
    ax.add_patch(FancyBboxPatch((7.30, 3.50), 4.45, 3.28,
                                boxstyle="round,pad=0.02,rounding_size=0.09",
                                facecolor="#fff1f2", edgecolor="#e11d48", lw=1.6, zorder=3))
    ax.text(9.525, 6.60, "LUỒNG A: Calico VXLAN + iptables",
            ha="center", va="center", fontsize=8.9, fontweight="bold", color="#9f1239", zorder=4)

    steps_a = [
        (3.60, "[A1] Netfilter PREROUTING Hook\n(Gói tin qua chuỗi lọc tầng IP Host)", "#ffe4e6", 0.54),
        (4.36, "[A2] Duyệt tuần tự KUBE-SERVICES / NODEPORTS\nĐộ phức tạp O(N) | Khóa xtables.lock", "#fecdd3", 0.56),
        (5.14, "[A3] DNAT (:30080 → PodIP:80) + nf_conntrack", "#ffe4e6", 0.42),
        (5.78, "[A4] Linux Routing → veth-host → veth-pod\n(Phát sinh SoftIRQ NET_RX lần 2)", "#fecdd3", 0.56),
    ]
    for yb, txt, bg, bh in steps_a:
        ax.add_patch(FancyBboxPatch((7.48, yb), 4.09, bh,
                                    boxstyle="round,pad=0.02,rounding_size=0.06",
                                    facecolor=bg, edgecolor="#e11d48", lw=1.0, zorder=4))
        ax.text(9.525, yb + bh / 2, txt, ha="center", va="center", fontsize=7.9, fontweight="semibold", color="#881337", zorder=5)

    for y_start, y_end in [(4.15, 4.35), (4.93, 5.13), (5.57, 5.77)]:
        draw_arrow(ax, (9.525, y_start), (9.525, y_end), color="#be123c", lw=1.8, mscale=10, zorder=6)

    # ---- PATH B: CILIUM eBPF (x: 12.10 .. 16.90, y: 3.50 .. 6.78) ----
    ax.add_patch(FancyBboxPatch((12.10, 3.50), 4.80, 3.28,
                                boxstyle="round,pad=0.02,rounding_size=0.09",
                                facecolor="#f0f9ff", edgecolor="#0284c7", lw=1.6, zorder=3))
    ax.text(14.50, 6.60, "LUỒNG B: Cilium eBPF + hostRouting",
            ha="center", va="center", fontsize=8.9, fontweight="bold", color="#075985", zorder=4)

    ax.add_patch(FancyBboxPatch((12.28, 3.60), 4.44, 0.56,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                facecolor="#e0f2fe", edgecolor="#0284c7", lw=1.1, zorder=4))
    ax.text(14.50, 3.88, "[B1] TC Ingress eBPF Hook\n(Bắt gói tin sớm tại eth0 trước toàn bộ Netfilter)",
            ha="center", va="center", fontsize=7.9, fontweight="semibold", color="#0c4a6e", zorder=5)

    ax.add_patch(FancyBboxPatch((12.28, 4.44), 4.44, 0.72,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                facecolor="#bae6fd", edgecolor="#0284c7", lw=1.2, zorder=4))
    ax.text(14.50, 4.80, "[B2] Tra cứu bảng băm BPF Maps (cilium_lb4_services_v2)\nĐộ phức tạp O(1) | eBPF DNAT | Không dùng xtables.lock",
            ha="center", va="center", fontsize=7.9, fontweight="bold", color="#0c4a6e", zorder=5)

    ax.add_patch(FancyBboxPatch((12.28, 5.48), 2.36, 0.88,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                facecolor="#dcfce7", edgecolor="#0284c7", lw=1.2, zorder=4))
    ax.text(13.46, 5.92, "[B3] bpf_redirect_peer()\nTắt qua (Bypass) Netfilter\n& Host IP Stack",
            ha="center", va="center", fontsize=7.8, fontweight="bold", color="#065f46", zorder=5)

    ax.add_patch(FancyBboxPatch((14.80, 5.48), 1.92, 0.88,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                facecolor="#f3e8ff", edgecolor="#7c3aed", lw=1.2, zorder=4))
    ax.text(15.76, 5.92, "eBPF Ring Buffer\nĐẩy sự kiện L3/L4\n(Bất đồng bộ, lockless)",
            ha="center", va="center", fontsize=7.7, fontweight="bold", color="#5b21b6", zorder=5)

    # Clean spacious intra-layer arrows Path B (0.28 - 0.32 gaps!)
    draw_arrow(ax, (14.50, 4.17), (14.50, 4.43), color="#0369a1", lw=1.8, mscale=10, zorder=6)
    draw_arrow(ax, (13.80, 5.17), (13.46, 5.47), color="#0284c7", lw=1.8, mscale=10, zorder=6)
    draw_arrow(ax, (15.22, 5.17), (15.76, 5.47), color="#7c3aed", lw=1.7, mscale=10, zorder=6)

    # ---- STRICT BORDER-TO-BORDER ARROWS: TẦNG 3 top (7.20) -> TẦNG 4B bottom (7.78) ----
    # A5: Calico -> target-server Pod
    draw_arrow(ax, (9.525, 7.21), (9.525, 7.77), color="#e11d48", lw=2.4, mscale=15, zorder=7)
    ax.text(9.68, 7.49, "A5: veth-host → veth-pod", ha="left", va="center", fontsize=8.0, fontweight="bold", color="#9f1239", zorder=8)

    # B4: Cilium bpf_redirect_peer -> target-server Pod
    draw_arrow(ax, (12.90, 7.21), (12.90, 7.77), color="#0284c7", lw=2.4, mscale=15, zorder=7)
    ax.text(13.06, 7.49, "B4: Redirect Bypass", ha="left", va="center", fontsize=8.0, fontweight="bold", color="#075985", zorder=8)

    # B5: eBPF Ring Buffer -> Cilium Hubble Relay
    draw_arrow(ax, (15.76, 7.21), (15.76, 7.77), color="#7c3aed", lw=2.1, ls="--", mscale=14, zorder=7)
    ax.text(15.92, 7.49, "B5: RingBuf Stream", ha="left", va="center", fontsize=8.0, fontweight="bold", color="#5b21b6", zorder=8)

    # ---- Control Plane Border-to-Border Side Channels (TẦNG 4A bottom 9.42 -> TẦNG 3 outer side border 7.15/17.05) ----
    ax.plot([6.80, 6.80], [9.41, 4.65], color="#e11d48", lw=1.7, linestyle="--", zorder=5)
    draw_arrow(ax, (6.80, 4.65), (7.14, 4.65), color="#e11d48", lw=1.8, ls="--", mscale=12, zorder=6)
    ax.text(6.62, 6.95, "Nạp bảng rule O(N)", rotation=90, ha="center", va="center", fontsize=8.0, fontweight="bold", color="#be123c", zorder=6)

    ax.plot([17.36, 17.36], [9.41, 4.80], color="#0284c7", lw=1.7, linestyle="--", zorder=5)
    draw_arrow(ax, (17.36, 4.80), (17.06, 4.80), color="#0284c7", lw=1.8, ls="--", mscale=12, zorder=6)
    ax.text(17.54, 6.95, "Cập nhật BPF Map O(1)", rotation=90, ha="center", va="center", fontsize=8.0, fontweight="bold", color="#0369a1", zorder=6)

    # --- TẦNG 2: NIC DRIVER & INTERRUPT LAYER (y: 1.66 .. 2.82, x: 6.55 .. 17.55) ---
    ax.add_patch(FancyBboxPatch((6.55, 1.66), 11.00, 1.16,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor="#fffbeb", edgecolor="#d97706", lw=1.5, zorder=2))
    ax.text(12.05, 2.64, "TẦNG 2: GIAO DIỆN MẠNG (NIC), DMA & NGẮT MỀM (INTERRUPT LAYER)",
            ha="center", va="center", color="#92400e", fontsize=8.9, fontweight="bold", zorder=3)

    ax.add_patch(FancyBboxPatch((6.70, 1.77), 2.82, 0.70,
                                boxstyle="round,pad=0.02,rounding_size=0.07",
                                facecolor="white", edgecolor="#d97706", lw=1.2, zorder=3))
    draw_mini_icon(ax, 7.02, 2.12, "nic", "#d97706")
    ax.text(8.34, 2.25, "eth0: 192.168.10.30", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#0f172a", zorder=4)
    ax.text(8.34, 1.95, "Tiếp nhận NodePort :30080", ha="center", va="center", fontsize=7.8, color="#475569", zorder=4)

    ax.add_patch(FancyBboxPatch((9.88, 1.77), 2.74, 0.70,
                                boxstyle="round,pad=0.02,rounding_size=0.07",
                                facecolor="white", edgecolor="#f59e0b", lw=1.2, zorder=3))
    ax.text(11.25, 2.24, "DMA Ring Buffer (NIC)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a", zorder=4)
    ax.text(11.25, 1.95, "Cấp phát sk_buff nhân Linux", ha="center", va="center", fontsize=7.7, color="#475569", zorder=4)

    ax.add_patch(FancyBboxPatch((12.98, 1.77), 4.42, 0.70,
                                boxstyle="round,pad=0.02,rounding_size=0.07",
                                facecolor="#fef3c7", edgecolor="#d97706", lw=1.2, zorder=3))
    ax.text(15.19, 2.24, "HardIRQ → SoftIRQ NET_RX (ksoftirqd)", ha="center", va="center", fontsize=8.7, fontweight="bold", color="#92400e", zorder=4)
    ax.text(15.19, 1.95, "Calico: 4.134 ngắt/s  |  Cilium giảm -37.5% (2.582 ngắt/s)", ha="center", va="center", fontsize=7.7, color="#78350f", zorder=4)

    draw_arrow(ax, (9.53, 2.12), (9.87, 2.12), color="#d97706", lw=1.8, mscale=11, zorder=5)
    draw_arrow(ax, (12.63, 2.12), (12.97, 2.12), color="#d97706", lw=1.8, mscale=11, zorder=5)

    # ---- STRICT BORDER-TO-BORDER ARROWS: TẦNG 2 top (2.82) -> TẦNG 3 bottom (3.38) ----
    draw_arrow(ax, (9.525, 2.83), (9.525, 3.37), color="#e11d48", lw=2.3, mscale=14, zorder=7)
    ax.text(9.68, 3.10, "A0: Vào Netfilter", ha="left", va="center", fontsize=8.0, fontweight="bold", color="#9f1239", zorder=8)

    draw_arrow(ax, (14.50, 2.83), (14.50, 3.37), color="#0284c7", lw=2.3, mscale=14, zorder=7)
    ax.text(14.66, 3.10, "B0: Vào TC eBPF Hook", ha="left", va="center", fontsize=8.0, fontweight="bold", color="#075985", zorder=8)

    # --- TẦNG 1: TELEMETRY LAYER (y: 0.46 .. 1.32, x: 6.55 .. 17.55) ---
    ax.add_patch(FancyBboxPatch((6.55, 0.46), 11.00, 0.86,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor="#f1f5f9", edgecolor="#475569", lw=1.4, zorder=2))
    ax.text(12.05, 1.17, "TẦNG 1: THU THẬP CHỈ SỐ TÀI NGUYÊN HỆ THỐNG (TELEMETRY — 1 MẪU/GIÂY)",
            ha="center", va="center", color="#1e293b", fontsize=8.7, fontweight="bold", zorder=3)

    ax.add_patch(FancyBboxPatch((6.70, 0.54), 2.75, 0.48,
                                boxstyle="round,pad=0.02,rounding_size=0.07",
                                facecolor="white", edgecolor="#334155", lw=1.1, zorder=3))
    draw_mini_icon(ax, 7.02, 0.78, "chart", "#334155")
    ax.text(8.30, 0.78, "collect_metrics.sh (1s)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a", zorder=4)

    for px, lbl in [
        (9.65, "CPU Busy %\n(/proc/stat)"),
        (11.65, "SoftIRQ NET_RX/s\n(/proc/softirqs)"),
        (13.65, "RAM Used MB\n(free -m)"),
        (15.65, "metrics.csv\n& rules.csv"),
    ]:
        ax.add_patch(FancyBboxPatch((px, 0.54), 1.80, 0.48,
                                    boxstyle="round,pad=0.02,rounding_size=0.07",
                                    facecolor="white", edgecolor="#64748b", lw=1.0, zorder=3))
        ax.text(px + 0.90, 0.78, lbl, ha="center", va="center", fontsize=7.9, fontweight="semibold", color="#0f172a", zorder=4)

    # STRICT BORDER-TO-BORDER telemetry arrow: TẦNG 2 bottom (1.66) -> TẦNG 1 top (1.33)
    draw_arrow(ax, (14.50, 1.65), (14.50, 1.33), color="#475569", lw=1.6, ls=":", mscale=11, zorder=6)
    ax.text(14.66, 1.49, "Đọc /proc/* mỗi 1 giây", ha="left", va="center", fontsize=7.8, fontweight="semibold", color="#334155", zorder=6)

    return save_both(fig, "fig_system_architecture.png")


if __name__ == "__main__":
    p1 = make_topology()
    p2 = make_system_architecture()
    print("[OK] Generated topology:", p1)
    print("[OK] Generated architecture:", p2)
