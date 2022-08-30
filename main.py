import asyncio
import logging
import time
import curses

logger = logging.getLogger('async-console-game')


class EventLoopCommand():
    def __await__(self):
        return (yield self)


class Sleep(EventLoopCommand):
    def __init__(self, seconds):
        self.seconds = seconds


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def show_text(canvas, row, column, text='*', attributes=curses.A_NORMAL, sleep=0.0):
    canvas.addstr(row, column, text, attributes)
    canvas.refresh()

    time.sleep(sleep)


def draw(canvas):
    row, column = (5, 20)
    # canvas.addstr(row, column, 'Hello, World!')

    canvas.border()

    # coroutine = blink(canvas, row, column)

    # while True:
    #     try:
    #         coroutine.send(None)
    #     except StopIteration:
    #         break

    #     canvas.refresh()

    coroutines = [
        blink(canvas, row, 20),
        blink(canvas, row, 23),
        blink(canvas, row, 26),
        blink(canvas, row, 29),
        blink(canvas, row, 32),
    ]

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()

        time.sleep(1)

        if len(coroutines) == 0:
            break


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )

    curses.initscr()
    curses.curs_set(False)

    curses.update_lines_cols()
    curses.wrapper(draw)
