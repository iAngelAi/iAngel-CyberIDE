# Mission 003: Stress Test & Optimize File Watcher

**Priority:** High
**Status:** Ready to Start

## Context
We have hardened the `FileMapper` with `fnmatch` and forced exclusions, but we haven't stress-tested it on massive repositories (e.g., 50k+ files).

## Objectives
1. Create a benchmark script `scripts/benchmark_watcher.py`.
2. Measure CPU/RAM usage of `neural_cli` when targeting a large mocked directory structure.
3. Optimize `file_watcher.py` debouncing if necessary (currently 1s).

## Definition of Done (DoD)
- [ ] Benchmark script committed
- [ ] CPU usage < 5% on idle for 10k files
- [ ] RAM usage < 200MB stable
