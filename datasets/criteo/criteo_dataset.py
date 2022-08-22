from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
# pytorch
import torch
from torch.utils.data import Dataset


class CriteoDataset(Dataset):
    """
    Criteo data set is an online advertising dataset released
    by Criteo Labs. Link to dataset - 'link<https://figshare.com/
    articles/dataset/Kaggle_Display_Advertising_Challenge_dataset
    /5732310>'__

    Attributes
    ----------
    Dataset  : The dataset to be loaded
    X_int: int
         An array in the integer form
    X_cat: int
         its an array storing some tensor value
    y:int
         its an array storing some values
    max_ind_range: int
         for defining the maximum range of indices

    """

    def __init__(
            self,
            X_int, X_cat, y,
            max_ind_range):
        self.max_ind_range = max_ind_range
        self.X_int = X_int
        self.X_cat = X_cat
        self.y = y

    def __getitem__(self, index):
        """
        allows its instances to use the [] (indexer) operators

        Arguments
        ---------
        index- int
             takes the index as input

        """

        if isinstance(index, slice):
            return [
                self[idx] for idx in range(
                    index.start or 0, index.stop or len(self), index.step or 1
                )
            ]

        if self.max_ind_range > 0:
            return (
                self.X_int[index],
                self.X_cat[index] % self.max_ind_range,
                self.y[index]
            )
        else:
            return self.X_int[index], self.X_cat[index], self.y[index]

    def _default_preprocess(self, X_int, X_cat, y):
        """
        It implements the default preprocesses

        Arguments
        ---------
        X_int:tensor
              integer variable
        X_cat:tensor
              categorical variable
        y:tensor

        Returns
        -------
        the integer variable and the categorical variable.
        """
        X_int = torch.log(torch.tensor(X_int, dtype=torch.float) + 1)
        if self.max_ind_range > 0:
            X_cat = torch.tensor(X_cat % self.max_ind_range, dtype=torch.long)
        else:
            X_cat = torch.tensor(X_cat, dtype=torch.long)
        y = torch.tensor(y.astype(np.float32))

        return X_int, X_cat, y

    def __len__(self):
        return len(self.y)


def collate_wrapper_criteo_offset(list_of_tuples):
    """
    In this function each tuple is (X, lS_o, lS_i, T),
    it collects and combines the bias_value(offset)
    which will be used during model training.

    Arguments
    ---------
    list_of_tuples: list
        returns tuples where each tuple is (X_int, X_cat, y)

    """
    # where each tuple is (X_int, X_cat, y)
    transposed_data = list(zip(*list_of_tuples))
    X_int = torch.log(torch.tensor(transposed_data[0], dtype=torch.float) + 1)
    X_cat = torch.tensor(transposed_data[1], dtype=torch.long)
    T = torch.tensor(transposed_data[2], dtype=torch.float32).view(-1, 1)

    batchSize = X_cat.shape[0]
    featureCnt = X_cat.shape[1]

    lS_i = [X_cat[:, i] for i in range(featureCnt)]
    lS_o = [torch.tensor(range(batchSize)) for _ in range(featureCnt)]

    return (X_int, torch.stack(lS_o), torch.stack(lS_i)), T

# Conversion from offset to length


def offset_to_length_converter(lS_o, lS_i):
    """
    This function converts the bias_value(offset) to length converter

    Arguments
    ---------
    lS_o: tuple

    lS_i: tuple

    Returns
    ------
    Concatenates a sequence of tensors along a new dimension.
    """
    def diff(tensor):
        return tensor[1:] - tensor[:-1]

    return torch.stack(
        [
            diff(torch.cat((S_o, torch.tensor(lS_i[ind].shape))).int())
            for ind, S_o in enumerate(lS_o)
        ]
    )


def collate_wrapper_criteo_length(list_of_tuples):
    """
    This function collects and joins two tuples together,
    creates a multi-dimensional matrix containing elements
    of a single data type returns a new tensor with
    the same data as the self tensor but of a different shape.

    Arguments
    ----------
    list_of_tuples :list
          the list values of tuple

    Returns
    -------
    computes the categorical feature in the range of
    feature count.
    """
    # where each tuple is (X_int, X_cat, y)
    transposed_data = list(zip(*list_of_tuples))
    X_int = torch.log(torch.tensor(transposed_data[0], dtype=torch.float) + 1)
    X_cat = torch.tensor(transposed_data[1], dtype=torch.long)
    T = torch.tensor(transposed_data[2], dtype=torch.float32).view(-1, 1)

    batchSize = X_cat.shape[0]
    featureCnt = X_cat.shape[1]

    lS_i = torch.stack([X_cat[:, i] for i in range(featureCnt)])
    lS_o = torch.stack(
        [torch.tensor(range(batchSize)) for _ in range(featureCnt)]
    )

    lS_l = offset_to_length_converter(lS_o, lS_i)
    return (X_int, lS_l, lS_i), T


def make_criteo_data_and_loaders(args, offset_to_length_converter=False):
    """
    Arguments
    ----------
    args: takes the arguments
    offset_to_length_converter: boolean
           initial value has been taken false

    Returns
    -------
    the train data,test data,train loader and test loader
    """
    train_data = CriteoDataset(
        args.data_set,
        args.max_ind_range,
        args.data_sub_sample_rate,
        args.data_randomize,
        "train",
        args.raw_data_file,
        args.processed_data_file
    )

    test_data = CriteoDataset(
        args.data_set,
        args.max_ind_range,
        args.data_sub_sample_rate,
        args.data_randomize,
        "test",
        args.raw_data_file,
        args.processed_data_file
    )

    collate_wrapper_criteo = collate_wrapper_criteo_offset
    if offset_to_length_converter:
        collate_wrapper_criteo = collate_wrapper_criteo_length

    train_loader = torch.utils.data.DataLoader(
        train_data,
        batch_size=args.mini_batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_wrapper_criteo,
        pin_memory=False,
        drop_last=False,  # True
    )

    test_loader = torch.utils.data.DataLoader(
        test_data,
        batch_size=args.test_mini_batch_size,
        shuffle=False,
        num_workers=args.test_num_workers,
        collate_fn=collate_wrapper_criteo,
        pin_memory=False,
        drop_last=False,  # True
    )

    return train_data, train_loader, test_data, test_loader
