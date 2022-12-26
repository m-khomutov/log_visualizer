import matplotlib.pyplot as plt
from datetime import datetime
from typing import List
from .logcounter import LogCounter, LogCounterException


class LogVisual:
    def __init__(self):
        counter: LogCounter = LogCounter()
        plots: int = len(counter)
        height: int = 5 if counter.separate_graphs else 3 * plots
        plt.figure(figsize=(12, height))
        plt.grid()
        for i, key in enumerate(counter, 1):
            dates: List[datetime] = []
            levels: List[int] = []
            for tm, count in counter[key]:
                dates.append(tm)
                levels.append(count)
            if counter.separate_graphs:
                plt.subplot(plots, 1, i)
                plt.grid()
            plt.plot(dates, levels, label=f'"{key}"')
            plt.xlim(counter.xlim)
            plt.ylabel(f'сбор по {counter.calc_period} сек.')
            plt.legend()
        plt.show()


def run():
    try:
        LogVisual()
    except LogCounterException as e:
        print(e.with_traceback())
