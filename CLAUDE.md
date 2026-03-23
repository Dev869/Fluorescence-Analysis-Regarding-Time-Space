# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a calcium fluorescence imaging analysis toolkit for neuroscience research. It integrates and customizes several open-source tools for detecting and analyzing events in time-series data from fluorescence microscopy recordings. The original upstream tools have been significantly modified to fit specific lab needs.

## Key Components

### BASS (Biomedical Analysis Software Suite) — `notebooks/BASS/`
The primary analysis engine. A Python library + Jupyter notebook pipeline for event detection and measurement in time-series data.

**Architecture:** All top-level functions pass three dictionaries — `Data`, `Settings`, `Results` — to preserve clean namespaces across multi-file sessions. Mid-level wrappers gate pipeline flow based on `Settings`; bottom-level functions are the actual algorithms (built on scipy, numpy, matplotlib, pandas).

- `bass.py` — `BASS_Dataset` class: loads data, syncs settings across batch instances, dispatches to analysis modules
- `bass_functions.py` — Core function library (~1500 lines): signal processing, event detection (peaks/bursts), baseline methods, PSD, entropy, Poincare plots, I/O
- `modules/pleth_analysis.py` — Plethysmography (breathing) analysis pipeline
- `modules/ekg_analysis.py` — ECG/heart rate variability analysis pipeline

**Data flow:** Load → Transform (detrend/filter/smooth) → Baseline → Peak detection → Burst detection → Filter events → Measurements → Analysis (entropy, PSD, Poincare, etc.)

**Data dict keys:** `Data['original']`, `Data['trans']`, `Data['shift']` (linear baseline), `Data['rolling']` (rolling baseline)

### CaImAn Pipelines — `notebooks/CAIMAN/`
Calcium imaging neuron extraction using the CaImAn library. Requires a separate conda environment (`conda activate caiman`).

- `Extraction_Pipeline_INDIVIDUAL.ipynb` — Single-file neuron extraction
- `Extraction_Pipeline_BATCH.ipynb` — Batch processing across multiple recordings
- `demo_pipeline_voltage_imaging.ipynb` — Voltage imaging demo from upstream CaImAn

### RAAIM — `RAAIM/` and `notebooks/RAAIM/`
ROI (Region of Interest) relationship analysis for extracted calcium traces. Multiple revision notebooks exist; `RAAIM Rev2.ipynb` is the current version.

### Spike Analysis — `notebooks/`
`07_27_Extraction_Pipeline_SpikeAnalysis.ipynb` — Post-CaImAn spike detection and analysis. The `_devin` variant is the working copy.

## Running Notebooks

```bash
# For BASS notebooks (standard Python environment)
jupyter notebook notebooks/BASS/

# For CaImAn notebooks (requires caiman conda env)
conda activate caiman
jupyter lab
```

## Dependencies

RAAIM requirements (`RAAIM/Requirements.txt`): numpy, scipy, pandas, matplotlib, Pillow

BASS relies on: numpy, scipy, pandas, matplotlib, h5py, plus PyEEG (bundled as `pyeeg.py` for entropy calculations)

CaImAn has its own conda environment with separate dependency management.

## Important Context

- Video/TIFF data files are excluded from the repo (too large). Analysis notebooks expect external data paths provided at runtime.
- BASS `*.py` files must be co-located with the notebooks that import them (relative imports).
- `bass_functions.py` uses `from __future__ import absolute_import, print_function` — written to be compatible with Python 2/3 but now runs on Python 3.
- The `BASS_Dataset.Batch` class variable accumulates all instantiated datasets for batch processing. This persists across notebook cells — restart the kernel to clear it.
- Imaging metadata: framerate 1.5895, pixels/micron 0.2635765 (from `README/info.txt`).
