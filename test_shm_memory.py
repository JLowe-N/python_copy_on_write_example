import time
import gc
import argparse
import psutil
import os

parser = argparse.ArgumentParser()
parser.add_argument('--freeze', '-f', action='store_true')
parser.add_argument('--size', '-s', type=int, default=1, help="number of elements to use for in-memory list")
parser.add_argument('--no-freeze', '-nf', dest='freeze', action='store_false')
parser.set_defaults(freeze=True)
args = parser.parse_args()

if args.freeze:
    gc.disable()

print("Lower Unique Set Size (USS) memory is better, as this is the memory specific to a process.")
print(f"Test: Freeze is {args.freeze}, Array Size is {args.size}")
print("==================\n================")
parent_process = psutil.Process()
print(f"Parent Process # {parent_process.ppid()} before import:")
print(parent_process.memory_full_info())

# Make some large imports, ideally these are shared between parent & child memory
import tornado
import pandas
import numpy
import sqlalchemy
print("Libraries imported!")

# Make a large object in memory
big_list = [x for x in range(args.size)]
print("List allocated!")

# Instagram procedure pre-fork for their POC
lists = []
strs = []
for i in range(16000):
    lists.append([])
    for j in range(40):
        strs.append(' ' * 8)


print(f"Parent Process # {parent_process.ppid()} after import:")
print(parent_process.memory_full_info())

if args.freeze:
    print("FREEZE!")
    gc.freeze()
    gc.enable()

print("FORK!")
os.fork()

current_process = psutil.Process()
print(f"After Fork Process # {current_process.ppid()} before gc:\n {current_process.memory_full_info()}")



for _ in range(10):
    gc.collect()
    time.sleep(2)

print(f"After Fork Process # {current_process.ppid()} after gc:\n {current_process.memory_full_info()}")

time.sleep(60)

# lets put some references here to avoid optimizations on gc
lists
strs
big_list
tornado
pandas
numpy
sqlalchemy
