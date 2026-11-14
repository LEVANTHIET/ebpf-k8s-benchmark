"""Chay mot lenh bat ky, luu toan bo log ra file terminal.log va quay video terminal (.mp4) theo thoi gian thuc.
Dung: python record_run.py <output_dir> <command...>
Vi du: python record_run.py results/run2_cilium python -u run_experiment.py cilium
"""
import os, sys, time, subprocess, threading, queue
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

OUT_DIR = sys.argv[1]
CMD = sys.argv[2:]
os.makedirs(OUT_DIR, exist_ok=True)
LOG_PATH = os.path.join(OUT_DIR, "terminal.log")
MP4_PATH = os.path.join(OUT_DIR, "terminal_recording.mp4")

W, H = 1280, 720
FPS = 4
FONT_SIZE = 16
LINE_H = 22
MAX_LINES = (H - 52) // LINE_H

def get_font():
    for p in (r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\lucon.ttf", r"C:\Windows\Fonts\cour.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, FONT_SIZE)
    return ImageFont.load_default()

FONT = get_font()
lines = [f"$ {' '.join(CMD)}", "-" * 90]
q = queue.Queue()
done_evt = threading.Event()

def reader(proc):
    with open(LOG_PATH, "w", encoding="utf-8", errors="replace") as lf:
        lf.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] CMD: {' '.join(CMD)}\n")
        for raw in iter(proc.stdout.readline, b""):
            txt = raw.decode("utf-8", errors="replace").rstrip("\r\n")
            lf.write(txt + "\n"); lf.flush()
            q.put(txt)
    done_evt.set()

def render_frame():
    img = Image.new("RGB", (W, H), (18, 20, 26))
    d = ImageDraw.Draw(img)
    # Header bar
    d.rectangle([0, 0, W, 34], fill=(32, 36, 46))
    d.text((14, 8), f"eBPF K3s Benchmark Terminal  |  {time.strftime('%Y-%m-%d %H:%M:%S')}  |  {' '.join(CMD)}", fill=(130, 210, 255), font=FONT)
    y = 42
    for ln in lines[-MAX_LINES:]:
        color = (220, 228, 238)
        if "==" in ln or "DONE" in ln or "[OK]" in ln: color = (120, 235, 150)
        elif "WARN" in ln or "LOI" in ln or "ERROR" in ln: color = (255, 130, 120)
        elif ln.startswith("->") or ln.startswith("  ->"): color = (255, 215, 120)
        d.text((14, y), ln[:145], fill=color, font=FONT)
        y += LINE_H
    return img.tobytes()

proc = subprocess.Popen(CMD, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
t = threading.Thread(target=reader, args=(proc,), daemon=True)
t.start()

writer = imageio_ffmpeg.write_frames(MP4_PATH, (W, H), fps=FPS, codec="libx264", pix_fmt_in="rgb24")
writer.send(None)

try:
    while not done_evt.is_set() or not q.empty():
        while not q.empty():
            txt = q.get_nowait()
            # Wrap long lines
            while len(txt) > 140:
                lines.append(txt[:140]); txt = "  " + txt[140:]
            lines.append(txt)
        writer.send(render_frame())
        time.sleep(1.0 / FPS)
    # Hold final frame for 2 seconds
    for _ in range(FPS * 2):
        writer.send(render_frame())
finally:
    writer.close()

rc = proc.wait()
print(f"[record_run] Exit={rc} | Log={LOG_PATH} | Video={MP4_PATH}")
sys.exit(rc)
