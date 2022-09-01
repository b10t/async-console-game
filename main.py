import asyncio
import curses
import glob
import logging
import os
import time
from itertools import cycle
from random import choice, randint

from curses_tools import draw_frame, read_controls

logger = logging.getLogger('async-console-game')

TIC_TIMEOUT = 0.1


def load_spaceship_frames(folder='frames'):
    spaceship_frames = []

    for frame_filename in glob.glob(os.path.join(folder, 'rocket_frame_*.txt')):
        logger.info(f'Found frame file: {frame_filename}')

        with open(frame_filename, 'r') as frame_file:
            spaceship_frames.append(frame_file.read())

    return spaceship_frames


def create_coroutines(canvas, coroutine_count=1):
    """Создаёт список корутин."""
    coordinates = []
    coroutines = []

    max_row, max_column = canvas.getmaxyx()
    max_row, max_column = max_row - 2, max_column - 2

    while coroutine_count != 0:
        row = randint(1, max_row)
        column = randint(1, max_column)

        if (row, column) not in coordinates:
            coordinates.append((row, column))
            coroutines.append(blink(canvas, row, column, choice('+*.:')))

            coroutine_count -= 1

    return coroutines


async def animate_spaceship(canvas, row, column, spaceship_frames):
    canvas.nodelay(True)

    old_frame = ''
    for frame in cycle(spaceship_frames):
        draw_frame(canvas, row, column, old_frame, negative=True)
        draw_frame(canvas, row, column, frame)
        old_frame = frame
        await asyncio.sleep(0)

        rows_direction, columns_direction, space_pressed = read_controls(
            canvas)

        if rows_direction != 0 or columns_direction != 0:
            draw_frame(canvas, row, column, old_frame, negative=True)
            draw_frame(canvas, row, column, frame, negative=True)

            row += rows_direction
            column += columns_direction


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
    spaceship_frames = load_spaceship_frames()

    canvas.border()
    canvas.refresh()

    coroutines = create_coroutines(canvas, 200)
    # coroutines.append(fire(canvas, 0, 100, rows_speed=0.3))
    coroutines.append(animate_spaceship(canvas, 5, 15, spaceship_frames))

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
