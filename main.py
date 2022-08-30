import asyncio
import curses
import logging
import time
from random import choice, randint

logger = logging.getLogger('async-console-game')

TIC_TIMEOUT = 0.1


def create_coroutines(canvas, coroutine_count=1):
    """Создаёт список корутин."""
    coordinates = []
    coroutines = []

    max_y, max_x = canvas.getmaxyx()

    max_y, max_x = max_y - 2, max_x - 2

    while coroutine_count != 0:
        y = randint(1, max_y)
        x = randint(1, max_x)

        if (y, x) not in coordinates:
            coordinates.append((y, x))
            coroutines.append(blink(canvas, y, x, choice('+*.:')))

            coroutine_count -= 1

    return coroutines


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):
    for _ in range(0, randint(0, 20)):
        await asyncio.sleep(0)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(0, 20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(0, 3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(0, 5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(0, 3):
            await asyncio.sleep(0)


def draw(canvas):
    canvas.border()
    canvas.refresh()

    # coroutine = blink(canvas, row, column)

    # while True:
    #     try:
    #         coroutine.send(None)
    #     except StopIteration:
    #         break

    #     canvas.refresh()
    #     time.sleep(TIC_TIMEOUT)

    # row = 0

    # coroutines = [
    #     blink(canvas, row, 0),
    #     blink(canvas, row, 23),
    #     blink(canvas, row, 26),
    #     blink(canvas, row, 29),
    #     blink(canvas, row, 32),
    # ]

    coroutines = create_coroutines(canvas, 200)
    coroutines.append(fire(canvas, 0, 100, rows_speed=0.3))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()

        time.sleep(TIC_TIMEOUT)

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
