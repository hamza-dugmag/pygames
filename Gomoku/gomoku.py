# Hamza Dugmag
# Project 02 - Gomoku
# University of Toronto
# Engineering Science (ESC180)
# Updated 2020-11-17


# ======================================================================= GIVEN
def make_empty_board(sz):
    board = []
    for i in range(sz):
        board.append([" "]*sz)

    return board


def print_board(board):
    s = "*"
    for i in range(len(board[0]) - 1):
        s += str(i % 10) + "|"

    s += str((len(board[0]) - 1) % 10)
    s += "*\n"

    for i in range(len(board)):
        s += str(i % 10)
        for j in range(len(board[0]) - 1):
            s += str(board[i][j]) + "|"

        s += str(board[i][len(board[0]) - 1])
        s += "*\n"

    s += (len(board[0])*2 + 1) * "*"
    print(s)


def score(board):
    MAX_SCORE = 100000

    open_b = {}
    semi_open_b = {}
    open_w = {}
    semi_open_w = {}

    for i in range(2, 6):
        open_b[i], semi_open_b[i] = detect_rows(board, "b", i)
        open_w[i], semi_open_w[i] = detect_rows(board, "w", i)

    if open_b[5] >= 1 or semi_open_b[5] >= 1:
        return MAX_SCORE

    elif open_w[5] >= 1 or semi_open_w[5] >= 1:
        return -MAX_SCORE

    return (-10000*(open_w[4] + semi_open_w[4]) +
            500*open_b[4] +
            50*semi_open_b[4] +
            -100*open_w[3] +
            -30*semi_open_w[3] +
            50*open_b[3] +
            10*semi_open_b[3] +
            open_b[2] + semi_open_b[2] - open_w[2] - semi_open_w[2])


def analysis(board):
    for c, full_name in [["b", "Black"], ["w", "White"]]:
        print("%s stones" % (full_name))

        for i in range(2, 6):
            open, semi_open = detect_rows(board, c, i)
            print("Open rows of length %d: %d" % (i, open))
            print("Semi-open rows of length %d: %d" % (i, semi_open))


def put_seq_on_board(board, y, x, d_y, d_x, length, col):
    for i in range(length):
        board[y][x] = col
        y += d_y
        x += d_x


def play_gomoku(board_size):
    board = make_empty_board(board_size)
    board_height = len(board)
    board_width = len(board[0])

    while True:
        print_board(board)
        if is_empty(board):
            move_y = board_height // 2
            move_x = board_width // 2
        else:
            move_y, move_x = search_max(board)

        print("Computer move: (%d, %d)" % (move_y, move_x))
        board[move_y][move_x] = "b"
        print_board(board)
        analysis(board)

        game_res = is_win(board)
        if game_res in ["White won", "Black won", "Draw"]:
            return game_res

        print("Your move:")
        move_y = int(input("y coord: "))
        move_x = int(input("x coord: "))
        board[move_y][move_x] = "w"
        print_board(board)
        analysis(board)

        game_res = is_win(board)
        if game_res in ["White won", "Black won", "Draw"]:
            return game_res


# =================================================================== COMPLETED
def is_empty(board):
    """Check if the board does not contain any pieces"""

    # Check if any spot is not empty
    for row in board:
        for column in row:
            if column != " ":
                return False

    return True


def is_bounded(board, y_end, x_end, length, d_y, d_x):
    """Determine if a sequence is closed, semi-open, or open"""

    # Construct sequence
    sequence = []
    for i in range(length-1, -1, -1):
        sequence.append([y_end - d_y*i, x_end - d_x*i])

    open_spots = 2  # Currently open

    # Check if placing in the previous spot is valid
    first = sequence[0]
    prev = [first[0] - d_y, first[1] - d_x]

    if prev[0] not in range(0, len(board)) or prev[1] not in range(0, len(board)):
        open_spots -= 1
    elif board[prev[0]][prev[1]] != " ":
        open_spots -= 1

    # Check if placing in the next spot is valid
    last = sequence[-1]
    next = [last[0] + d_y, last[1] + d_x]

    if next[0] not in range(0, len(board)) or next[1] not in range(0, len(board)):
        open_spots -= 1
    elif board[next[0]][next[1]] != " ":
        open_spots -= 1

    return ["CLOSED", "SEMIOPEN", "OPEN"][open_spots]


def get_sequences(board, col, y_start, x_start, length, d_y, d_x):
    """Generate all sequences of a certain length"""

    sequences = []
    s = []

    for i in range(len(board)):
        # Get the next square
        square = [y_start + i*d_y, x_start + i*d_x]

        try:
            # Get the color of this square
            current_col = board[square[0]][square[1]]
        except IndexError:
            # The current square is not a valid location on the board
            if s not in sequences:
                sequences.append(s)
            break

        # Extend the sequence if it matches the desired color
        if current_col == col:
            s.append(square)
        else:
            if s not in sequences:
                sequences.append(s)
            s = []

    # Append the final sequence in case checks were not conducted
    if s not in sequences:
        sequences.append(s)

    # Truncate sequences that extend into invalid squares
    for i in range(len(sequences)):
        if sequences[i] == []:
            continue

        # Verify that all the coordinates are positive
        for j in range(len(sequences[i])):
            if sequences[i][j][0] < 0 or sequences[i][j][1] < 0:
                sequences[i] = sequences[i][:j]
                break

    return sequences


