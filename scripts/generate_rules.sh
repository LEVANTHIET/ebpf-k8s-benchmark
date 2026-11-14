#!/bin/bash
# ==============================================================================
# Chay tren worker-2 (k3s). Sinh dummy Services theo lo (batch) va do thoi gian:
#   - create_s : thoi gian gui lenh tao toan bo Services
#   - program_s: thoi gian tu luc tao xong den khi so rule trong iptables du (rule programming).
#                Voi Cilium (khong kube-proxy) khong do duoc bang iptables -> ghi -1.
# Dung: ./generate_rules.sh --scale N [--out file.csv] | --clean
# Moc de xuat: 50 -> 500 -> 1000 -> 1500
# ==============================================================================
export KUBECONFIG=${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}
NAMESPACE="benchmark-rules"
BATCH_SIZE=50
DELAY_BETWEEN_BATCH=4

if [ "$1" == "--clean" ]; then
  kubectl -n "$NAMESPACE" delete svc --all --force --grace-period=0 >/dev/null 2>&1 || true
  kubectl delete namespace "$NAMESPACE" --ignore-not-found=true --wait=true
  echo "[OK] Da don dep dummy rules"; exit 0
fi
[ "$1" == "--scale" ] && [ -n "$2" ] || { echo "Dung: $0 --scale N [--out file.csv] | --clean"; exit 1; }
TOTAL=$2
OUT=""; [ "$3" == "--out" ] && OUT="$4"

kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || kubectl create namespace "$NAMESPACE"
T0=$(date +%s.%N)
i=1
while [ "$i" -le "$TOTAL" ]; do
  END=$((i+BATCH_SIZE-1)); [ "$END" -gt "$TOTAL" ] && END=$TOTAL
  {
    for ((j=i; j<=END; j++)); do
cat <<EOF
apiVersion: v1
kind: Service
metadata:
  name: dummy-svc-$j
  namespace: $NAMESPACE
spec:
  ports:
  - port: $((8000 + (j % 1000)))
    targetPort: 80
  selector:
    app: dummy-$j
---
EOF
    done
  } | kubectl create -f - >/dev/null
  echo "  -> $END / $TOTAL services"
  i=$((END+1))
  [ "$END" -lt "$TOTAL" ] && sleep $DELAY_BETWEEN_BATCH
done
T1=$(date +%s.%N)

PROG=-1
if iptables-save 2>/dev/null | grep -q 'KUBE-SERVICES'; then
  for _ in $(seq 1 600); do
    C=$(iptables-save 2>/dev/null | grep -c "benchmark-rules/dummy-svc")
    [ "$C" -ge "$TOTAL" ] && break
    sleep 1
  done
  T2=$(date +%s.%N)
  PROG=$(awk "BEGIN{print $T2 - $T1}")
fi
CREATE=$(awk "BEGIN{print $T1 - $T0}")
printf "scale=%s create_s=%.1f program_s=%.1f\n" "$TOTAL" "$CREATE" "$PROG"
[ -n "$OUT" ] && printf "%s,%.1f,%.1f\n" "$TOTAL" "$CREATE" "$PROG" >> "$OUT"
exit 0
