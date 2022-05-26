import argparse
import os
from collections.abc import Iterable
import torch
from error_handler import errorhandler

@errorhandler
def load_tensors(path):
    if os.path.isfile(path) == True:
        tensors = torch.load(path)
        return tensors
    else:
        raise ValueError("Path does not exist.")

@errorhandler
def to_dict_with_sorted_values(d, key=None):
    return {k: sorted(v, key=key) for k, v in d.items()}

@errorhandler
def to_dict_with_set_values(d):
    result = {}
    for k, v in d.items():
        hashable_v = []
        for v_elem in v:
            if isinstance(v_elem, list):
                hashable_v.append(tuple(v_elem))
            else:
                hashable_v.append(v_elem)
        result[k] = set(hashable_v)
    return result

@errorhandler
def save_tensors(tensors, path) -> str:
    if os.path.isfile(path) == True:
        torch.save(tensors, path)
        return path
    else:
        completeName = os.path.join(path)
        file1 = open(completeName, "wb")
        torch.save(tensors, file1)
        return completeName

@errorhandler
def tuplify(dictionary):
    if dictionary is None:
        return tuple()
    assert isinstance(dictionary, dict)
    def value(x): return dictionary[x]
    return tuple(key for key in sorted(dictionary, key=value))

@errorhandler
def dictify(iterable):
    assert isinstance(iterable, Iterable)
    return {v: i for i, v in enumerate(iterable)}


@errorhandler
def dash_separated_ints(value):
    vals = value.split("-")
    for val in vals:
        try:
            int(val)
        except ValueError:
            raise argparse.ArgumentTypeError(
                "%s is not a valid dash separated list of ints" % value
            )

    return value

@errorhandler
def dash_separated_floats(value):
    vals = value.split("-")
    for val in vals:
        try:
            float(val)
        except ValueError:
            raise argparse.ArgumentTypeError(
                "%s is not a valid dash separated list of floats" % value
            )

    return value
