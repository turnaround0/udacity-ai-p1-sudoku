assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s + t for s in A for t in B]

def collect(A, B):
    return list(map(lambda x: x[0] + x[1], zip(A, B)))

rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diag_units = [collect(rows, cols), collect(rows, cols[::-1])]
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[])) - set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Remove digits of twins on other boxes in a unit.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    # Find all twin boxes and make set of tuple with same value
    doubles = [box for box in values if len(values[box]) == 2]
    twins = {tuple(sorted([s, t])) for s in doubles for t in doubles if s != t and values[s] == values[t]}

    # Store twin values before applying this strategy,
    # because box values of the twins can be changed due to this strategy
    twin_digits = dict()
    for twin in twins:
        twin_digits[twin[0]] = values[twin[0]]

    # For each unit, apply the naked twins strategy
    for unit in unitlist:
        for twin in twins:
            if twin[0] in unit and twin[1] in unit:
                digits = twin_digits[twin[0]]
                for box in unit:
                    # remove digits of twins on other boxes in same unit
                    if values[box] != digits and box not in twins:
                        assign_value(values, box, values[box].replace(digits[0], '').replace(digits[1], ''))
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    # '.' means empty cell, so '.' should be converted to '123456789'.
    return dict(zip(boxes, [value.replace('.', '123456789') for value in grid]))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    if values:
        width = 1 + max(len(values[s]) for s in boxes)
        line = '+'.join(['-' * (width * 3)] * 3)
        # print column line after 3 and 6, and row line after C and F.
        for r in rows:
            print(''.join(values[r + c].center(width) + ('|' if c in '36' else '') for c in cols))
            if r in 'CF':
                print(line)

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    # Find box with only one digit
    singles = [box for box in values.keys() if len(values[box]) == 1]

    # Remove the digit of single box on all its peers.
    for box in singles:
        for peer in peers[box]:
            if values[box] in values[peer]:
                assign_value(values, peer, values[peer].replace(values[box], ''))
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            digit_box = [box for box in unit if digit in values[box]]
            # If the digit exists on only ne box, the digit is assigned to the box.
            if len(digit_box) == 1:
                assign_value(values, digit_box[0], digit)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate(), only_choice(), and naked_twins().
    If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.

    Args:
        values: A sudoku in dictionary form.
    Returns:
        The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])

        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Using depth-first search and propagation, try all possible values.

    Args:
        values: A sudoku in dictionary form.
    Returns:
        The resulting sudoku in dictionary form. False if no solution exists.
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[box]) == 1 for box in values):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    _, box = min((len(values[box]), box) for box in boxes if len(values[box]) > 1)

    # Now use recursion to solve each one of the resulting sudokus,
    # and if one returns a value (not False), return that answer!
    for digit in values[box]:
        new_values = values.copy()
        assign_value(new_values, box, digit)
        new_values = search(new_values)
        if new_values:
            return new_values

    return False

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # Convert grid to a sudoku in dictionary form, and search the solution of the sudoku
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
