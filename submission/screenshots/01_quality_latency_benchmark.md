# Evidence 01 — Quality & Latency Benchmark Results

## 1. Quality — Precision@10 on 50 Golden Queries

```
Day 19 benchmark — keyword vs semantic vs hybrid
==============================================================
  Loaded 50 golden queries
  Indexed 1000 docs in 75.9s

Quality — Precision@10 (% of top-10 in matching topic)
  Keyword (BM25)   :  77.8%
  Semantic (vector):  73.2%
  Hybrid  (RRF=60) :  78.6%   <- PASS (Hybrid beats both pure modes)

Quality by query type:
  type           n       kw     sem     hyb
  exact         15   96.7%  88.7%  96.7%
  paraphrase    15   33.3%  24.0%  32.0%
  mixed         20   97.0%  98.5% 100.0%
```

## 2. Latency — P50 / P95 / P99 over 5000 calls per mode

```
Latency — P50 / P95 / P99 over 5000 calls/mode
  keyword  : P50=   0.7ms  P95=   1.1ms  P99=   1.5ms
  semantic : P50=  20.5ms  P95=  31.4ms  P99=  59.5ms
  hybrid   : P50=  26.4ms  P95=  36.9ms  P99=  52.6ms

PASS — hybrid beats keyword by +0.8pp, semantic by +5.4pp
```
