import numpy as np
import torch
from numpy.random import choice
from pytorch_lightning import LightningDataModule
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset
from torchvision.transforms import Compose, ToTensor


class ImageDataModule(LightningDataModule):
    def __init__(self, dataset_fn, batch_size=128, num_workers=2):
        super().__init__()
        self.save_hyperparameters()
        self.dataset_fn = dataset_fn
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.transforms = Compose([ToTensor()])

    def train_dataloader(self) -> DataLoader:
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
        )

    def val_dataloader(self) -> DataLoader:
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
        )

    def test_dataloader(self) -> DataLoader:
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
        )


class MNISTDataModule(ImageDataModule):
    def __init__(self, dataset_fn, batch_size=128, num_workers=2):
        super().__init__(dataset_fn, batch_size, num_workers)

    def download_data(self) -> None:
        self.downloaded_train_dataset = self.dataset_fn(
            root="/tmp/data",
            train=True,
            transform=self.transforms,
            download=True,
        )
        self.downloaded_test_dataset = self.dataset_fn(
            root="/tmp/data",
            train=False,
            transform=self.transforms,
            download=True,
        )

    def sample_data(self, train_size, seed=None) -> None:
        # Load raw train and test datasets
        raw_train_dataset, raw_test_dataset = (
            self.downloaded_train_dataset,
            self.downloaded_test_dataset,
        )
        # Define random sample indices and train/val splits
        if seed is not None:
            np.random.seed(seed)
        self.sample_idx = choice(len(raw_train_dataset), train_size, replace=False)
        train_split_idx, val_split_idx = train_test_split(
            np.arange(len(self.sample_idx)), test_size=0.1, shuffle=True
        )
        assert len(np.intersect1d(train_split_idx, val_split_idx)) == 0
        # Convert to tensor dataset for indexing
        train_dataset_sample = TensorDataset(
            torch.unsqueeze(raw_train_dataset.data, dim=1).float() / 255.0,
            raw_train_dataset.targets,
        )[self.sample_idx]
        self.train_dataset = TensorDataset(
            train_dataset_sample[0][train_split_idx],
            train_dataset_sample[1][train_split_idx],
        )
        self.val_dataset = TensorDataset(
            train_dataset_sample[0][val_split_idx],
            train_dataset_sample[1][val_split_idx],
        )
        self.test_dataset = TensorDataset(
            torch.unsqueeze(raw_test_dataset.data, dim=1).float() / 255.0,
            raw_test_dataset.targets,
        )


class FashionMNISTDataModule(MNISTDataModule):
    """This class is exactly the same as MNISTDataModule."""


class EMNISTDataModule(MNISTDataModule):
    def __init__(self, dataset_fn, split, batch_size=128, num_workers=2):
        super().__init__(dataset_fn, batch_size, num_workers)
        self.split = split

    def download_data(self) -> None:
        self.downloaded_train_dataset = self.dataset_fn(
            root="/tmp/data",
            split=self.split,
            train=True,
            transform=self.transforms,
            download=True,
        )
        self.downloaded_test_dataset = self.dataset_fn(
            root="/tmp/data",
            split=self.split,
            train=False,
            transform=self.transforms,
            download=True,
        )
        if self.split == "letters":
            self.downloaded_train_dataset.targets -= 1
            self.downloaded_test_dataset.targets -= 1


class CIFAR10DataModule(ImageDataModule):
    def __init__(self, dataset_fn, batch_size=128, num_workers=2):
        super().__init__(dataset_fn, batch_size, num_workers)
        # self.normalize = Normalize((0.4914, 0.4822, 0.4465), (0.247, 0.2435, 0.2616))

    def download_data(self) -> None:
        self.downloaded_train_dataset = self.dataset_fn(
            root="/tmp/data",
            train=True,
            transform=self.transforms,
            download=True,
        )
        self.downloaded_test_dataset = self.dataset_fn(
            root="/tmp/data",
            train=False,
            transform=self.transforms,
            download=True,
        )

    def sample_data(self, train_size, seed=None) -> None:
        # Load raw train and test datasets
        raw_train_dataset, raw_test_dataset = (
            self.downloaded_train_dataset,
            self.downloaded_test_dataset,
        )
        # Define random sample indices and train/val splits
        if seed is not None:
            np.random.seed(seed)
        self.sample_idx = choice(len(raw_train_dataset), train_size, replace=False)
        train_split_idx, val_split_idx = train_test_split(
            np.arange(len(self.sample_idx)), test_size=0.1, shuffle=True
        )
        assert len(np.intersect1d(train_split_idx, val_split_idx)) == 0
        # Convert to tensor dataset for indexing
        train_dataset_sample = TensorDataset(
            torch.tensor(raw_train_dataset.data).permute(0, 3, 1, 2).float() / 255.0,
            torch.tensor(raw_train_dataset.targets),
        )[self.sample_idx]
        self.train_dataset = TensorDataset(
            train_dataset_sample[0][train_split_idx],
            train_dataset_sample[1][train_split_idx],
        )
        self.val_dataset = TensorDataset(
            train_dataset_sample[0][val_split_idx],
            train_dataset_sample[1][val_split_idx],
        )
        self.test_dataset = TensorDataset(
            torch.tensor(raw_test_dataset.data).permute(0, 3, 1, 2).float() / 255.0,
            torch.tensor(raw_test_dataset.targets),
        )


class CIFAR100DataModule(CIFAR10DataModule):
    """This class is exactly the same as CIFAR10DataModule."""
