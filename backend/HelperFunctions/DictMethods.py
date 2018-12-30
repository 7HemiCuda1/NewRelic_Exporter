# Change the default encoding to utf8 (I don't know why this works) - NO REMOVE
import sys

reload(sys)
sys.setdefaultencoding("utf8")


def add_to_dict_lst(dct, key, item):
    """(dict(Hashable Object: [Object]), Hashable Object, Object) -> None

    Inserts item into the list located at dct[key]. If key does not exist in
    dct's keys, the function will begin a new list equivalent to [item] at
    dct[key].

    :param dct: the dct item will be inserted into
    :param key: the key item will be inserted at
    :param item: the item to insert into the list at dct[key]
    :return: Nothing
    """
    if key not in dct:
        dct[key] = [item]
    else:
        dct[key] += [item]


def add_to_dict_num(dct, key, amt):
    """(dict(Hashable Object: Number), Hashable Object, Number) -> None

    Increments the value at dct[key] by amt. If key does not exist in dct,
    dct[key] will be set to 1.

    :param dct: the dictionary to modify
    :param key: the key we want to increment the value at
    :param amt: the amount we want to increment dct[key] by
    :return: Nothing
    """

    if key not in dct:
        dct[key] = 1
    else:
        dct[key] += amt


def raw_var_dict_str(dct):
    """(dict(str:str)) -> str

    Returns a string in the following format, where A1,A2... are keys of dct
    and dct[A1, A2, ...] = B1, B2... :
        A1 = B1
        A2 = B2
        .
        .
        .

    :param dct: the dct we want to convert into a string
    :return:
    """
    lst = []
    for key in sorted(dct):
        lst += ["{k} = {value}".format(k=str(key), value=dct[key])]
    return "\n".join(lst)


def table_varname_val_str(dct):
    """ (dct(str(k1):dict(str(k2):str(k3)))) -> str

    Returns a string in the style of:
    k1
        k2 = k3
    k1a
        k2a = k3a

    >>> dct = {1:{2:3}}
    >>> print table_varname_val_str(dct)
    1
        2 = 3
    """
    tab = " " * 4
    str_arr = []
    for k1 in dct:
        str_arr += ["{title}:".format(title=k1)]
        for k2 in dct[k1]:
            str_to_add = "{tb}{var_name} = {var_val}"
            str_arr += [str_to_add.format(tb=tab,
                                          var_name=k2,
                                          var_val=dct[k1][k2])]
    return "\n".join(str_arr)


def table_varname_str(dct):
    """ (dct(str(k1):str(k2))) -> str
    Returns a string in the style of:
    k1
        k2
    k1a
        k2a

    >>> dct = {1:2}
    >>> print table_varname_str(dct)
    1
        2
    """
    tab = " " * 4
    str_arr = []
    for k1 in dct:
        str_arr += ["{title}:".format(title=k1)]
        for k2 in dct[k1]:
            str_to_add = "{tb}{var_name}"
            str_arr += [str_to_add.format(tb=tab,
                                          var_name=k2)]
    return "\n".join(str_arr)


def dictionary_difference(d1, d2):
    """(dict, dict) -> lst

    Returns a list of keys that are "new" to d2 or whose values in d2 are
    different from those in d1

    """
    keys1 = set(d1)
    keys2 = set(d2)

    new_keys = list(keys2.difference(keys1))
    same_keys = list(keys1.intersection(keys2))

    different_keys = []
    for key in same_keys:
        if d1[key] != d2[key]:
            different_keys += [key]
    return sorted(different_keys + new_keys)


def pseudo_hash(dct, dct_val_type):
    """(dict(Hashable Object : Hashable Object or Iterable(Hashable Object),
    Object) -> int

    Returns a unique hash-code for dct.
    Warning: hacky

    :param dct: the dictionary we want to hash
    :param dct_val_type: the type of values in dct
    :return: a hash code for dct
    """
    items_to_hash = dct.items()
    if dct_val_type == list:
        temp = []
        for tup in items_to_hash:
            temp += [(tup[0], tuple(tup[1]))]
        items_to_hash = temp
    return hash(frozenset(items_to_hash))
