import sys
import os
import subprocess

def solve_nurikabe(filename):
    # check if the instance file exists before proceeding
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found.")
        return
    
    # load and sanitize the input grid
    # we need to handle potential whitespace or formatting issues from different text editors
    with open(filename, 'r') as f:
        raw_lines = f.readlines()

    grid = []
    for line in raw_lines:
        clean = line.strip().replace(" ", "").replace("\t", "")
        if clean:
            grid.append(list(clean))

    rows = len(grid)
    cols = len(grid[0])

    # Variable Mapping:
    # Each cell (r, c) is mapped to a unique integer ID > 0.
    # Semantics: True = black cell (Ocean), False = white cell (Island).
    def var_idx(r, c):
        return r * cols + c + 1

    clauses = []
    
    # Iterate over the grid to generate local constraints
    for r in range(rows):
        for c in range(cols):
            v = var_idx(r, c)

            # identify valid orthogonal neighbors
            nbs = []
            for nr, nc in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
                if 0 <= nr < rows and 0 <= nc < cols:
                    nbs.append(var_idx(nr, nc))

            cell = grid[r][c]

            # Constraint 1: Hint '1'
            # If a cell contains '1', it is an island of size 1.
            # Logic: The cell itself must be white (false), and all neighbors must be black (true).
            if cell == '1':
                clauses.append([-v]) # Force self to white
                for n in nbs:
                    clauses.append([n]) # Force neighbors to black

            # Constraint 2: Hint '2'
            # If a cell contains '2', it is an island of size 2.
            # Logic: The cell is white. Exactly one neighbor is white.
            elif cell == '2':
                clauses.append([-v]) # Force self to white

                # Rule: At least one neighbor must be white (not all can be black)
                # CNF: (-n1 v -n2 v ...)
                clauses.append([-n for n in nbs])

                # Rule: At most one neighbor can be White (pairwise exclusion)
                # This ensures we don't form a 'T' shape or larger blob.
                for i in range(len(nbs)):
                    for j in range(i + 1, len(nbs)):
                        clauses.append([nbs[i], nbs[j]])


                # Rule: The chosen white neighbor cannot extend the island further.
                # Its neighbors (except the original '2') must be Black.
                for nr, nc in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
                    if 0 <= nr < rows and 0 <= nc < cols:
                        n_var = var_idx(nr, nc)

                        # look at the neighbors of this neighbor
                        nn_list = []
                        for nnr, nnc in [(nr-1, nc), (nr+1, nc), (nr, nc-1), (nr, nc+1)]:
                            if 0 <= nnr < rows and 0 <= nnc < cols:
                                nn_list.append(var_idx(nnr, nnc))

                        # Implication: If n_var is white -> its neighbors (nn) must be black        
                        for nn in nn_list:
                            if nn != v:
                                clauses.append([n_var, nn])

            # Constraint 3: Empty Cells
            # Optimization: In the "1 & 2" variant, an island can only start at a number.
            # If an empty cell is not adjacent to a '2', it cannot possibly be white
            # because '1's are isolated and '2's can only extend one step.
            elif cell == '.':
                is_near_2 = False
                for nr, nc in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if grid[nr][nc] == '2':
                            is_near_2 = True

                # If not near a 2, force it to be Ocean (black) to reduce search space            
                if not is_near_2:
                    clauses.append([v])

    # Constraint 4: The Ocean Rule
    # No 2x2 block of cells can be entirely black (True).
    # CNF: (-A v -B v -C v -D) for every 2x2 square.
    for r in range(rows - 1):
        for c in range(cols - 1):
            v1, v2 = var_idx(r, c), var_idx(r+1, c)
            v3, v4 = var_idx(r, c+1), var_idx(r+1, c+1)
            clauses.append([-v1, -v2, -v3, -v4])


    cnf_file = "task.cnf"
    res_file = "solution.txt"
    
    with open(cnf_file, 'w') as f:
        f.write(f"p cnf {rows * cols} {len(clauses)}\n")
        for c in clauses:
            f.write(" ".join(map(str, c)) + " 0\n")

    if not os.path.exists("./glucose"):
        print("Error: glucose binary not found.")
        return

    subprocess.call(["./glucose", cnf_file, res_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Decode Result
    if not os.path.exists(res_file):
        print("Error: Solver output not found.")
        return

    with open(res_file, 'r') as f:
        content = f.read()

    model = set()
    tokens = content.replace('v', '').split()
    
    if not tokens and "UNSAT" in content:
        print("UNSATISFIABLE")
        return

    try:
        for t in tokens:
            val = int(t)
            if val > 0:
                model.add(val)
    except ValueError:
        pass
    
    if len(model) == 0 and "UNSAT" in content:
        print("UNSATISFIABLE")
        return

    # Visualizing the solution
    print(f"Solution for {filename}:")
    for r in range(rows):
        s = ""
        for c in range(cols):
            if var_idx(r, c) in model:
                s += "#"
            else:
                orig = grid[r][c]
                s += orig if orig != '.' else '.'
        print(s)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 solver.py <file>")
    else:
        solve_nurikabe(sys.argv[1])