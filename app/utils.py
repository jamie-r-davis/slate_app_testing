def col_to_a1(col: int) -> str:
    """
    Formats a numeric column index to its A1 notation equivalent.

    For example:
    > col_to_a1(1)
    'A'
    > col_to_a1(27)
    'AA'

    Parameters
    ----------
    col : int
        A numeric column index (starting at 1).

    Returns
    -------
    str
    """
    div = int(col)
    col_label = ""

    while div:
        (div, mod) = divmod(div, 26)
        if mod == 0:
            mod = 26
            div -= 1
        col_label = chr(mod + 64) + col_label

    return col_label
