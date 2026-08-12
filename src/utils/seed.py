"""Global random seed configuration for reproducibility."""
import os
import random

import numpy as np
import torch

DEFAULT_SEED = int(os.environ.get("SEED", 42))


def set_seed(seed: int = DEFAULT_SEED) -> None:
    """Set random seeds for Python, NumPy, and PyTorch."""
    random.seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    os.environ["PYTHONHASHSEED"] = str(seed)
