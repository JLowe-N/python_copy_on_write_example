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

I found that smem was the easiest to analyze.  USS - Unique Set Size, displays the memory unique to a process.
If USS size grows after forking without additional intentional object creation in the script, copy on write behavior
caused by Python garbage collection would be probable.

Debian has a package `smem` which can help.

The test_shm_memory.py script using `psutil` will print out USS with print statements during execution.

Below are results using Python 3.9.7 on MacOS:

### Default Python behavior
`python test_shm_memory.py --no-freeze --size 1`
```
After Fork Process # 32409 before gc:
 pfullmem(rss=79937536, vms=419123167232, pfaults=5993, pageins=807, uss=2097152)
After Fork Process # 42884 before gc:
 pfullmem(rss=6373376, vms=419123167232, pfaults=571, pageins=0, uss=4571136)

Garbage Collection!!!

After Fork Process # 42884 after gc:
 pfullmem(rss=56098816, vms=419123167232, pfaults=4988, pageins=0, uss=34193408)
After Fork Process # 32409 after gc:
 pfullmem(rss=74694656, vms=419123167232, pfaults=7962, pageins=807, uss=34045952)
```
Key in on uss - unique set size. We want this to be small.  
We can see gc.collect (run several times), actually increases uss (copy on write).

### Python behavior when using gc.disable(), gc.freeze(), gc.enable() before fork
`python test_shm_memory.py --freeze --size 1`
```
After Fork Process # 32409 before gc:
 pfullmem(rss=80789504, vms=419793207296, pfaults=6052, pageins=806, uss=2048000)
After Fork Process # 43293 before gc:
 pfullmem(rss=6422528, vms=419793207296, pfaults=580, pageins=0, uss=4014080)

Garbage Collection!!!! Frozen objects before fork

After Fork Process # 43293 after gc:
 pfullmem(rss=3948544, vms=419793207296, pfaults=897, pageins=0, uss=2113536)
After Fork Process # 32409 after gc:
 pfullmem(rss=19529728, vms=419793207296, pfaults=6323, pageins=806, uss=1884160)
 ```

 ### Conclusion

 Using gc.freeze() in Python 3.9.7 reduced Unique Set Size from 34MB in the default Python execution down to 2MB in the frozen execution.
 Copy on write memory was reduced by 95%.