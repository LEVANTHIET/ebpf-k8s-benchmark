#!/bin/bash
# Chay tren worker-2 (node k3s): ghi CSV moi 1 giay gom CPU busy %, SoftIRQ NET_RX/giay, RAM da dung (MB).
# Dung: ./collect_metrics.sh metrics.csv   (dung bang kill)
OUT=${1:-metrics.csv}
echo "ts,cpu_busy_pct,softirq_net_rx_per_s,mem_used_mb" > "$OUT"
pt=0; pi=0; prx=0
while true; do
  read -r _ u n s i io irq sirq st _ < /proc/stat
  total=$((u+n+s+i+io+irq+sirq+st)); idle=$((i+io))
  rx=$(awk '/NET_RX/{t=0;for(k=2;k<=NF;k++)t+=$k;print t}' /proc/softirqs)
  mem=$(free -m | awk '/Mem:/{print $3}')
  if [ "$pt" -ne 0 ]; then
    dt=$((total-pt)); di=$((idle-pi))
    [ "$dt" -gt 0 ] && echo "$(date +%s),$(( 100*(dt-di)/dt )),$((rx-prx)),$mem" >> "$OUT"
  fi
  pt=$total; pi=$idle; prx=$rx
  sleep 1
done
