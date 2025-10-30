# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands and Workflow

### Environment Setup
```bash
# Create and activate conda environment
conda create --name paddle python=3.12
conda activate paddle

# Install dependencies
python -m pip install paddlepaddle==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
python -m pip install "paddleocr[all]"

# Test installation
python -c "from paddleocr import PaddleOCR; print('PaddleOCR 安装成功！')"
```

### Persistent Service Architecture (Recommended)

**New Workflow for Persistent Model Loading:**

1. **Start OCR Service Once** (10-15 minutes initialization):
```bash
# Start persistent server
python ocr_server.py
# or double-click: start_ocr_service.bat
```

2. **Use OCR Anytime** (instant processing):
```bash
# Single image OCR
python ocr_client.py image_path.jpg

# Batch OCR processing
python batch_ocr_client.py
# or double-click: 批量OCR客户端.bat

# Check server status
python ocr_client.py --status

# Stop service when done
python ocr_client.py --shutdown
# or double-click: stop_ocr_service.bat
```

### Legacy Single-Use Commands
```bash
# Single image OCR (reloads model each time)
python PaddleOCRVL_main.py

# Batch OCR processing (reloads model each time)
python batch_ocr.py

# One-time model conversion (for legacy mode)
python convert_models_once.py
```

## Architecture Overview

This is a CPU-optimized PaddleOCR-VL project now featuring both legacy and persistent service architectures.

### Persistent Service Architecture (New)
**ocr_server.py** - Persistent OCR server
- Loads model once and keeps it in memory indefinitely
- Handles client requests via TCP socket (localhost:8888)
- Supports graceful shutdown and status monitoring
- Multi-threaded client handling

**ocr_client.py** - OCR client for server communication
- Connects to persistent server for instant OCR processing
- Supports single image processing, status queries, and server shutdown
- Handles connection failures and provides detailed error reporting

**batch_ocr_client.py** - Client-mode batch processor
- Same interface as batch_ocr.py but uses persistent server
- Verifies server status before processing
- Provides performance statistics and detailed progress reporting

**start_ocr_service.bat/stop_ocr_service.bat** - Service management scripts
- Windows batch files for easy service lifecycle management
- Handles conda environment activation automatically

### Architecture Components
**ocr_server.py** - Persistent OCR server
- Loads model once and keeps it in memory indefinitely
- Handles client requests via TCP socket (localhost:8888)
- Supports graceful shutdown and status monitoring
- Multi-threaded client handling

**ocr_client.py** - OCR client for server communication
- Connects to persistent server for instant OCR processing
- Supports single image processing, status queries, and server shutdown
- Handles connection failures and provides detailed error reporting

**batch_ocr_client.py** - Client-mode batch processor
- Scans OCR_Flies folder for supported image formats
- Verifies server status before processing
- Provides performance statistics and detailed progress reporting

**setup_safetensors.py** - Critical compatibility layer
- Monkey patches safetensors.safe_open to support Paddle framework
- Handles automatic bfloat16 to float32 conversion during model loading
- Provides transparent bfloat16 support without requiring PyTorch

**convert_models_once.py** - Performance optimization tool
- Converts bfloat16 models to float32 permanently to avoid runtime conversion
- Searches ~/.paddlex/official_models for .safetensors files
- Creates .bak backups before conversion

### Performance Characteristics

**Performance Characteristics:**

- Model initialization: ~2 minutes (once) *(actual: 121.66 seconds)*
- Single image processing: ~80-260 seconds (1.3-4.3 minutes) *(actual performance data)*
- Model stays loaded until manual shutdown
- Eliminates repeated model initialization overhead

**Key Advantage:**
- Model loads once, processes multiple images without reloading
- Image processing time varies based on content complexity (80-260 seconds observed)
- Substantial time savings for multiple image processing

**Critical Note**: CPU implementation runs significantly slower than official PP-OCRv5 CPU version in both modes.

### Model Conversion Architecture

The project implements a two-stage model conversion system:
1. **Runtime conversion** (setup_safetensors.py): Automatic bfloat16→float32 during loading
2. **Permanent conversion** (convert_models_once.py): One-time conversion to eliminate runtime overhead

The bfloat16 conversion uses bit manipulation: `float32_data.view(np.uint32)[:] = bfloat16_data.astype(np.uint32) << 16`

### File Structure and Data Flow

```
input: OCR_Flies/*.png|jpg|jpeg|bmp|tiff|tif|webp|gif
  ↓
batch_ocr_client.py discovers images and sends requests
  ↓
ocr_server.py processes requests using loaded model
  ↓
setup_safetensors.py handles model loading with format conversion
  ↓
output: output/batch_results/[image_name]/{result.json, result.md}
```

### Key Implementation Details

- **Persistent Model**: Model loaded once and kept in memory until service shutdown
- **Client-Server Architecture**: TCP socket communication between client and server
- **Format Support**: Comprehensive image format support including WebP and GIF
- **Error Handling**: Continues processing other images when individual files fail
- **Output Structure**: Each image gets its own directory with JSON and Markdown results
- **Compatibility**: Designed to work around PaddleOCR safetensors limitations in CPU environments

### Dependencies and Environment

- Python 3.12 required
- PaddlePaddle 3.2.0 (CPU version)
- PaddleOCR with all optional dependencies
- NumPy, safetensors for model manipulation
- No GPU dependencies (explicitly CPU-optimized)