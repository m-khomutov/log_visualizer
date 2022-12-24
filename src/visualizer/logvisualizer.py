import matplotlib.pyplot as plt
from datetime import datetime
from typing import List
from .logcounter import LogCounter, LogCounterException


class LogVisual:
    def __init__(self):
        counter: LogCounter = LogCounter()
        plots: int = len(counter.timeline)
        plt.figure(figsize=(12, 3 * plots))
        for i, timeline in enumerate(counter.timeline.items(), 1):
            dates: List[datetime] = []
            levels: List[int] = []
            for tm, count in timeline[1]:
                dates.append(tm)
                levels.append(count)
            plt.subplot(plots, 1, i)
            plt.plot(dates, levels, label=f'"{timeline[0]}"')
            plt.xlim(counter.xlim)
            plt.ylabel(f'сбор по {counter.calc_period} сек.')
            plt.legend()
            plt.grid()
        plt.show()


def run():
    try:
        visual: LogVisual = LogVisual()
    except LogCounterException as e:
        print(e.with_traceback())