def detect_row(board, col, y_start, x_start, length, d_y, d_x):
    """Determine the boundedness of a sequence along a certain row"""

    # Initial count
    seqs = get_sequences(board, col, y_start, x_start, length, d_y, d_x)
    open_seq_count = 0
    semi_open_seq_count = 0

    for seq in seqs:
        # Filter out sequences not of the desired length
        if len(seq) != length:
            continue

        # Update count
        analysis = is_bounded(board, seq[-1][0], seq[-1][1], length, d_y, d_x)

        if analysis == "OPEN":
            open_seq_count += 1

        elif analysis == "SEMIOPEN":
            semi_open_seq_count += 1

    return open_seq_count, semi_open_seq_count


def detect_rows(board, col, length):
    """Determine the boundedness of all sequences along all rows"""

    open_seq_count = 0
    semi_open_seq_count = 0

    for i in range(len(board)):
        # Horizontally
        d_y, d_x = 0, 1
        open, semi = detect_row(board, col, i, 0, length, d_y, d_x)
        open_seq_count += open
        semi_open_seq_count += semi

        # Top left to bottom right: bottom triangle
        d_y, d_x = 1, 1
        open, semi = detect_row(board, col, i, 0, length, d_y, d_x)
        open_seq_count += open
        semi_open_seq_count += semi

        # Top left to bottom right: top triangle
        d_y, d_x = 1, 1
        open, semi = detect_row(board, col, 0, i+1, length, d_y, d_x)
        open_seq_count += open
        semi_open_seq_count += semi

        # Vertically
        d_y, d_x = 1, 0
        open, semi = detect_row(board, col, 0, i, length, d_y, d_x)
        open_seq_count += open
        semi_open_seq_count += semi

        # Top right to bottom left: bottom triangle
        d_y, d_x = 1, -1
        open, semi = detect_row(board, col, i, len(board)-1, length, d_y, d_x)
        open_seq_count += open
        semi_open_seq_count += semi

        # Top right to bottom left: top triangle
        d_y, d_x = 1, -1
        open, semi = detect_row(board, col, 0, len(board)-i-2, length, d_y, d_x)
        open_seq_count += open
        semi_open_seq_count += semi

    return open_seq_count, semi_open_seq_count


def copy_board(board):
    """Deep copy the board"""

    copy = []
    for y in board:
        row = []
        for x in y:
            row.append(x)
        copy.append(row)

    return copy


def search_max(board):
    """Identify the best next move for the AI"""

    max_points = None
    move_y, move_x = None, None

    # Check the score at each non-empty square
    for y in range(len(board)):
        for x in range(len(board[0])):

            # Create a temporary board to check the score
            if board[y][x] == " ":
                copy = copy_board(board)
                copy[y][x] = "b"
                points = score(copy)

                # Set the current score if greater than the tentative maximum
                if max_points is None or points > max_points:
                    max_points = points
                    move_y, move_x = y, x

    return move_y, move_x


def detect_win(board, col, y_start, x_start, d_y, d_x):
    """Determine if a player won along a certain row"""

    # Ignore invalid starting points
    if y_start < 0 or x_start < 0:
        return False

    # Look for sequences of exactly 5
    seqs = get_sequences(board, col, y_start, x_start, 5, d_y, d_x)
    for seq in seqs:
        if len(seq) == 5:
            return True

    return False


def col_win(board, col):
    """Check if a certain color won on the board"""

    for i in range(len(board)):
        # Horizontally
        d_y, d_x = 0, 1
        if detect_win(board, col, i, 0, d_y, d_x):
            return True

        # Top left to bottom right: bottom triangle
        d_y, d_x = 1, 1
        if detect_win(board, col, i, 0, d_y, d_x):
            return True

        # Top left to bottom right: top triangle
        d_y, d_x = 1, 1
        if detect_win(board, col, 0, i+1, d_y, d_x):
            return True

        # Vertically
        d_y, d_x = 1, 0
        if detect_win(board, col, 0, i, d_y, d_x):
            return True

        # Top right to bottom left: bottom triangle
        d_y, d_x = 1, -1
        if detect_win(board, col, i, len(board)-1, d_y, d_x):
            return True

        # Top right to bottom left: top triangle
        d_y, d_x = 1, -1
        if detect_win(board, col, 0, len(board)-i-2, d_y, d_x):
            return True

    return False


def is_win(board):
    """Determine the state of the current board"""

    # White wins
    if col_win(board, "w"):
        return "White won"

    # Black wins
    if col_win(board, "b"):
        return "Black won"

    # Continue playing if there are still empty squares
    for y in board:
        if " " in y:
            return "Continue playing"

    # Otherwise, tie
    return "Draw"


# ===================================================================== TESTING
if __name__ == "__main__":
    print(play_gomoku(8))
