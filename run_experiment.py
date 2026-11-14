"""Dieu phoi thuc nghiem tu may Windows: chay kich ban 1/2/3A tren worker-1 (sinh tai) va worker-2 (k3s),
roi keo toan bo log / CSV ve may nay va ve bieu do.
Dung:  set W1_PASS=<mat khau worker-1>;  python run_experiment.py <nhan: calico|cilium> [--skip-k3]
Ket qua: ../results/<nhan>_<thoigian>/
"""
import os, sys, time, shlex, subprocess, posixpath
import paramiko

LABEL = sys.argv[1] if len(sys.argv) > 1 else "calico"
SCALES = [50, 500, 1000, 1500]
SETTLE = 60
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "scripts")
RES = os.path.join(HERE, "results", f"{LABEL}_{time.strftime('%Y%m%d_%H%M%S')}")
os.makedirs(RES, exist_ok=True)
REMOTE = "/tmp/ebpf"

def connect(host, port, user, password=None):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, port=port, username=user, password=password, timeout=15,
              look_for_keys=password is None, allow_agent=password is None)
    c.get_transport().set_keepalive(20)
    return c

def get_w1(): return connect("192.168.10.20", 22, "quan", os.environ["W1_PASS"])
def get_w2():
    try: return connect("127.0.0.1", 2222, "k8s-worker-2")
    except Exception: return connect("192.168.10.30", 22, "k8s-worker-2")

w1 = get_w1()
w2 = get_w2()
PASS = {"w1": os.environ["W1_PASS"], "w2": None}

def run(c, cmd, name, check=True):
    global w1, w2
    pre = f"echo {shlex.quote(PASS[name])} | sudo -S -p '' " if PASS[name] else "sudo -n "
    for attempt in (1, 2):
        try:
            _, o, e = c.exec_command(pre + "bash -c " + shlex.quote(cmd))
            out = o.read().decode(errors="replace"); err = e.read().decode(errors="replace")
            rc = o.channel.recv_exit_status()
            if check and rc != 0:
                print(f"[LOI {name}] {cmd}\n{out}\n{err}"); sys.exit(1)
            return out.strip()
        except Exception as ex:
            if attempt == 2: raise
            print(f"[RECONNECT {name}] {ex}", flush=True)
            c = get_w1() if name == "w1" else get_w2()
            if name == "w1": w1 = c
            else: w2 = c

def put(c, name):
    run(c, f"mkdir -p {REMOTE} && chmod 777 {REMOTE}", "w1" if c is w1 else "w2")
    s = c.open_sftp()
    for f in ("run_benchmark.sh", "generate_rules.sh", "collect_metrics.sh"):
        data = open(os.path.join(SCRIPTS, f), "rb").read().replace(b"\r\n", b"\n")
        with s.open(f"{REMOTE}/{f}", "wb") as fh: fh.write(data)
    s.close()

def log(m): print(time.strftime("%H:%M:%S"), m, flush=True)
def now2(): return int(run(w2, "date +%s", "w2"))

put(w1, "w1"); put(w2, "w2")
run(w2, "DEBIAN_FRONTEND=noninteractive apt-get install -y iperf3 >/dev/null 2>&1; pkill iperf3; iperf3 -s -D; sleep 1; pgrep iperf3", "w2")
run(w2, f"rm -f {REMOTE}/metrics.csv {REMOTE}/rules.csv; nohup bash {REMOTE}/collect_metrics.sh {REMOTE}/metrics.csv >/dev/null 2>&1 &", "w2")
run(w2, f"export KUBECONFIG=/etc/rancher/k3s/k3s.yaml; kubectl get nodes; bash {REMOTE}/generate_rules.sh --clean", "w2")
run(w1, f"rm -rf {REMOTE}/out; mkdir -p {REMOTE}/out", "w1")

def pull_results():
    run(w1, f"chmod -R a+r {REMOTE}/out", "w1", check=False)
    run(w2, f"chmod a+r {REMOTE}/*.csv", "w2", check=False)
    pull_dir(w1, f"{REMOTE}/out", os.path.join(RES, "worker1_out"))
    s = w2.open_sftp()
    for f in ("metrics.csv", "rules.csv"):
        try: s.get(f"{REMOTE}/{f}", os.path.join(RES, f))
        except IOError: pass
    s.close()
    with open(os.path.join(RES, "phases.csv"), "w") as fh:
        fh.write("phase,start,end\n")
        for p in phases: fh.write("%s,%d,%d\n" % p)

def pull_dir(c, rdir, ldir):
    s = c.open_sftp(); os.makedirs(ldir, exist_ok=True)
    def rec(r, l):
        for a in s.listdir_attr(r):
            rp, lp = posixpath.join(r, a.filename), os.path.join(l, a.filename)
            if a.st_mode & 0o040000: os.makedirs(lp, exist_ok=True); rec(rp, lp)
            else: s.get(rp, lp)
    rec(rdir, ldir); s.close()

phases = []
def phase(name, fn):
    t0 = now2(); log(f"== {name}"); fn(); t1 = now2(); phases.append((name, t0, t1)); pull_results()

phase("k1", lambda: print(run(w1, f"bash {REMOTE}/run_benchmark.sh {REMOTE}/out/k1 k1", "w1")))
for n in SCALES:
    def step(n=n):
        print(run(w2, f"bash {REMOTE}/generate_rules.sh --clean >/dev/null; bash {REMOTE}/generate_rules.sh --scale {n} --out {REMOTE}/rules.csv", "w2"))
        log(f"on dinh {SETTLE}s"); time.sleep(SETTLE)
        print(run(w1, f"bash {REMOTE}/run_benchmark.sh {REMOTE}/out/k2_{n} k2_cps 60", "w1"))
    phase(f"k2_{n}", step)
run(w2, f"bash {REMOTE}/generate_rules.sh --clean >/dev/null", "w2")
if "--skip-k3" not in sys.argv:
    phase("k3", lambda: print(run(w1, f"bash {REMOTE}/run_benchmark.sh {REMOTE}/out/k3 k3_saturation", "w1")))
run(w2, "pkill -f collect_metrics.sh; pkill iperf3; true", "w2", check=False)

pull_results()
log(f"Da luu log vao {RES}")
subprocess.call([sys.executable, os.path.join(HERE, "plot.py"), RES])
