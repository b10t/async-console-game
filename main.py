import asyncio
import curses
import glob
import logging
import os
import statistics
import time
from itertools import cycle
from random import choice, randint

from curses_tools import draw_frame, get_frame_size, read_controls

logger = logging.getLogger('async-console-game')

TIC_TIMEOUT = 0.1


def load_spaceship_frames(folder='frames'):
    spaceship_frames = []

    for frame_filename in glob.glob(os.path.join(folder, 'rocket_frame_*.txt')):
        with open(frame_filename, 'r') as frame_file:
            spaceship_frames.append(frame_file.read())

    return spaceship_frames


def create_star_sky(canvas, star_count=1):
    """Создаёт звездное небо."""
    border_size = 2
    coordinates = []
    coroutines = []

    height, width = canvas.getmaxyx()
    height, width = height - border_size, width - border_size

    while star_count:
        row = randint(1, height)
        column = randint(1, width)

        if (row, column) not in coordinates:
            offset_tics = randint(0, 20)
            coordinates.append((row, column))
            coroutines.append(
                blink(canvas, row, column, offset_tics, choice('+*.:'))
            )

            star_count -= 1

    return coroutines


async def animate_spaceship(canvas, row, column, spaceship_frames):
    border_size = 1
    height, width = canvas.getmaxyx()
    height, width = height - border_size, width - border_size

    frame_rows, frame_columns = get_frame_size(spaceship_frames[0])
    height -= frame_rows
    width -= frame_columns

    for frame in cycle(spaceship_frames):
        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)

        draw_frame(canvas, row, column, frame, negative=True)

        rows_direction, columns_direction, _ = read_controls(canvas)

        if rows_direction or columns_direction:
            row += rows_direction
            column += columns_direction

            row = max(1, row)
            column = max(1, column)

            row = min(row, height)
            column = min(column, width)


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


async def blink(canvas, row, column, offset_tics, symbol='*'):
    for _ in range(0, offset_tics):
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

    canvas.nodelay(True)
    canvas.border()

    coroutines = create_star_sky(canvas, 200)
    coroutines.append(animate_spaceship(canvas, 1, 1, spaceship_frames))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()

        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )

    curses.initscr()
    curses.curs_set(False)

    curses.update_lines_cols()
    curses.wrapper(draw)
