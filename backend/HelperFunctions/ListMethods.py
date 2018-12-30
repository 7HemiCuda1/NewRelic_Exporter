def remove_clones(lst):
    """(list) -> list
    Returns a new list with no clones succeeding any element
    >>> remove_clones([1,1,1])
    [1]
    >>> remove_clones([2,3,4,4,3])
    [2,3,4,3]
    """
    ret_lst = [lst[0]]
    for i in range(1, len(lst)):
        prev = lst[i - 1]
        cur = lst[i]
        if prev != cur:
            ret_lst += [cur]
    return ret_lst


def find_sequence_indices(lst, sequence):
    """(list, list) -> list
    Returns a list of indices where sequence appears in lst
    >>> find_sequence_indices([1,1,1], [1,1])
    [0, 1]
    >>> find_sequence_indices([2,3,4,4,3], [3,4])
    [1]
    """
    ret_lst = []
    for i in range(0, len(lst) - len(sequence) + 1):
        window = lst[i: (i + len(sequence))]
        if window == sequence:
            ret_lst += [i]
    return ret_lst


def replace_sequence(lst, old_sequence, new_sequence):
    """(list, list) -> list

    Replaces all occurrences of old_sequence in lst with new_sequence

    >>> lst = [1,2,2,3,2,2,4,2,2,5]
    >>> replace_sequence(lst, [2,2], [2])
    [1, 2, 3, 2, 4, 2, 5]
    >>> replace_sequence(lst, [1, 2], [3,4])
    [3, 4, 2, 3, 2, 2, 4, 2, 2, 5]
    >>> replace_sequence(lst, [7], [3])
    [1, 2, 2, 3, 2, 2, 4, 2, 2, 5]
    """
    appearances = find_sequence_indices(lst, old_sequence)
    if appearances == []:
        return lst

    app_tups = [(appearance, appearance + len(old_sequence)) \
                for appearance in appearances]

    ret_lst = []
    i = 0
    for tup in app_tups:
        ret_lst += lst[i:tup[0]]
        ret_lst += new_sequence
        i = tup[1]
    ret_lst += lst[i:]

    return ret_lst


def make_collapsed_range(lst):
    """([str of int or int]) -> str

    Makes a collapsed range of numbers. See below for more details

    >>> lst = [1, 2, 3, 4, 7, 8, 9]
    >>> collapsed_range = make_collapsed_range(lst)
    >>> collapsed_range
    1-4, 7-9

    """
    joiner = ", "
    if len(lst) > 0:
        lst = sorted([int(x) for x in lst])
        interval_lst = []
        lst_to_add = []
        last_val_seen = lst[0] - 1
        for num in lst:
            if num == last_val_seen + 1:
                lst_to_add += [num]
            else:
                interval_lst += [lst_to_add]
                lst_to_add = [num]
            last_val_seen = num
        interval_lst += [lst_to_add]
        intervals = []
        for interval in interval_lst:
            if len(interval) > 2:
                str_to_add = "{first}-{last}".format(first=interval[0],
                                                     last=interval[-1])
            else:
                str_to_add = joiner.join([str(x) for x in interval])
            intervals += [str_to_add]

        return joiner.join(intervals)
    else:
        return ""
