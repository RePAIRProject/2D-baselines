# RePAIR Example Repository
This repository includes the 2D baselines solvers. 

# 1) Description
This is a test repository for demonstration. It has some cool features.

# 2) Installation
Build/Installation instructions (including requirements and dataset).
The geometric solver was running in Python 3.9

1. Clone the repo
```
git clone https://github.com/RePAIRProject/2D-baselines
cd 2D-baselines
```

2. Download the repair dataset 

Download the [repair dataset](https://drive.google.com/drive/folders/1G4ffmH5lxEqITZMNValiModByYUAO6yk), extract the zip, and put it in the root directory of the project. 

3. Download supplementary for the geometric greedy solver
Download from [springs_server.zip](https://drive.google.com/uc?export=download&id=1ELKJnEcggrtusnFRzAwthtpC-QVgryW1), extract the zip, and put the extracted folder under the geometric greedy solver directory.

4. Install python libraries
```
pip install -r  requirements.txt
```

# 3) Usage

## Geometric greedy solver
To run the sovler, you would need a Windows machine (10\11).


In a new terminal, run the following to initiate the server.

```
"geometric greedy solver\start_springs_server.bat"
```

Then, you can run the solver:
```
    python "geometric greedy solver"/main.py --group <GROUP_IDENTIFIER> --output_path <CSV_PATH>
```

Where the following --group is the group identifier  and --output_path is the path to the csv saving the transformations. For example

```
 python "geometric greedy solver"/main.py --group RPobj_g1_o0001 --output_path REPAIR_DATASET_NIPS_24/tmp/RPobj_g1_o0001.txt"
```

The following parameters are optional: 
- *--segmenting_curvedness_threshold*: determine the curvedness threshold for the segmenting points. This value should be in (0,1)
- *--is_debug_final_assembly*: if specified, enables viewing the final reconstruction of the group.


# 4) Known Issues
Bug descriptions.

# 5) Relevant publications
Some publications.

