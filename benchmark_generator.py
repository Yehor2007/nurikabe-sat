# Generates a MASSIVE 8000x8000 instance to guarantee >10s runtime
# 64,000,000 variables forces the I/O and parsing time to exceed 10 seconds.
import sys

SIZE = 8000

print(f"Generating {SIZE}x{SIZE} benchmark... this might take a moment.")

with open("benchmark_huge.txt", "w") as f:
    for r in range(SIZE):
        row = []
        for c in range(SIZE):
            if (r + c) % 2 == 0:
                row.append("1")
            else:
                row.append(".")
        f.write("".join(row) + "\n")

print(f"Success! Created benchmark_huge.txt")