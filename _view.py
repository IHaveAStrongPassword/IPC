from threading import Thread, Event
import subprocess
from subprocess import TimeoutExpired
import os
import sys
import re
import argparse
from multiprocessing import Pool
from pathlib import Path
import sys

import psutil


def kill(proc_pid):
    p = psutil.Process(proc_pid)
    for c in p.children(recursive=True):
        c.kill()
    p.kill()



processes = []
def call(s, wait = True):
    p = subprocess.Popen([s], shell=True)
    if wait:
        p.wait()
    else:
        processes.append(p)
        return p
def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]
outputs = [d for d in os.scandir('./output') if d.is_dir()]
outputs.sort(key=lambda d: natural_keys(d.name))


try:
        parser = argparse.ArgumentParser(description='View IPC outputs in PhysBAM')
        parser.add_argument('-a', '--all', action='store_true', help='View all outputs')
        parser.add_argument('-l', '--list', action='store_true', help='List all outputs')
        parser.add_argument('-v', '--view', nargs='+', help='View the selected outputs')
        args = parser.parse_args()

        if len(sys.argv)==1:
            parser.print_help(sys.stderr)
            sys.exit(1)
        if args.list or not any(vars(args).values()):
            def f(d):
                c = Path(f'{d.path}/common/last_frame')
                if c.is_file():
                    c = c.read_text().rstrip()
                else:
                    c = 0
                return f'{d.name} ({c})'
            #print(f'Output listing')
            for i, s in enumerate([f(d) for d in outputs]):
                print(f'[{i:2}] {s}')
            print()


        def view(name, started = None, proceed = None, canceled = None):
            p = f'output/{name}/common/last_frame'
            if Path(p).is_file():
                call(f'rm -rf output/{name}/*/')
            call(f'cd output/{name}\n ~/PhysBAM/Scripts/misc/make_sim_obj.sh 2>/dev/null')
            f = Path(p).read_text().rstrip()
            print(f'now viewing ({f} frames): {name}')
            if started:
                started.set()
            title = f'{name} ({f})'
            qt = '$PHYSBAM/Projects/qt_viewer/qt_viewer'
            p = call(f'cd output/{name}\n{qt} . "{title}"', False)
            if canceled:
                def cancel():
                    canceled.wait()
                    if p.poll() is not None:
                        return
                    print(f'kill {p}')
                    kill(p.pid)
                t = Thread(target=cancel)
                t.start()
            p.wait()
            proceed.set()
        if args.view:
            names = set([outputs[int(i)].name for i in args.view])
            p = Pool()
            p.map(view, names)
        if args.all:
            def viewAll(n):
                if(n.startswith('~')):
                    print(f'skip {n}')
                    #continue
                    return
                started = Event()
                proceed = Event()
                cancel = Event()
                t = Thread(target=view, args=[n, started, proceed, cancel])
                t.start()
                started.wait()


                def getEnter():
                    input("Press Enter to continue");
                    cancel.set()
                    proceed.set()

                t = Thread(target=getEnter)
                t.start()
                proceed.wait()
            # enter each output dir and run the viewer in it
            names = [d.name for d in outputs]
            #p = Pool()
            #p.map(viewAll, names)
            for n in names:
                viewAll(n)
finally:
        for p in processes: p.terminate()
