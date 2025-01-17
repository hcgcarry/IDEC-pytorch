import numpy as np
from sklearn.preprocessing import LabelEncoder
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.datasets import UCR_UEA_datasets
import torch
from torch.utils.data import Dataset, DataLoader


def load_ucr(dataset, scale):
    """
    Load ucr dataset.
    Taken from https://github.com/FlorentF9/DeepTemporalClustering/blob/4f70d6b24722bd9f8331502d9cae00d35686a4d2/datasets.py#L18
    """
    X_train, y_train, X_test, y_test = UCR_UEA_datasets().load_dataset(dataset)
    X = np.concatenate((X_train, X_test))
    y = np.concatenate((y_train, y_test))
    if dataset == "HandMovementDirection":  # this one has special labels
        y = [yy[0] for yy in y]
    y = LabelEncoder().fit_transform(
        y
    )  # sometimes labels are strings or start from 1
    assert y.min() == 0  # assert labels are integers and start from 0
    # preprocess data (standardization)
  
    if scale:
        X = TimeSeriesScalerMeanVariance().fit_transform(X)

    return X, y


def load_data(dataset_name, all_ucr_datasets, scale=True):
    """
    args :
        dataset_name : a string representing the dataset name.
        all_ucr_datasets : a list of all ucr datasets present in tslearn UCR_UEA_datasets
        scale : a boolean that represents whether to scale the time series or not.
    return :
        X : time series , scaled or not.
        y : the labels ( binary in our case) . s
    """
    if dataset_name in all_ucr_datasets:
        return load_ucr(dataset_name, scale)
    else:
        print(
            "Dataset {} not available! Available datasets are UCR/UEA univariate and multivariate datasets.".format(
                dataset_name
            )
        )
        exit(0)


class CustomDataset(Dataset):
    def __init__(self, time_series, labels):
        """
        This class creates a torch dataset.

        """
        self.x=np.squeeze(time_series).astype(np.float32)
        print("self.x",self.x.shape)
        self.y= labels.astype(np.int32)
        print("self.y",self.y.shape)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):

        return torch.from_numpy(np.array(self.x[idx])), torch.from_numpy(
        np.array(self.y[idx])), torch.from_numpy(np.array(idx))


def get_loader(dataset_name,batch_size):

    ucr = UCR_UEA_datasets()
    all_ucr_datasets = ucr.list_datasets()
    X_scaled, y = load_data(dataset_name, all_ucr_datasets)
    # create dataset
    trainset = CustomDataset(X_scaled, y)

    ## create dataloader
    trainloader = DataLoader(
        trainset, batch_size=batch_size, shuffle=True, num_workers=2
    )
    return trainset, X_scaled
