import curses
import threading
import time

TICK_TIME_MS = 100

def setup(stdscr: curses.window) -> tuple[curses.window, curses.window]:
    stdscr.clear()
    stdscr.refresh()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
    curses.init_pair(5, -1, -1)

    title_win = curses.newwin(2, stdscr.getmaxyx()[1], 0, 0)
    title_win.clear()
    title_win.bkgd(' ', curses.color_pair(3))
    title_win.addstr(0, stdscr.getmaxyx()[1] // 2 - 6, "Game of life", curses.color_pair(2) | curses.A_BOLD)
    title_win.addstr(1, stdscr.getmaxyx()[1] // 2 - 27, "k: toggle paintbrush | home: start simulation | q: quit", curses.color_pair(2) | curses.A_BOLD)
    title_win.refresh()

    board_win = curses.newwin(stdscr.getmaxyx()[0]-2, stdscr.getmaxyx()[1], 2, 0)
    board_win.clear()
    board_win.refresh()

    return (title_win, board_win)

def render_board(win: curses.window, board):
    win.clear()
    for i in range(len(board)):
        for j in range(len(board[i])):
            win.move(i, j)
            if(board[i][j] == 1):
                win.addch(' ', curses.color_pair(4))
    win.refresh()

def count_nbors(board: list[list[int]], y: int, x: int):
    nbors = 0
    for i in range(-1, 2):
        if y + i < 0 or y + i >= len(board):
            continue
        for j in range(-1, 2):
            if (i == 0 and j == 0) or (x + j < 0) or (x + j >= len(board[i])):
                continue
            if(board[y+i][x+j] == 1):
                nbors += 1
    return nbors

def simulate(board_win: curses.window, board: list[list[int]], stop_event: threading.Event):
    while not stop_event.is_set():
        new_board = [[0 for _ in range(len(board[0]))] for _ in range(len(board))]

        for i in range(0, len(board)):
            for j in range(0, len(board[i])):
                nbors = count_nbors(board, i, j)
                if board[i][j] == 1:
                    new_board[i][j] = 1 if (nbors == 2 or nbors == 3) else 0
                else:
                    if nbors == 3:
                        new_board[i][j] = 1

        board = new_board
        render_board(board_win, board)
        time.sleep(TICK_TIME_MS/1000)

def main(stdscr: curses.window):
    title_win, board_win = setup(stdscr)    

    height, width = board_win.getmaxyx()
    cursor_y, cursor_x = 0, 0
    is_painting = False
    k = 0

    board = [[0 for _ in range(width)] for _ in range(height)]

    # input board initial state

    while k != ord('q'):
        if is_painting:
            was_alive = board[cursor_y][cursor_x] == 1
            board[cursor_y][cursor_x] = 0 if was_alive else 1
            board_win.addch(' ', curses.color_pair(5) if was_alive else curses.color_pair(4))

        match k:
            case curses.KEY_UP:
                cursor_y -= 1
            case curses.KEY_LEFT:
                cursor_x -= 1
            case curses.KEY_DOWN:
                cursor_y += 1
            case curses.KEY_RIGHT:
                cursor_x += 1
            case 107:
                is_painting = not is_painting
            case curses.KEY_HOME:
                break

        cursor_x = max(0, cursor_x)
        cursor_x = min(width - 1, cursor_x)
        cursor_y = max(0, cursor_y)
        cursor_y = min(height - 1, cursor_y)

        board_win.move(cursor_y, cursor_x)
        board_win.refresh()
        k = stdscr.getch()
    
    # start simulation

    curses.curs_set(0)
    stop_simulation_event = threading.Event()
    simulation_thread = threading.Thread(target=simulate, args=(board_win, board, stop_simulation_event))
    simulation_thread.start()

    while(k != ord('q')):
        k = stdscr.getch()

    stop_simulation_event.set()

curses.wrapper(main)
