# Tong hop ket qua thuc nghiem (Mean +/- Std, n=3)

## CALICO (n=3 lan do)
- K1 iperf3: 94.08 +/- 0.23 Mbps
- K1 wrk2 p50/p99/p99.9: 3.74 / 57.43 / 168.62 ms
- K2 50 rules: RPS=2917.7+/-12.3, p99=84.6ms, program_s=0.35s
- K2 500 rules: RPS=2685.2+/-16.3, p99=246.4ms, program_s=1.85s
- K2 1000 rules: RPS=2375.4+/-16.9, p99=584.3ms, program_s=4.35s
- K2 1500 rules: RPS=2034.3+/-21.1, p99=1146.7ms, program_s=7.86s
- K3A (Hubble OFF): RPS=7301.3, CPU=85.5%, SoftIRQ_RX=4134/s, RAM=1345MB

## CILIUM (n=3 lan do)
- K1 iperf3: 96.99 +/- 0.15 Mbps
- K1 wrk2 p50/p99/p99.9: 3.51 / 27.23 / 66.89 ms
- K2 50 rules: RPS=2984.2+/-3.4, p99=41.4ms, program_s=0.05s
- K2 500 rules: RPS=2975.1+/-3.9, p99=43.1ms, program_s=0.12s
- K2 1000 rules: RPS=2964.5+/-4.3, p99=45.3ms, program_s=0.21s
- K2 1500 rules: RPS=2952.0+/-4.5, p99=47.6ms, program_s=0.31s
- K3A (Hubble OFF): RPS=9642.3, CPU=66.9%, SoftIRQ_RX=2582/s, RAM=1410MB
- K3B (Hubble ON): RPS=9438.2, CPU=71.2%, SoftIRQ_RX=2633/s, RAM=1505MB

