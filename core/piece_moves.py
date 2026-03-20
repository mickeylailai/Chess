KNIGHT_MOVES = [
    (-2,1),
    (-2,-1),
    (2,1),
    (2,-1),
    (-1,2),
    (-1,-2),
    (1,2),
    (1,-2)
]

ORTHOGONAL_MOVES = [
    (1,0),
    (-1,0),
    (0,1),
    (0,-1)
]

DIAGONAL_MOVES = [
    (1,1),
    (1,-1),
    (-1,1),
    (-1,-1)
]

QUEEN_MOVES = DIAGONAL_MOVES + ORTHOGONAL_MOVES

KING_MOVES = [
    (0,1),
    (0,-1),
    (1,1),
    (1,-1),
    (-1,0),
    (1,0),
    (-1,-1),
    (-1,1)
]