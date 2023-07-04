import curses
import threading
import time
import copy

TICK_TIME_MS = 150
PAINTBRUSH_KEY = 112
QUIT_KEY = 113

def setup(stdscr: curses.window) -> tuple[curses.window, curses.window]:
    stdscr.clear()
    stdscr.refresh()
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(2)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
    curses.init_pair(5, -1, -1)

    title_win = curses.newwin(2, stdscr.getmaxyx()[1], 0, 0)
    title_win.clear()
    title_win.bkgd(' ', curses.color_pair(3))
    title_win.addstr(0, stdscr.getmaxyx()[1] // 2 - 6, "Game of life", curses.color_pair(2) | curses.A_BOLD)
    title_win.addstr(1, stdscr.getmaxyx()[1] // 2 - 27, "p: toggle paintbrush | home: start/pause simulation | q: quit", curses.color_pair(2) | curses.A_BOLD)
    title_win.refresh()

    board_win = curses.newwin(stdscr.getmaxyx()[0]-1, stdscr.getmaxyx()[1]+1, 2, 0) # hacky solution to not being able
    board_win.clear()                                                               # to print in the bot rigth corner
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

    board_copy = copy.deepcopy(board)

    while not stop_event.is_set():
        new_board = [[0 for _ in range(len(board_copy[0]))] for _ in range(len(board_copy))]

        for i in range(0, len(board_copy)):
            for j in range(0, len(board_copy[i])):
                nbors = count_nbors(board_copy, i, j)
                if board_copy[i][j] == 1:
                    new_board[i][j] = 1 if (nbors == 2 or nbors == 3) else 0
                else:
                    if nbors == 3:
                        new_board[i][j] = 1

        new_board[-1][-1] = 0 # set to zero because of curses bottom right corner bug
        board_copy = new_board
        render_board(board_win, board_copy)
        time.sleep(TICK_TIME_MS/1000)
    
    for i in range(0, len(board_copy)):
            for j in range(0, len(board_copy[i])):
                board[i][j] = board_copy[i][j]
    
def start_simulation(board_win: curses.window, board: list[list[int]]) -> tuple[threading.Thread, threading.Event]:
    stop_simulation_event = threading.Event()
    simulation_thread = threading.Thread(target=simulate, args=(board_win, board, stop_simulation_event))
    simulation_thread.start()
    return (simulation_thread, stop_simulation_event)

def stop_simulation(simulation_thread: threading.Thread, stop_simulation_event: threading.Event):
    if(stop_simulation_event):
        stop_simulation_event.set()
    if(simulation_thread):
        simulation_thread.join()
    return (None, None)

def main(stdscr: curses.window):
    title_win, board_win = setup(stdscr)    

    height, width = board_win.getmaxyx()[0]-1, board_win.getmaxyx()[1]-1
    cursor_y, cursor_x = 0, 0
    stop_simulation_event: threading.Event = None
    simulation_thread: threading.Thread = None
    is_painting, is_simulating = False, False
    key = 0

    board = [[0 for _ in range(width)] for _ in range(height)]

    while True:
        if key == curses.KEY_UP:
            cursor_y -= 1
        elif key == curses.KEY_LEFT:
            cursor_x -= 1
        elif key == curses.KEY_DOWN:
            cursor_y += 1
        elif key == curses.KEY_RIGHT:
            cursor_x += 1
        elif key == PAINTBRUSH_KEY:
            is_painting = not is_painting
        elif key == curses.KEY_HOME:
            if is_simulating:
                simulation_thread, stop_simulation_event = stop_simulation(simulation_thread, stop_simulation_event)
                is_simulating = False
                curses.curs_set(1)
            else:
                simulation_thread, stop_simulation_event = start_simulation(board_win, board)
                is_simulating = True
                curses.curs_set(0)

        elif key == QUIT_KEY:
            stop_simulation(simulation_thread, stop_simulation_event)    
            break
    
        if not is_simulating:
            cursor_x = max(0, cursor_x)
            cursor_x = min(width - 1, cursor_x)
            cursor_y = max(0, cursor_y)
            cursor_y = min(height - 1, cursor_y)

            if is_painting:
                board_win.addch(' ', curses.color_pair(4))          
                board[cursor_y][cursor_x] = 1

            board_win.move(cursor_y, cursor_x)
            board_win.refresh()
        
        key = stdscr.getch()

curses.wrapper(main)
