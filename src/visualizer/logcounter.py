import argparse
import os.path
import re
from collections import defaultdict
from datetime import datetime
from enum import IntEnum

State: IntEnum = IntEnum('State', ('BEFORE', 'IN', 'AFTER', 'ERROR'))


class LogCounterException(Exception):
    pass


class PercentPrinter:
    def __init__(self, file: str):
        self._coefficient: float = os.get_terminal_size()[0] / os.path.getsize(file)
        self._offset = [0, 0]

    def print(self, line_size: int) -> None:
        self._offset[0] += line_size
        pos: int = int(self._offset[0] * self._coefficient)
        if pos != self._offset[1]:
            self._offset[1] = pos
            print('#', flush=True, end='')


class LogCounterMeta(type):
    def __new__(mcs, name, bases, namespace):
        parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Istream3 log counter')
        parser.add_argument('log', type=str, help='logfile to parse')
        parser.add_argument('pattern', type=str, help='pattern to calculate')
        parser.add_argument('-begin', type=str, default='', help='begin time (mm/dd/yy hh:mm:ss)')
        parser.add_argument('-end', type=str, default='', help='end time (mm/dd/yy HH:MM:SS)')
        parser.add_argument('-cp', type=int, default=60, help='calculation period sec. (def: 60 sec.)')
        parser.add_argument('-separate', type=str, default='n', help='show graphics separately (y|n, def: n)')
        args: argparse.Namespace = parser.parse_args()
        if not (os.path.exists(args.log) and os.path.isfile(args.log)):
            raise LogCounterException(f'invalid file: {args.log}')
        if not (args.separate == 'y' or args.separate == 'n'):
            raise LogCounterException(f'invalid separate parameter: {args.separate}. [y|n] are valid')

        namespace['_log'] = args.log
        namespace['needle'] = args.pattern.split(',')
        namespace['calc_period'] = args.cp
        namespace['separate_graphs'] = args.separate == 'y'
        namespace['_pattern'] = r'(?P<level>ml[\d]) (?P<time>\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{3})(?P<content>.+)'
        namespace['_timeline']: defaultdict = defaultdict(list)
        try:
            namespace['_begin'] = datetime.strptime(args.begin, '%m/%d/%y %H:%M:%S')
        except ValueError:
            namespace['_begin'] = None
        try:
            namespace['_end'] = datetime.strptime(args.end, '%m/%d/%y %H:%M:%S')
        except ValueError:
            namespace['_end'] = None

        return super().__new__(mcs, name, bases, namespace)


class LogCounter(metaclass=LogCounterMeta):
    def __init__(self) -> None:
        self._xlim: tuple = (None, None)
        pp: PercentPrinter = PercentPrinter(self._log)
        for line in open(self._log, 'r'):
            pp.print(len(line))
            rc: State = self._verify_line(line)
            if rc == State.AFTER:
                break

    def __len__(self):
        return len(self._timeline)

    def __iter__(self):
        return iter(self._timeline)

    def __getitem__(self, item):
        return self._timeline[item]

    @property
    def xlim(self) -> tuple:
        return self._xlim

    def _verify_line(self, line: str) -> State:
        for n in self.needle:
            if n in line:
                m = re.search(self._pattern, line)
                dt: datetime = datetime.strptime(m['time'], '%m/%d/%y %H:%M:%S.%f')
                if self._begin and dt < self._begin:
                    return State.BEFORE
                if self._end and dt > self._end:
                    return State.AFTER
                if self._timeline[n] and (dt - self._timeline[n][-1][0]).total_seconds() < self.calc_period:
                    self._timeline[n][-1] = (self._timeline[n][-1][0], self._timeline[n][-1][1] + 1)
                else:
                    self._timeline[n].append((dt, 1))
                if not self._xlim[0]:
                    self._xlim = (dt, dt)
                else:
                    self._xlim = (self._xlim[0], dt)
                return State.IN
        return State.ERROR
