# 2D Baseline Solvers and Evaluation Metrics for the RePAIR Dataset

This repository provides the implementation of two novel 2D baseline solvers and evaluation metrics for the **RePAIR Dataset**, introduced in the paper:

**"Re-assembling the Past: The RePAIR Dataset and Benchmark for Realistic 2D and 3D Puzzle Solving"** (in NeurIPS 2024).

The RePAIR dataset represents a challenging benchmark for computational puzzle-solving, featuring realistic fragment reassembly scenarios based on archaeological fresco fragments from the Pompeii Archaeological Park. These solvers and metrics serve as benchmarks for evaluating the performance of computational methods in solving complex 2D puzzles with irregular and eroded fragments.
For more details about the RePAIR dataset paper and baselines, visit the [RePAIR NeurIPS Project Page](https://repairproject.github.io/RePAIR_dataset/).

---

## Overview

### Baseline Solvers
1. **Geometric Greedy Solver**: A baseline solver that iteratively matches fragments based on their geometric properties using a greedy algorithm.
2. **Genetic Solver**: A solver employing a genetic optimization algorithm that minimizes the bounding box area and overlap errors for fragment arrangement.
3. Derech et al. (*"Solving Archaeological Puzzles"*, Pattern Recognition, 119:108065, 2021): We use the code provided by the author. The results of the method are referenced in the paper for comparison purposes. For more details, refer to their [paper](https://doi.org/10.1016/j.patcog.2021.108065) and [code](https://cgm.technion.ac.il/wp-content/uploads/2024/07/Reassembly2d_Sources.zip) from the authors [website](https://cgm.technion.ac.il/publications/).

### Evaluation Metrics
The repository includes evaluation metrics to assess puzzle-solving performance. These metrics account for:
- **Q_pos**: A novel metric for evaluating geometric alignment, which measures the shared area (in 2D) between the predicted and ground-truth fragment configurations, weighted by fragment size. This metric is invariant to rigid transformations, ensuring fair evaluation of positional accuracy.
- **Geometric Alignment**: Evaluating the accuracy of fragment positioning using translation and rotation errors.
- **Neighbor Consistency**: Assessing the accuracy of matching neighboring fragments using a ground-truth mating graph.

These metrics provide a comprehensive evaluation framework for the quality of puzzle-solving solutions.

---

## Installation

### Requirements
- Python 3.9 or later
- A Windows machine (required for the Geometric Greedy Solver)

### Steps
1. Clone the repository:
```
git clone https://github.com/RePAIRProject/2D-baselines
cd 2D-baselines
```

2. Download the [RePAIR dataset](https://drive.google.com/drive/folders/1G4ffmH5lxEqITZMNValiModByYUAO6yk), extract it, and place it in the root directory of the project.

3. For the Geometric Greedy Solver:
   - Download the supplementary files from [springs_server.zip](https://drive.google.com/uc?export=download&id=1ELKJnEcggrtusnFRzAwthtpC-QVgryW1).
   - Extract and place the folder under the *geometric greedy solver* directory.

4. Install Python dependencies:
```
pip install -r  requirements.txt
```

---

## Usage

### Geometric Greedy Solver
1. **Start the server**:
   ```
   geometric_greedy_solver\start_springs_server.bat
   ```

2. **Run the solver**:
   ```
   python geometric_greedy_solver/main.py --pieces_path <PIECES_FOLDER_PATH> --coordinates_path <COORDINATES_FOLDER_PATH> --output_path <CSV_PATH>
   ```
   Example:
   ```
   python geometric_greedy_solver/main.py --pieces_path REPAIR_DATASET_NIPS_24/2D_Fragments/2D_Images/assembled_objects/RPobj_g1_o0001 --coordinates_path geometric_greedy_solver/springs_server/data/RePAIR/csv --output_path results/RPobj_g1_o0001.csv
   ```

   **Required Parameters**:
   - `--pieces_path`: Path to the folder containing puzzle piece images (PNG files)
   - `--coordinates_path`: Path to the folder containing piece coordinate CSV files
   - `--output_path`: Path for the output CSV file containing the reconstruction results

   **Optional Parameters**:
   - `--segmenting_curvedness_threshold`: Threshold for segmenting points (range: (0,1)), default: 0.1
   - `--is_debug_final_assembly`: Enables viewing the final reconstruction

   **Important Requirements**:
   - The piece images and coordinate CSV files must be matched in alphabetical order
   - Both folders must contain the same number of files
   - Piece images should be PNG format
   - Coordinate files should be CSV format with 'x' and 'y' columns

### Genetic Solver

The `genetic_solver.py` script uses a genetic optimization algorithm to solve 2D puzzles. It resizes fragments, processes them with a genetic algorithm, and outputs the reconstructed solution both as a CSV file and an image.

#### Running the Solver

To run the solver, execute the following command:
```
python genetic_solver.py --input_dir <INPUT_DIRECTORY> --resize <RESIZE_DIMENSION> --population_size <POPULATION_SIZE> --max_generations <MAX_GENERATIONS> --mutation_rate <MUTATION_RATE> --output_solution <OUTPUT_SOLUTION_CSV> --output_image <OUTPUT_IMAGE_FILE>
```

#### Example
```
python genetic_solver.py --input_dir puzzle_fragments/ --resize 64 --population_size 100 --max_generations 500 --mutation_rate 0.05 --output_solution solution.csv --output_image solution.png
```

#### Arguments
- `--input_dir`: Directory containing puzzle fragment images.
- `--resize`: Dimension to resize fragments for processing (e.g., 64 for 64x64).
- `--population_size`: Number of individuals in the genetic algorithm population.
- `--max_generations`: Maximum number of generations for the genetic algorithm.
- `--mutation_rate`: Probability of mutation during the genetic algorithm process.
- `--output_solution`: Path to save the output CSV file containing fragment positions and rotations.
- `--output_image`: Path to save the reconstructed puzzle image.

#### Output
1. **CSV File**: Contains the reconstructed solution with columns:
   - `rpf`: Fragment filenames.
   - `x`, `y`: Fragment positions.
   - `rot`: Rotation angle in degrees.
2. **Image File**: A visual representation of the reconstructed puzzle saved as an image.

#### Additional Details
- **Fragment Resizing**: Fragments are resized to the specified dimension (`--resize`) during processing. The solution's positions are transformed back to the original dimensions before saving.
- **Rotation Normalization**: Rotation angles are normalized to the range `[0, 360)` in the output.
- **Canvas Size**: The canvas size for the reconstructed image is automatically set to accommodate all fragments (scaled by a factor of 10 based on the original fragment size).


### Evaluation Metrics

To compute evaluation metrics for some result reconstruction, use the `2D_reconstruction_evaluation.py` script. 

Run the script:
```
python 2D_reconstruction_evaluation.py --pieces_dir <PIECES_DIRECTORY> --results_dir <RESULTS_DIRECTORY> --ground_truth_dir <GROUND_TRUTH_DIRECTORY> --scores_dir <SCORES_DIRECTORY>
```

Example:
```
python 2D_reconstruction_evaluation.py --pieces_dir RePAIR_objects/ --results_dir derech_results/ --ground_truth_dir test_set_gt/ --scores_dir scores/
```

**Arguments**:
- `--pieces_dir`: Directory containing the puzzle pieces.
- `--results_dir`: Directory containing the predicted reconstruction results.
- `--ground_truth_dir`: Directory containing the ground truth data.
- `--scores_dir`: Directory to save the computed evaluation scores.

To compute the adjacency matrix based evaluation metrics, use the `2D_adjacency_based_evaluation.py` scripts. Since the evaluation relies on function calls, you need to import and use it programmatically in Python.

---

## Acknowledgements

This project has received funding from the European Union under the Horizon 2020 research and innovation program.

---

## Citation

If you use this code in your research, please cite the following paper:

```
@inproceedings{repair2024,
title={Re-assembling the Past: The RePAIR Dataset and Benchmark for Realistic 2D and 3D Puzzle Solving},
author={Tsesmelis, Theodore and Palmieri, Luca and Khoroshiltseva, Marina and Islam, Adeela and Elkin, Gur and Shahar, Ofir Itzhak and Scarpellini, Gianluca and Fiorini, Stefano and Ohayon, Yaniv and Alal, Nadav and Aslan, Sinem and Moretti, Pietro and Vascon, Sebastiano and Gravina, Elena and Napolitano, Maria Cristina and Scarpati, Giuseppe and Zuchtriegel, Gabriel and Spühler, Alexandra and Fuchs, Michel E. and James, Stuart and Ben-Shahar, Ohad and Pelillo, Marcello and Del Bue, Alessio},
booktitle={NeurIPS},
year={2024}
}
```

