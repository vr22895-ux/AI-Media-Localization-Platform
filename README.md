# Adaptive AI Framework for Multilingual Video Localization

An end-to-end AI-powered video localization and dubbing platform that uses **adaptive model routing** to dynamically select the best AI models for different languages and tasks.

## 🎯 Project Overview

This system takes a source video, detects the source language, transcribes speech, translates it into a target language, preserves speaker identity through voice cloning, synchronizes generated speech with lip movements, and produces a final localized video.

**Core Contribution:** An Adaptive AI Orchestration Framework with a Benchmark Knowledge Base that evaluates and routes AI models based on experimental evidence — not assumptions.

## 🏗️ Architecture

```
Video Upload → Audio Extraction → Language Detection → Adaptive ASR Routing
→ Speech-to-Text → Speaker Diarization → Adaptive Translation Routing
→ Machine Translation → LLM Refinement → Quality Validation (+ Fallback)
→ Voice Cloning/TTS → Lip Synchronization → Video Rendering → Evaluation
```

## 🔧 Tech Stack

- **Language:** Python 3.10
- **Backend:** FastAPI
- **Frontend:** Next.js (future)
- **ML Framework:** PyTorch 2.7+ (CUDA 12.8)
- **Video Processing:** FFmpeg
- **Database:** SQLite (MVP) → PostgreSQL (production)

## 🤖 AI Models (Candidates)

| Task | Candidates |
|------|-----------|
| ASR | Faster-Whisper, SeamlessM4T |
| Translation | NLLB-200, IndicTrans2, SeamlessM4T |
| LLM Refinement | Qwen2.5-1.5B |
| Speaker Diarization | pyannote.audio 3.1 |
| Voice Cloning/TTS | XTTS-v2, OpenVoice v2 |
| Lip Sync | Wav2Lip, MuseTalk, LatentSync |

> **Note:** No model is assumed "best." Model selection is justified through experimental evaluation.

## 📋 Prerequisites

- NVIDIA GPU with 8GB+ VRAM (CUDA 12.x)
- Miniconda (Python 3.10 environment)
- FFmpeg
- Git

## 🚀 Setup

```bash
# Clone repository
git clone https://github.com/vr22895-ux/AI-Media-Localization-Platform.git
cd AI-Media-Localization-Platform

# Create and activate conda environment
conda create -n dubbing python=3.10 -y
conda activate dubbing

# Install PyTorch with CUDA 12.8 (for RTX 50-series / Blackwell)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Install FFmpeg
conda install -y ffmpeg -c conda-forge

# Install project dependencies
pip install -r requirements.txt
```

## 📄 Research Base Papers

1. **EmoDubber** (CVPR 2025) — Validates end-to-end dubbing pipeline viability
2. **NLLB** (Meta AI) — Validates multilingual translation for low-resource languages

## 📊 Evaluation Metrics

| Metric | Module | Higher/Lower Better |
|--------|--------|-------------------|
| WER | ASR | Lower |
| BLEU | Translation | Higher |
| COMET | Translation | Higher |
| chrF | Translation | Higher |
| SECS | Voice Cloning | Higher |
| LSE-C | Lip Sync | Higher |
| LSE-D | Lip Sync | Lower |

## 📝 License

Academic use only (Final Year BE Project).

## 👤 Author

Vivek — Computer Engineering, Final Year
