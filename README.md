# SAT Solver Project: Nurikabe (Restricted 1 & 2)

## Problem Description
This project solves a restricted variant of the Nurikabe puzzle where island sizes are strictly limited to 1 and 2. The goal is to determine the state of every cell in a grid such that:
1. **Islands (White Cells)**: 
   - Cells containing a '1' must be isolated (size 1).
   - Cells containing a '2' must connect to exactly one other white cell (size 2).
2. **Ocean (Black Cells)**: 
   - All other cells are Black.
   - **Ocean Rule**: No $2 \times 2$ block of cells can be entirely Black.
   - (Connectivity is implicitly handled by the strict local constraints in this restricted variant).

## Encoding
The problem is translated into CNF (Conjunctive Normal Form) for the Glucose SAT solver.

### Variables
- Each cell $(r, c)$ is represented by a boolean variable $X_{r,c}$.
- **True** = Black Cell (Ocean)
- **False** = White Cell (Island)

### Constraints
1. **Hint Logic**:
   - **'1'**: Forced False. All orthogonal neighbors forced True.
   - **'2'**: Forced False. Exactly one orthogonal neighbor forced False; that neighbor's neighbors (excluding the original '2') are forced True.
   - **Empty ('.')**: If an empty cell is not adjacent to a '2', it is forced True (Black) because it cannot form a valid island.
2. **Ocean Rule**:
   - Clauses are added to prevent any $2 \times 2$ block of variables from being all True ($\neg X_{r,c} \lor \neg X_{r+1,c} \lor \neg X_{r,c+1} \lor \neg X_{r+1,c+1}$).

## User Documentation

### Requirements
- **Python 3**
- **Glucose 4.2** (The executable binary named `glucose` must be in the project root folder).

### Usage
Run the script with the path to an instance file:
```bash
python3 solver.py positive.txt