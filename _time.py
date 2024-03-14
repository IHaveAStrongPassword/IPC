
import argparse
import os
import re
import sys

# https://github.com/ipc-sim/IPC/blob/71ec1da8fc98ea0f18083c62cc871804563b2d69/src/main.cpp#L1324

parser = argparse.ArgumentParser(description='View times for models')
parser.add_argument('-a', '--all', action='store_true', help='View all times')
parser.add_argument('-l', '--list', action='store_true', help='List models')

parser.add_argument('-i', '--index', nargs='+', help='View models at index')

parser.add_argument('-t', '--time', action='store_true', help='Sort activity by time')
parser.add_argument('-n', '--name', action='store_true', help='Sort activity by name')
parser.add_argument('-z', '--zeros', action='store_true', help='Hide activity with zero time') 
args = parser.parse_args()

models =  [d for d in os.scandir('./output/') if d.is_dir()]
if args.list:
    for i,model in enumerate(models): print(f'[{i}] {model.name}')
    sys.exit(0)

if args.index:
    models = [models[int(i)] for i in args.index]
for model in models:
    print('=' * 64)
    print(f'times for {model.name}') # ({model.path})')
    all = dict()
    infos = [f for f in os.scandir(model.path) if f.is_file() and f.name.startswith('info')]
    for info in infos:
        #print(f'reading {info.path}')
        with open(info.path, 'r') as file:
            i_total = 0
            for pair in re.findall(r'^\s*([0-9.]+) s: ([a-zA-Z\s]+)$', file.read(), re.MULTILINE):
                (time, name) = pair
                #print(f'{name:<16}{time}')
                all[name] = all.get(name, 0) + float(time)
                if name == 'Total':
                    i_total += 1
                    key = f'Total [{i_total}]'
                    all[key] = all.get(key, 0) + float(time)
    def k_time(ip):
        (i,p)=ip
        (name, time) = p
        return time
    def k_name(ip):
        (i,p)=ip
        (name, time) = p
        return name.lower()
    k = None
    if args.time:
        k = k_time
    elif args.name:
        k = k_name

    print(f'steps: {len(infos)}')

    def pl(name, time, avg, part): return f'{name:<24}|{time:>16}|{avg:>12}|{part:>8}'
    #print('|'.join(['name'.ljust(24), 'time (s)'.rjust(16), 'part'.rjust(8)]))
    print('-' * 64)
    print(' i| ' + pl('activity', 'sec', 'sec/step', 'part'))
    print('-' * 64)
    total = all['Total'] = all.pop('Total')

    items = list(enumerate(all.items()))
    if k is not None:
        items = sorted(items, key=k);
    for i, p in items:
        (name, time) = p
        if time == 0 and args.zeros:
            continue
        #print('|'.join([f'{name:<24}', f'{time:>5.5f}'.rjust(16),  f'{100 * time/total:3.4f}'.rjust(8)]));
        print(f'{i:2}| ' + pl(name, f'{time:>5.5f}', f'{time/len(infos):5.5f}', f'{100 * time/total:3.4f}'))
