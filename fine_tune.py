import torch
import torch.nn as nn
import whisper

from dataset import Collator, PizzaSpeechDataset, IGNORE_TOKEN
from train import train, validate, calculate_wer


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
LR = 0.0005
BATCH_SIZE = 16
EPOCHS = 5

train_dataset = PizzaSpeechDataset(train=True, device=DEVICE)
val_dataset = PizzaSpeechDataset(train=False, device=DEVICE)

collator = Collator()
train_data_loader = torch.utils.data.DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    collate_fn=collator,
)
val_data_loader = torch.utils.data.DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    collate_fn=collator,
)

model = whisper.load_model("base.en")

loss_fn = nn.CrossEntropyLoss(ignore_index=IGNORE_TOKEN)
optimizer = torch.optim.AdamW(
    model.parameters(), lr=LR, betas=(0.9, 0.98), eps=1e-6, weight_decay=0.1
)

for i in range(EPOCHS):
    train(model, train_data_loader, loss_fn, optimizer, print_interval=10)
    validate(model, val_data_loader, loss_fn)
    val_wer = calculate_wer(model, val_data_loader)
    print(f"Epoch {i + 1} WER: {val_wer}")