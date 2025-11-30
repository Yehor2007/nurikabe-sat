import sys
import os
import subprocess
import argparse

def parse_arguments():
    # define command line arguments
    parser = argparse.ArgumentParser(description="Nurikabe (1 & 2) SAT Solver")
    parser.add_argument("-i", "--input", required=True, help="Path to the instance file")
    parser.add_argument("-o", "--output", default="task.cnf", help="Path to save the generated DIMACS CNF formula")
    parser.add_argument("-s", "--solver", default="./glucose", help="Path to the SAT solver executable")
    parser.add_argument("--stats", action="store_true", help="Output statistics from the SAT solver")
    return parser.parse_args()

def solve_nurikabe():
    args = parse_arguments()
    
    # check if the input file exists
    if not os.path.exists(args.input):
        print(f"Error: File {args.input} not found.")
        return

    # read the input file
    # we also handle potential whitespace issues to be safe
    with open(args.input, 'r') as f:
        raw_lines = f.readlines()

    grid = []
    for line in raw_lines:
        clean = line.strip().replace(" ", "").replace("\t", "")
        if clean:
            grid.append(list(clean))

    rows = len(grid)
    cols = len(grid[0])
    
    # map variables to grid positions
    # variables are numbered from 1
    # True means black cell (Ocean), False means white cell (Island)
    def var_idx(r, c):
        return r * cols + c + 1

    clauses = []
    
    # iterate over the grid and generate constraints
    for r in range(rows):
        for c in range(cols):
            v = var_idx(r, c)
            
            # get valid neighbors
            nbs = []
            for nr, nc in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
                if 0 <= nr < rows and 0 <= nc < cols:
                    nbs.append(var_idx(nr, nc))

            cell = grid[r][c]

            # constraints for '1'
            # if a cell is 1, it must be white, and neighbors must be black
            if cell == '1':
                clauses.append([-v]) 
                for n in nbs: 
                    clauses.append([n])
            
            # constraints for '2'
            # if a cell is 2, it is white and connects to exactly one white neighbor
            elif cell == '2':
                clauses.append([-v])
                
                # at least one neighbor is white
                clauses.append([-n for n in nbs]) 

                # at most one neighbor is white
                # this prevents the island from branching
                for i in range(len(nbs)):
                    for j in range(i + 1, len(nbs)):
                        clauses.append([nbs[i], nbs[j]])
                
                # the white neighbor cannot have other white neighbors
                # this ensures the island size is exactly 2
                for nr, nc in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
                    if 0 <= nr < rows and 0 <= nc < cols:
                        n_var = var_idx(nr, nc)
                        
                        # check neighbors of the neighbor
                        nn_list = []
                        for nnr, nnc in [(nr-1, nc), (nr+1, nc), (nr, nc-1), (nr, nc+1)]:
                            if 0 <= nnr < rows and 0 <= nnc < cols:
                                nn_list.append(var_idx(nnr, nnc))
                        
                        # if n_var is white, its neighbors must be black
                        for nn in nn_list:
                            if nn != v: # except the original cell
                                clauses.append([n_var, nn])

            # constraints for empty cells
            # optimization: in this variant, islands only start at numbers
            # so if an empty cell is not next to a 2, it must be black
            elif cell == '.':
                is_near_2 = False
                for nr, nc in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if grid[nr][nc] == '2':
                            is_near_2 = True
                
                if not is_near_2:
                    clauses.append([v])

    # ocean rule
    # no 2x2 block of cells can be entirely black
    for r in range(rows - 1):
        for c in range(cols - 1):
            v1, v2 = var_idx(r, c), var_idx(r+1, c)
            v3, v4 = var_idx(r, c+1), var_idx(r+1, c+1)
            clauses.append([-v1, -v2, -v3, -v4])

    # write the formula in DIMACS format
    with open(args.output, 'w') as f:
        f.write(f"p cnf {rows * cols} {len(clauses)}\n")
        for c in clauses:
            f.write(" ".join(map(str, c)) + " 0\n")

    # call the solver
    if not os.path.exists(args.solver):
        print(f"Error: Solver executable '{args.solver}' not found.")
        return

    # use a temp file for output
    res_file = "solver_output.tmp"
    
    # run glucose
    cmd = [args.solver, args.output, res_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # print statistics if requested
    if args.stats:
        print("--- SOLVER STATISTICS ---")
        for line in result.stdout.splitlines():
            if line.startswith("c"):
                print(line)
        print("-------------------------")

    # check if output was generated
    if not os.path.exists(res_file):
        print("Error: Solver produced no output file.")
        return

    with open(res_file, 'r') as f:
        content = f.read()
    
    # clean up
    if os.path.exists(res_file):
        os.remove(res_file)

    if "UNSAT" in content:
        print("UNSATISFIABLE")
        return

    # parse the model
    model = set()
    tokens = content.replace('v', ' ').split()
    for t in tokens:
        try:
            val = int(t)
            if val > 0: model.add(val)
        except ValueError: pass

    if not model and "UNSAT" in content:
        print("UNSATISFIABLE")
        return

    # print the result in a readable format
    print(f"Solution for {args.input}:")
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
    solve_nurikabe()