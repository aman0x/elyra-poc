# ROM-PIPELINE: Cylinder Flow Reduced Order Modeling

This pipeline demonstrates Reduced Order Modeling (ROM) using the Cylinder Flow dataset. It is beginner-friendly and designed to run on standard hardware.

## Dataset Overview
- **Source:** [ROM_code repository by Hugo Lui](https://github.com/hugolui/ROM_code)
- **Description:** Flow past a cylinder at Re=150, showing classic vortex shedding (MDPI)
- **Format:** CGNS and HDF5, ~280 training snapshots
- **Why it's great:** Complete ROM implementation, well-documented, small enough for most laptops
- **Download:** [Cylinder Data (HDF5)](https://drive.google.com/open?id=1cqxzDNG6ic1HqC7vmjq_bBmGFB9qYihp)

### MinIO Bucket and Folder Structure
- **Bucket name:** `rom-data`
- **Required structure inside the bucket:**
  - `/examples/cylinder/cylinder_data.hdf5`
  - That is, the root of the bucket must have a folder called `examples`, inside it a folder `cylinder`, and inside that the file `cylinder_data.hdf5`.
- Ensure this structure exists in your MinIO instance before running the pipeline.

## Pipeline Structure
This pipeline consists of three main notebooks:
1. **0_fetch_data.ipynb**: Downloads and inspects the Cylinder Flow dataset from MinIO or Google Drive, uploads to MinIO, and verifies data integrity.
2. **2_rom_modeling.ipynb**: Preprocesses the data, extracts velocity fields, creates the snapshot matrix, performs mean subtraction and normalization, and uploads processed data.
3. **3_visuazalition.ipynb**: Visualizes the results, including POD modes, energy captured, and generates a summary report.

## Prerequisites
- Python 3.8+
- Jupyter Notebook or Elyra Pipeline environment
- Access to MinIO or S3-compatible storage (default: minioadmin/minioadmin)
- Packages: numpy, h5py, matplotlib, boto3, psutil

## Environment Setup
Install dependencies (if not already installed):
```bash
pip install numpy h5py matplotlib boto3 psutil
```

Set environment variables for MinIO/S3 if needed:
```bash
export S3_ENDPOINT=http://minio:9000
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
```

## Running the Pipeline
1. **Fetch Data:**
   - Open `0_fetch_data.ipynb` and run all cells.
   - This will download the dataset, inspect its contents, and upload it to MinIO.
2. **ROM Modeling:**
   - Open `2_rom_modeling.ipynb` and run all cells.
   - This notebook preprocesses the data and prepares it for ROM analysis.
3. **Visualization:**
   - Open `3_visuazalition.ipynb` and run all cells.
   - Generates visualizations and a summary report of the ROM results.

## Usage Example
```python
# Example: Inspecting the HDF5 data structure
data = h5py.File('cylinder_data.hdf5', 'r')
print(list(data.keys()))
# Output: ['velocity', 'x', 'y']
```

## Outputs
- Processed HDF5 files and parameters in `rom-pipeline/outputs/`
- Visualizations and HTML report summarizing POD results

## References
- [ROM_code repository](https://github.com/hugolui/ROM_code)
- [Proper Orthogonal Decomposition (POD)](https://en.wikipedia.org/wiki/Proper_orthogonal_decomposition)

---
For questions or contributions, please open an issue or pull request.