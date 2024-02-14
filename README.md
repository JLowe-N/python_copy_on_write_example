# Description

Attempts to replicate Python garbage collection impact described
here: 
https://instagram-engineering.com/copy-on-write-friendly-python-garbage-collection-ad6ed5233ddf

Provide a simple example of the benefits of gc.freeze() prior to forking a process.
Do some common operations like importing shared packages and allocate large Python data objects.

## Commands
Install some common web application libraries to preload & share between parent & child.
Recommend installing in a Python virtual environment for isolation.
`pip install -r requirements.txt`

Test basic Python behavior on forking when gc.freeze() is not present:
`python test_shm_memory.py --no-freeze --size 2000000`
Ref count updates reportedly force making a copy of objects in the child process when it could be shared.

Test to see if shared memory is not copied (Copy of Write) when garbage collection is invoked:
`python test_shm_memory.py --freeze --size 2000000`

## Analysis

You will need a utility to observe shared memory, while also avoiding double counting memory across processes.
Resident Set Size reported in top/htop does a poor job as shared memory is lumped in with process-specific memory.

https://github.com/kwkroeger/smem

This only appears to work in Debian/Ubuntu, but not Mac.

## Results

Python 3.9.7 / Debian Container

I found that smem was the easiest to analyze.  USS - Unique Set Size, displays the memory unique to a process.
If USS size grows after forking without additional intentional object creation in the script, copy on write behavior
caused by Python garbage collection would be probable.


`smem -t |egrep "RSS|test_shm_memory.py"`
  PID User     Command                         Swap      USS      PSS      RSS
45415 esp      grep -E --color=auto RSS|te        0      360      449     2548
45306 esp      python3 test_shm_memory.py         0     1560   400802   803200 # Child
45305 esp      python3 test_shm_memory.py         0     1604   400987   805352 # Parent