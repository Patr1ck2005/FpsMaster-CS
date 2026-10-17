# FpsMaster-CS

**A historical computer-vision and input-control prototype.** The repository preserves experiments combining YOLOv5 detection, tracking/filtering, control logic and a Windows desktop interface.

[简体中文](README.zh-CN.md) · [Documentation history](docs/README-history.md)

## Source index

| Path | Contents |
|---|---|
| `models/`, `utils/` | Detection-model support and upstream-derived utilities |
| [cs_master/detector.py](cs_master/detector.py) | Detection integration |
| [cs_master/kfilter.py](cs_master/kfilter.py) | Tracking/filtering work |
| `cs_master/controller.py`, `cs_master/main_loop.py` | Input/control pipeline |
| `cs_master/gui.py`, `main.py` | PyQt desktop entry |
| `*.engine`, `*.pyd` | Historical platform-specific binary artifacts |

## Status and research boundary

Legacy source archive, not a maintained competitive-game product or a validated performance benchmark. Earlier claims about perfect recognition, indistinguishable input, leaderboard results or anti-cheat compatibility are not supported here by a reproducible evaluation and should not be treated as verified facts.

Opening the desktop application can initialize input listeners/control logic. This README intentionally provides a **source-reading entry**, not a quick-start for use against other players. Appropriate further study uses offline recordings, a self-built simulator or an explicitly authorized test environment, with detection error, tracking stability and latency measured separately.

The historical environment mixes Windows-specific native modules, serialized engines and Python dependencies; current portability and binary provenance have not been revalidated. No driver, GUI, controller or model was launched during this documentation update. Existing source and contributor history remain intact.

## License and provenance

No repository-wide license is declared in this snapshot. Included model code and utilities can have their own upstream terms; inspect their headers/notices before reuse. Binary presence is not a license or a reproducibility claim. The [previous public README](docs/README-history.md) remains available through Git history for provenance.
