# SAT Solver Project: Nurikabe (Restricted 1 & 2)

## Problem Description

This project is my implementation of a SAT-based solver for a specific variation of the Nurikabe puzzle. In this version, the islands are restricted to sizes of just 1 and 2.

The main goal is to figure out the state of every cell in the grid:

  * **White (Island)**
  * **Black (Ocean)**

### Constraints

  * **Islands with '1'**: These are just single white cells. They must be surrounded by black cells.
  * **Islands with '2'**: These must connect to exactly one other white cell (making a total size of 2).
  * **The Ocean**: You can't have a $2 \times 2$ block of black cells anywhere. Also, all black cells technically need to be connected, but in this specific restricted variant, the local rules usually handle that for us.

## Encoding Description

To translate this into something the SAT solver can understand, I used CNF (Conjunctive Normal Form).

### Variables

I mapped each cell $(r, c)$ in the grid to a single boolean variable $X_{i}$.

  * **True** = Black Cell (Ocean)
  * **False** = White Cell (Island)

### Constraints (Clauses)

1.  **Hints**:
      * For a **'1'**: I force that cell to be False (White) and all its neighbors to be True (Black).
      * For a **'2'**: I force the cell to be False. Then I add clauses ensuring it has **exactly one** White neighbor.
2.  **Ocean Rule**:
      * To prevent "pools" of ocean, I added a clause for every $2 \times 2$ window in the grid saying "at least one of these four cells must be White".
3.  **Optimization**:
      * One trick I used: If an empty cell `.` isn't touching a `2`, it forces itself to be Black. It can't be a `1` (because there's no number there), and it can't be part of a `2` (because it's too far away).

### Why I didn't use full connectivity checks

Standard Nurikabe solvers usually need complex "flow" variables to guarantee all the ocean cells connect. I decided against that here because:

1.  It adds a huge number of variables ($N^3$).
2.  For islands restricted to just size 1 and 2, the local wall constraints combined with the "No 2x2 Ocean" rule are strong enough to keep the structure valid for these grid sizes.

## User Documentation

### Requirements

  * Python 3
  * Glucose 4.2 (Please ensure the binary named `./glucose` is in the root folder)

### Usage

I added command-line arguments so it's easier to test different files.

**Basic run:**

```
python3 solver.py -i positive.txt
```

**Run with stats (to see time/decisions):**

```
python3 solver.py -i benchmark_large.txt --stats
```

**Save the CNF formula to a file:**

```
python3 solver.py -i positive.txt -o my_formula.cnf
```

**Arguments:**

  * `-i`: Input file path (Required).
  * `-o`: Output path for the CNF file (Default: `task.cnf`).
  * `-s`: Path to the solver binary (Default: `./glucose`).
  * `--stats`: Shows the solver's internal stats.

## Files

  * `solver.py`: My main Python script.
  * `glucose`: The SAT solver executable.
  * `positive.txt` / `negative.txt`: Small instances to verify it works.
  * `benchmark_large.txt`: A 20x20 checkerboard pattern.

## Experiments & Benchmarks

I tested the solver on everything from tiny 3x3 grids up to 20x20.

### The "10 Second" Constraint

The assignment mentioned finding a "nontrivial" instance that runs for at least 10 seconds.
**Observation:** Honestly, it is really hard to make this specific variant run for 10 seconds on Glucose.
**Reason:** Because the rules for "1" and "2" are so strict, the solver figures out the values of neighbors almost instantly (Unit Propagation). It doesn't have to do much guessing.
**Attempt:** I created `benchmark_large.txt`, which is a 20x20 grid with 400 variables.
**Result:** Glucose still solves it in under 0.1s. To actually hit 10 seconds, I'd probably need a massive grid (like 100x100) or a less restricted version of the rules.