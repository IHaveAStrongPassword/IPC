"""
Adapted from batch.py

- Implemented pause functionality so that incomplete models resume on next run.
"""

THREADS = 12

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

parser = argparse.ArgumentParser(description='Run models in IPC with pause functionality')
parser.add_argument('-p', '--print', action='store_true', help='Prints commands only')
args = parser.parse_args()

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


setThreadCount = f'{NTSetStr0}{THREADS}\n{NTSetStr1}{THREADS}\n{NTSetStr2}{THREADS}\n'
if args.print:
    print(setThreadCount)
if True:
    def atoi(text): return int(text) if text.isdigit() else text
    def natural_keys(text):
        '''
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        '''
        return [ atoi(c) for c in re.split(r'(\d+)', text) ]
    def run(model):
        inp = f'input/{model}'
        status = glob.glob(f'{incomplete}{model}/status*')
        status.sort(key=natural_keys)
        if len(status) > 0:
            status = status[-1]
            text = ''
            with open(inp, 'r') as f:
                text = f.read()
            end = t.find('\nrestart')
            if end > -1:
                text = text[:end]
            text = f'{text}\nrestart {status}\n'
            with open(inp, 'w') as f:
                f.write(text)
    
        inc = f'incomplete/{model}'
        out = f'output/{model}'
        
        if args.print:
            cmd = f'{progPath} 100 {inp} --numThreads {THREADS} -o {out}'
            print(cmd)
            return
        cmd = f'{progPath} 100 {inp} --numThreads {THREADS} -o {inc}'
        subprocess.call([setThreadCount + cmd], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f'complete: {model}')
        subprocess.call([f'mv {inc} {out}'], shell=True)
    def shouldRun(f):
        hasOutput =  isdir(join(output, f))
        #hasIncomplete = isdir(join(incomplete, f))
        return isfile(join(input, f)) and not hasOutput #and hasIncomplete
    files = filter(shouldRun, listdir(input))
    pool = Pool()
    pool.map(run, files)
