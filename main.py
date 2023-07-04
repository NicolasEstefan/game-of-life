import curses


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
    title_win.addstr(1, stdscr.getmaxyx()[1] // 2 - 25, "Enter: toggle cel | Home: start simulation | q: quit", curses.color_pair(2) | curses.A_BOLD)
    title_win.refresh()

    board_win = curses.newwin(stdscr.getmaxyx()[0]-2, stdscr.getmaxyx()[1], 2, 0)
    board_win.clear()
    board_win.refresh()

    return (title_win, board_win)

def render_board(win: curses.window, board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            win.move(i, j)
            if(board[i][j] == 1):
                win.addch(' ', curses.color_pair(4))
    win.refresh()

def main(stdscr: curses.window):
    title_win, board_win = setup(stdscr)    

    height, width = board_win.getmaxyx()
    cursor_y, cursor_x = 0, 0
    k = 0

    board = [[0 for _ in range(width)] for _ in range(height)]

    while k != ord('q'):
        match k:
            case curses.KEY_UP:
                cursor_y -= 1
            case curses.KEY_LEFT:
                cursor_x -= 1
            case curses.KEY_DOWN:
                cursor_y += 1
            case curses.KEY_RIGHT:
                cursor_x += 1
            case curses.KEY_ENTER | 10:
                was_alive = board[cursor_y][cursor_x] == 1
                board[cursor_y][cursor_x] = 0 if was_alive else 1
                board_win.addch(' ', curses.color_pair(5) if was_alive else curses.color_pair(4))

        cursor_x = max(0, cursor_x)
        cursor_x = min(width - 1, cursor_x)
        cursor_y = max(0, cursor_y)
        cursor_y = min(height - 1, cursor_y)

        board_win.move(cursor_y, cursor_x)
        board_win.refresh()
        k = stdscr.getch()

curses.wrapper(main)
