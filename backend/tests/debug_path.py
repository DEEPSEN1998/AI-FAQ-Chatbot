import os
import sys

print("Current working directory:")
print(os.getcwd())

print("\nPython executable:")
print(sys.executable)

print("\nFirst 5 entries of sys.path:")
for p in sys.path[:5]:
    print(repr(p))