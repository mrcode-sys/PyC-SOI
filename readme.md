# 🖼️ PyC-SOI (Similar Object Identifier)

**PyC-SOI** (*pronounced: Pie-See-Soy*) stands for **Py**thon & **C** - **S**imilar **O**bject **I**dentifier. 

It is a high-performance, intelligent media organizer and classifier designed specifically to process massive image collections ultra-fast. It was built to bypass the hardware bottlenecks common in lightweight, low-spec processors (such as the Intel Celeron line).

The project leverages a **hybrid architecture**: it utilizes the flexibility and rich ecosystem of **Python** for high-level data management and I/O operations, while delegating heavy mathematical loops to a native, raw **C library** via `ctypes`.

---

## 🧠 How the Pipeline Works

To extract maximum speed from the CPU and optimize RAM usage, the organization lifecycle is split into independent modules:

1. **Embedding Extraction (Python + ONNX):** Images are analyzed using a MobileNetV2 model running on the ONNX Runtime. Each image is translated into a 1280-dimensional vector, acting as a "conceptual coordinate" of the image's abstract visual features. These vectors are cached into local JSON files in batches (e.g., 500 images) to preserve disk write-lifespan.
2. **Optimized Clustering (Python + Native C):** The system performs a Two-Stage Clustering algorithm with category merging based on vector averages (Centroids). The cross-comparison loops (`while`) and repetitive Cosine Similarity calculations are processed at bare-metal speed by the compiled C library, slashing identification time from minutes to seconds.
3. **Interactive User Feedback (Lazy Learning):** The system learns from human organization. If you manually move files or rename folders directly via your operating system's file manager, **PyC-SOI** reads the new folder structure upon its next boot and instantly updates its mathematical map, removing the need for heavy neural network retraining.

---

## 📁 Directory Structure

```text
PyC-SOI/
│
├── core/                         # Python logical modules
│   ├── vector_extractor.py       # Embedding extraction via ONNX
│   ├── category_separator.py     # Clustering orchestrator & ctypes bridge
│   └── folder_manager.py         # File validation and management
│
├── src_c/                        # Math engine in pure C
│   └── agrupador.c               # Dot product, linalg norm, and cosine similarity
│
├── lib/                          # Target folder for the compiled dynamic library (.so)
└── data/                         # Local caches and vector persistence in JSON
```
## 🛠️ Compilation & Setup (Linux)

1. **System Requirements**

    Python 3.x

    GCC Compiler (Native on Linux Mint / Ubuntu Server)

2. **Automated Environment Setup**

    The project includes a standalone automation script (build.sh) that verifies directory structure, compiles the native C module with aggressive hardware optimization flags (-O3 -march=native), and installs all Python dependencies automatically.

    Simply open your terminal in the project root directory and run:
    ```Bash
    chmod +x build.sh
    ./build.sh
    ```
    (The -march=native flag instructs GCC to inspect your local CPU—whether it's your development machine or your target Celeron chip—and enable all natively supported instruction sets).

3. **Running the System**

    Once the build script finishes successfully, run the main orchestrator script:
    ```Bash
    python main.py
    ```
## 🗺️ Project Roadmap

    [x] Hybrid Python + C core architecture.

    [x] Persistent vector caching with batch-saving strategies.

    [] Automatic cache synchronization and cleanup of orphaned image vectors.

    [ ] Implementation of a multi-criteria scoring system (Weighted Ensemble).

    [ ] Color Histogram analytical module integration.

    [ ] Object Tagging module integration (via lightweight YOLO models).