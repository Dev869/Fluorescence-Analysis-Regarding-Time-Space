# Fluorescence Analysis Pipline

A calcium fluorescence imaging analysis toolkit for neuroscience research. This repository integrates and customizes several open-source tools into Jupyter notebook pipelines for extracting neurons from calcium imaging videos, detecting physiological events in time-series signals, and analyzing relationships between regions of interest (ROIs).

> **Note:** The upstream tools listed below have been significantly modified to fit our specific experimental needs. The original demo pipelines may not work directly for calcium analysis. Video/TIFF data files are not included in this repository due to size constraints.

## Integrated Tools

| Tool | Upstream | Purpose |
|------|----------|---------|
| [CaImAn](#caiman-calcium-imaging-analysis) | [flatironinstitute/CaImAn](https://github.com/flatironinstitute/CaImAn) | Neuron extraction from calcium imaging videos |
| [RAAIM](#raaim-roi-relationship-analysis) | [aedobyns/lab](https://github.com/aedobyns/lab) | ROI relationship analysis (correlations, clustering) |
| [BASS](#bass-biomedical-analysis-software-suite) | [drcgw/bass](https://github.com/drcgw/bass) | Event detection and analysis in time-series data |
| [Cadence](#cadence-calcium-events-detection) | [asenicos/cadence](https://github.com/asenicos/cadence) | Supervised calcium event detection and rasterization |
| [S8](#s8-n-dimensional-signal-analytics) | [franccm/s8](https://github.com/franccm/s8) | Particle-based dynamic ROI detection in TIFF stacks |

## Overall Workflow

The typical end-to-end analysis follows this pipeline:

```
Raw calcium imaging video (.TIFF)
        |
        v
  [1] CaImAn — Motion correction, neuron extraction, deconvolution
        |
        v
  Extracted fluorescence traces (time-series per ROI)
        |
        v
  [2] RAAIM — ROI relationship analysis (correlations, clustering, spatial maps)
        |
        +--------+--------+
        |                 |
        v                 v
  [3] BASS            [4] Spike Analysis
  Event detection     Post-CaImAn spike
  & measurement       detection
  (peaks, bursts,
   entropy, PSD,
   HRV analysis)
```

## Imaging Parameters

- **Framerate:** 1.5895 fps
- **Spatial resolution:** 0.2635765 pixels/micron

---

## CaImAn (Calcium Imaging Analysis)

**Location:** `notebooks/CAIMAN/`

Modified version of the [CaImAn](https://github.com/flatironinstitute/CaImAn) CNMF (Constrained Nonnegative Matrix Factorization) pipeline, adapted as a replacement for the LC_Pro ImageJ plugin. Best suited for two-photon data with relatively low background noise.

### Pipeline Steps

1. **Motion correction** using NoRMCorre (nonrigid motion correction)
2. **Source separation** using CNMF to extract initial neuron candidates
3. **Component evaluation** to classify and filter neurons
4. **Deconvolution** to extract neural activity

### Notebooks

| Notebook | Description |
|----------|-------------|
| `Extraction_Pipeline_INDIVIDUAL.ipynb` | Process a single recording |
| `Extraction_Pipeline_BATCH.ipynb` | Batch process multiple recordings |
| `demo_pipeline_voltage_imaging.ipynb` | Upstream voltage imaging demo |

### Setup

CaImAn requires its own conda environment, separate from the rest of the toolkit.

```bash
# Navigate to CaImAn data directory
cd C:\Users\labuser\caiman_data\demos\notebooks  # Windows lab machine

# Activate environment and launch
conda activate caiman
jupyter lab

# When finished, shut down:
# Press Ctrl+C in the terminal, then:
conda deactivate
```

---

## RAAIM (ROI Relationship Analysis)

**Location:** `notebooks/RAAIM/` and `RAAIM/`

Analyzes relationships between ROIs extracted from calcium imaging data. Designed specifically for LC_Pro-formatted outputs where column positions and label formats are critical.

### Features

- Correlation analysis between ROI time-series
- K-means clustering of ROIs by measurement similarity
- Spatial relationship mapping (when centroid coordinates are available)
- Descriptive statistics across ROI populations

### Notebooks

| Notebook | Description |
|----------|-------------|
| `RAAIM Rev2.ipynb` | Current version (recommended) |
| `RAAIM_CAIMAN.ipynb` | Adapted for CaImAn-extracted data |
| `RAAIM Rev1.ipynb` | Previous revision |
| `RAAIM_original.ipynb` | Original implementation |
| `RAAIM Plots.ipynb` | Visualization-focused notebook |

### Important Notes

- **Saves without warning!** RAAIM will overwrite existing files of the same name without confirmation.
- Data folder must contain the expected LC_Pro output files.
- If you see a `SettingWithCopyWarning`, it is expected and intentional.

### Dependencies

See `RAAIM/Requirements.txt`:

```
numpy==1.16.6
scipy==1.2.3
pandas==0.24.2
matplotlib==2.2.4
Pillow==6.2.2
```

---

## BASS (Biomedical Analysis Software Suite)

**Location:** `notebooks/BASS/`

> **BASS is still in active development.** Features, APIs, and notebook interfaces may change. Some functionality may be incomplete or experimental.

A Python library and Jupyter notebook system for detecting and measuring events within time-series data. Originally designed for ECG analysis, it has been adapted for calcium fluorescence signals, plethysmography, and other biomedical signals.

### Architecture

BASS is built around three core dictionaries that flow through every function:

- **`Data`** — Holds all versions of the input signal as pandas DataFrames
  - `Data['original']` — Raw time-series as loaded
  - `Data['trans']` — After transformation (filtering, detrending)
  - `Data['shift']` — After linear baseline normalization
  - `Data['rolling']` — After rolling baseline calculation
- **`Settings`** — User-configurable parameters for every pipeline stage (no defaults — all must be set explicitly)
- **`Results`** — All computed outputs: event tables, entropy values, PSD results, etc.
  - `Results['Bursts-Master']` and `Results['Peaks-Master']` — Master event records

### Analysis Pipeline

```
1. Load Data         → Data['original']
2. Transform         → Detrend (linear fit), bandpass filter, Savitzky-Golay smooth
3. Baseline          → Linear | Rolling | Static
4. Peak Detection    → Local minima/maxima with delta threshold (top-down)
5. Peak Filtering    → Amplitude min/max constraints
6. Burst Detection   → Threshold crossing relative to baseline (bottom-up)
7. Burst Filtering   → Duration, inter-event interval, peaks-per-burst constraints
8. Measurements      → Amplitude, intervals, duration, area, attack/decay, frequency
9. Advanced Analysis → PSD, entropy (approximate, sample, histogram), Poincare plots
10. Save & Export    → CSV results, settings files, auto-saved plots
```

### Notebooks

| Notebook | Audience | Description |
|----------|----------|-------------|
| `Single Wave- Interactive.ipynb` | New / basic users | Step-by-step guided analysis with interactive prompts |
| `Single Wave- Basic.ipynb` | Advanced users | Direct parameter entry, less guidance |
| `Kitchen Sink-Bass.ipynb` | Developers / superusers | Full access to all features |
| `BASS v2.0.ipynb` | All | Object-oriented batch processing via `BASS_Dataset` class |
| `BASSING.ipynb` | All | Additional analysis workflows |

### Object-Oriented Interface (BASS v2.0)

The `BASS_Dataset` class (`bass.py`) enables batch processing of multiple recordings:

```python
from bass import BASS_Dataset

# Load datasets (automatically added to BASS_Dataset.Batch)
ds1 = BASS_Dataset(inputDir='/path/to/data', fileName='recording1.txt',
                   outputDir='/path/to/output', fileType='Plain')
ds2 = BASS_Dataset(inputDir='/path/to/data', fileName='recording2.txt',
                   outputDir='/path/to/output', fileType='Plain')

# Run batch analysis with shared settings (synced across all datasets)
ds1.run_analysis(analysis_mod='pleth', settings=ds1.Settings, batch=True)
# Or for EKG:
ds1.run_analysis(analysis_mod='ekg', settings=ds1.Settings, batch=True)
```

**Important:** `BASS_Dataset.Batch` is a class variable that accumulates all instantiated datasets. Restart the Jupyter kernel to clear it between independent analyses.

### Supported File Types

| Type | Format | Notes |
|------|--------|-------|
| `Plain` | Tab-delimited `.txt` | Time (seconds) in first column, no header. General purpose. |
| `ImageJ` | Folder with `ROI normalized.txt`, `Parameter List.txt`, `rgb.png` | Exported from ImageJ ROI analysis |
| `LCPro` | LC_Pro export | Specialized format from the LC_Pro ImageJ plugin |
| `HDF5` | HDF5 (`.h5`) | From RTXI or similar acquisition systems, time in milliseconds |
| `Morgan` | Comma-separated | Legacy format, supports millisecond time scale |

### Analysis Modules

| Module | File | Purpose |
|--------|------|---------|
| Plethysmography | `modules/pleth_analysis.py` | Breathing analysis: breath rate, inspiration/expiration times, apnea detection, AUC |
| EKG/HRV | `modules/ekg_analysis.py` | Heart rate variability: heartbeat count, heart rate, interval entropy, PSD of R-R intervals |

### Signal Processing Options

- **Linear detrending** — Removes photobleaching drift by subtracting best-fit line (gated by Pearson r threshold)
- **Butterworth bandpass filter** — Isolates frequency band of interest (lowcut, highcut, polynomial order)
- **Savitzky-Golay filter** — Smooths signal while preserving event morphology (window size, polynomial order)
- **Absolute value** — Rectifies signal (automatically enabled with Savitzky-Golay)

### Event Detection Methods

- **Peaks (top-down):** Local maxima detection using delta threshold. A peak must exceed its neighboring valleys by at least delta. Works even when the signal baseline is shifting.
- **Bursts (bottom-up):** Threshold crossing relative to a calculated baseline. Event starts when signal exceeds threshold; event ends when it drops below. Baseline can be linear (from a quiet segment), rolling (moving average), or static (user-specified value).

### Advanced Analysis Features

| Feature | Description |
|---------|-------------|
| **Poincare (lag) plots** | Successive-pair scatter plots showing variability; SD1/SD2 ellipse axes |
| **Power Spectral Density** | Frequency domain analysis with configurable bands (ULF, VLF, LF, HF); raw power or dB scale |
| **Histogram Entropy** | Predictability measure (0 = fully predictable, 1 = uniform distribution) |
| **Approximate Entropy** | Regularity measure for time-series (requires bundled PyEEG) |
| **Sample Entropy** | Improved ApEn variant (requires bundled PyEEG) |
| **Moving Statistics** | Sliding window mean, standard deviation, and count |
| **Autocorrelation** | Temporal self-similarity analysis |
| **Frequency plots** | Event rate in events/min over time |

### Setup

```bash
# From the repository root
cd notebooks/BASS

# Launch Jupyter (all .py files must be in the same directory as notebooks)
jupyter notebook
```

### Dependencies

numpy, scipy, pandas, matplotlib, Pillow, h5py, six

PyEEG is bundled as `pyeeg.py` in the BASS directory (required for approximate/sample entropy).

---

## Cadence (Calcium Events Detection)

**Upstream:** [asenicos/cadence](https://github.com/asenicos/cadence)

A neuroinformatics tool for supervised detection and rasterization of calcium events from dF/F fluorescence traces. After calcium imaging videos are processed into relative fluorescence traces (by CaImAn, ImageJ/Fiji, MiniAn, etc.), Cadence provides an interactive GUI for reviewing, accepting, and exporting detected events.

### Features

- **Qt6 GUI** (PySide6) for interactive channel-by-channel review and acceptance of detected events
- **Configurable peak detection** with adjustable threshold and window parameters
- **Low-pass / high-pass filtering** of dF/F traces (recommended for Celena X data; not needed for MiniAn-processed Miniscope data)
- **Fast throughput** — up to 20 channels per minute
- **Export** of rasterized event data to text files for downstream analysis
- **Integration with Elephant/Viziphant** for spike-train analysis (mean firing rate, synchrony, ensemble detection)

### Dependencies

Python 3.8+, PySide6, SciPy, Pandas, Matplotlib. Optional: Elephant, Viziphant (for downstream spike-train analysis).

### Reference

Aseyev et al., *Neuroinformatics* (2024), DOI: [10.1007/s12021-024-09677-3](https://doi.org/10.1007/s12021-024-09677-3)

---

## S8 (N-Dimensional Signal Analytics)

**Upstream:** [franccm/s8](https://github.com/franccm/s8)

An n-dimensional signal analytics tool that uses particle analysis to define dynamic regions of interest (ROIs) in time-series microscopy image data. Processes multi-frame TIFF stacks to detect, track, and analyze transient biological signals or events.

### Features

- **TIFF stack loading** via PIMS for multi-frame microscopy data
- **Temporal smoothing** using Savitzky-Golay filtering with spatial noise reduction and baseline subtraction
- **Adaptive thresholding** with selectable algorithms: Otsu, Triangle, or Yen
- **Binary image segmentation** with noise gating, region labeling, and morphological filtering
- **Particle tracking** of centroids and properties across time frames (via Trackpy)
- **Wave/propagation analysis** — divergence/convergence patterns and wave behavior
- **Metrics extraction** — area, intensity amplitude, duration, and coordinates per event

### Outputs

- Processed TIFF images (filtered, binary, masked)
- PDF report with 7 visualization pages (scatter plots, 3D trajectories, spatial maps)
- Pickle files with complete event dictionaries
- Optional CSV exports with ROI data and coordinates

### Dependencies

Python 3.8+, NumPy, Trackpy, Matplotlib, Plotly, psutil, PIMS, scikit-image, SciPy, tifffile, tqdm

---

## Spike Analysis

**Location:** `notebooks/`

Post-CaImAn spike detection and analysis pipeline.

| Notebook | Description |
|----------|-------------|
| `07_27_Extraction_Pipeline_SpikeAnalysis.ipynb` | Original spike analysis pipeline |
| `07_27_Extraction_Pipeline_SpikeAnalysis_devin.ipynb` | Working copy with modifications |
| `batch_processing.ipynb` | Batch spike analysis across multiple recordings |

---

## Repository Structure

```
├── notebooks/
│   ├── BASS/                  # BASS library + notebooks
│   │   ├── bass.py            # BASS_Dataset class (batch interface)
│   │   ├── bass_functions.py  # Core analysis functions (~1500 lines)
│   │   ├── pyeeg.py           # Bundled entropy library
│   │   ├── modules/           # Specialized analysis pipelines
│   │   │   ├── pleth_analysis.py   # Plethysmography
│   │   │   └── ekg_analysis.py     # ECG / HRV
│   │   ├── bass_settings/     # Saved settings files
│   │   └── *.ipynb            # Analysis notebooks
│   ├── CAIMAN/                # CaImAn extraction pipelines
│   ├── RAAIM/                 # RAAIM analysis notebooks
│   └── *.ipynb                # Spike analysis notebooks
├── RAAIM/                     # RAAIM standalone (with original source)
│   ├── Requirements.txt
│   └── RAAIM_original/        # Upstream RAAIM source
├── README/                    # Lab documentation
│   ├── LCPRO SOP.docx         # LC_Pro standard operating procedure
│   ├── RAAIM Outputs.pdf      # Expected RAAIM output documentation
│   └── *.txt                  # Setup instructions for CaImAn
├── analysis/                  # GraphPad Prism analysis files
└── BASS_README.md             # Detailed BASS protocol documentation
```

## Quick Start

### For calcium imaging neuron extraction:
```bash
conda activate caiman
jupyter lab
# Open notebooks/CAIMAN/Extraction_Pipeline_INDIVIDUAL.ipynb
```

### For ROI relationship analysis:
```bash
jupyter notebook notebooks/RAAIM/
# Open "RAAIM Rev2.ipynb"
```

### For time-series event analysis:
```bash
cd notebooks/BASS
jupyter notebook
# Open "Single Wave- Interactive.ipynb" for guided analysis
# Open "BASS v2.0.ipynb" for batch processing
```

## Input Data Format

For BASS (Plain file type):
- Tab-delimited text file (`.txt`)
- First column: time in seconds
- No header row
- Subsequent columns: signal measurements

For RAAIM:
- LC_Pro export format (specific column layout required)
- Or CaImAn-extracted traces (use `RAAIM_CAIMAN.ipynb`)

## Outputs

All analysis outputs are saved to user-specified output directories:

- **CSV tables** — Event measurements, summary statistics, entropy values, PSD bands
- **Settings files** — Timestamped CSV of all analysis parameters (for reproducibility)
- **Plots** — Auto-saved to `plots/` subdirectory within output folder
- **Subfolders** — Created automatically for Poincare, PSD, Moving Stats, Histogram Entropy, etc.
