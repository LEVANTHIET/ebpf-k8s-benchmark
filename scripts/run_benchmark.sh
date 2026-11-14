#!/bin/bash
# ==============================================================================
# Chay tren worker-1 (may sinh tai, NGOAI cluster) -> goi vao NodePort cua worker-2.
# Dung: ./run_benchmark.sh <OUTPUT_DIR> <k1|k2_cps|k3_saturation|all> [DURATION_K2]
# Bien moi truong: TARGET_IP (mac dinh 192.168.10.30), NODEPORT (30080)
# ==============================================================================
OUTPUT_DIR=${1:?thieu OUTPUT_DIR}
SCENARIO=${2:-k1}
DUR=${3:-60}
TARGET_IP=${TARGET_IP:-192.168.10.30}
NODEPORT=${NODEPORT:-30080}
TARGET_URL="http://$TARGET_IP:$NODEPORT/"
mkdir -p "$OUTPUT_DIR"

run_k1() {
  echo "-> K1.1 iperf3 TCP 30s, 4 luong"
  iperf3 -c "$TARGET_IP" -t 30 -P 4 --json > "$OUTPUT_DIR/k1_iperf3.json" 2>&1 || echo "WARN: iperf3 that bai"
  echo "-> K1.2 wrk2 latency 2000 RPS, 60s"
  wrk2 -t2 -c100 -d60s -R2000 --latency "$TARGET_URL" > "$OUTPUT_DIR/k1_wrk2_latency.txt" 2>&1
}
run_k2_cps() {
  echo "-> K2 wrk2 Connection: close 3000 RPS, ${DUR}s"
  wrk2 -t2 -c100 -d${DUR}s -R3000 -H "Connection: close" --latency "$TARGET_URL" > "$OUTPUT_DIR/k2_cps.txt" 2>&1
}
run_k3() {
  echo "-> K3 bao hoa 400 ket noi, 20000 RPS, 120s"
  wrk2 -t2 -c400 -d120s -R20000 --latency "$TARGET_URL" > "$OUTPUT_DIR/k3_saturation.txt" 2>&1
}
case "$SCENARIO" in
  k1) run_k1;;
  k2_cps) run_k2_cps;;
  k3_saturation) run_k3;;
  all) run_k1; sleep 5; run_k2_cps; sleep 5; run_k3;;
  *) echo "Kich ban khong hop le"; exit 1;;
esac
echo "DONE -> $OUTPUT_DIR"
