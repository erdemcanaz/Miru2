import torch

if torch.cuda.is_available():
    device = torch.device("cuda")
    print("PyTorch is using CUDA.")
else:
    device = torch.device("cpu")
    print("PyTorch is using CPU.")