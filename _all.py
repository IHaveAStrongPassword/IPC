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
inputDir = f'input'
outputDir = f'output'
incompleteDir = f'incomplete'
testDir = f'test-out'

parser = argparse.ArgumentParser(description='Run models in IPC with pause functionality')
parser.add_argument('-p', '--print', action='store_true', help='Prints commands only')
args = parser.parse_args()

# on Mac:
# progPath = os.path.realpath('.') + '/build/Release/IPC_bin'
# on Minchen's Mac:
# progPath = '/Users/mincli/Library/Developer/Xcode/DerivedData/IPC-cegibpdumtrmuqbjruacrqwltitb/Build/Products/Release/IPC'
# on Ubuntu:
binPath = f'build/IPC_bin'
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
    def run(inputPath):
        #inputPath = os.path.relpath(inputPath, '.')
        model = os.path.basename(inputPath)
        status = glob.glob(f'{incompleteDir}/{model}/status*')
        status.sort(key=natural_keys)
        if len(status) > 0:
            status = status[-1]
            text = ''
            with open(inputPath, 'r') as f:
                text = f.read()
            end = text.find('\nrestart')
            if end > -1:
                text = text[:end]
            text = f'{text}\nrestart {status}\n'
            with open(inputPath, 'w') as f:
                f.write(text)
    
        incompletePath = f'{incompleteDir}/{model}'
        outputPath = f'{outputDir}/{model}'
        
        if args.print:
            cmd = f'{binPath} 100 {inputPath} --numThreads {THREADS} -o {testDir}/{model}'
            print(cmd)
            return
        cmd = f'{binPath} 100 {inputPath} --numThreads {THREADS} -o {incompletePath}'
        subprocess.call([setThreadCount + cmd], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f'complete: {model}')
        subprocess.call([f'mv {incompletePath} {outputPath}'], shell=True)
    def shouldRun(modelPath):
        model = os.path.basename(modelPath)
        hasFile = isfile(modelPath)
        hasTxt = model.endswith('.txt')
        hasOutput = isdir(f'{outputDir}/{model}')
        #hasIncomplete = isdir(f'{incompleteDir}/{f}')
        return hasFile and hasTxt and not hasOutput #and hasIncomplete

    modelPaths = [os.path.relpath(f'{d}/{f}', '.') for (d, _, files) in os.walk(inputDir) for f in files]
    #print(modelPaths)
    modelPaths = list(filter(shouldRun, modelPaths))
    #print(modelPaths)
    pool = Pool()
    pool.map(run, modelPaths)
