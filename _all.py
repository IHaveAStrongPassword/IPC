import subprocess
import os
from multiprocessing import Pool
from os import listdir
from os.path import isfile, join, isdir
import re
import argparse
import glob

cwd = os.path.realpath('.')
input = f'{cwd}/input/'
output = f'{cwd}/output/'
incomplete = f'{cwd}/incomplete/'

# on Mac:
# progPath = os.path.realpath('.') + '/build/Release/IPC_bin'
# on Minchen's Mac:
# progPath = '/Users/mincli/Library/Developer/Xcode/DerivedData/IPC-cegibpdumtrmuqbjruacrqwltitb/Build/Products/Release/IPC'
# on Ubuntu:
progPath = f'{cwd}/build/IPC_bin'
# progPath = os.path.realpath('.') + '/src/Projects/DistortionMin/DistortionMin'

# envSetStr = 'export LD_LIBRARY_PATH=/usr/local/lib\n'
# for Ubuntu or Mac when CHOLMOD is compiled with MKL LAPACK and BLAS
NTSetStr0 = 'export MKL_NUM_THREADS='
# for Ubuntu when CHOLMOD is compiled with libopenblas
NTSetStr1 = 'export OMP_NUM_THREADS='
# for Mac when CHOLMOD is compiled with default LAPACK and BLAS
NTSetStr2 = 'export VECLIB_MAXIMUM_THREADS='

def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def run(model):
    i = f'{input}{model}'
    s = glob.glob(f'{incomplete}{model}/status*')
    s.sort(key=natural_keys)
    if len(s) > 0:
        s = s[-1]
        t = ''
        with open(i, 'r') as f:
            t = f.read()
        prev = t.find('\nrestart')
        if prev > -1:
            t = t[:prev]
        t = f'{t}\nrestart {s}\n'
        with open(i, 'w') as f:
            f.write(t)

    n = f'incomplete/{model}'
    o = f'output/{model}'
    s = f'{NTSetStr0}12\n'
    s+= f'{NTSetStr1}12\n'
    s+= f'{NTSetStr2}12\n'
    s+= f'{progPath} 100 {i} t12 -o {n}'
    subprocess.call([s], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f'complete: {model}')
    subprocess.call([f'mv {n} {o}'], shell=True)
for numOfThreads in ['12']:
    def shouldRun(f):
        hasOutput =  isdir(join(output, f))
        #hasIncomplete = isdir(join(incomplete, f))
        return isfile(join(input, f)) and not hasOutput #and hasIncomplete
    files = filter(shouldRun, listdir(input))
    pool = Pool()
    pool.map(run, files)
