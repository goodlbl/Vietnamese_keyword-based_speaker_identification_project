import os, torch, torchaudio
import torch.nn.functional as F
from torch import nn

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ============================================================
# 🧩 Các class model giống code train
# ============================================================

class Swish(nn.Module):
    def forward(self, x): return x * torch.sigmoid(x)

class ConvModule(nn.Module):
    def __init__(self, dim, k=15):
        super().__init__()
        self.ln = nn.LayerNorm(dim)
        self.pw1 = nn.Conv1d(dim, 2*dim, 1)
        self.dw  = nn.Conv1d(dim, dim, k, padding=k//2, groups=dim)
        self.bn  = nn.BatchNorm1d(dim)
        self.act = Swish()
        self.pw2 = nn.Conv1d(dim, dim, 1)
    def forward(self, x):
        y = self.ln(x).transpose(1,2)
        y = F.glu(self.pw1(y), dim=1)
        y = self.pw2(self.act(self.bn(self.dw(y)))).transpose(1,2)
        return x + y

class FeedForwardModule(nn.Module):
    def __init__(self, dim, exp=4, drop=0.1):
        super().__init__()
        self.ln = nn.LayerNorm(dim)
        self.ff = nn.Sequential(
            nn.Linear(dim, exp*dim), Swish(), nn.Dropout(drop),
            nn.Linear(exp*dim, dim), nn.Dropout(drop)
        )
    def forward(self, x): return x + 0.5 * self.ff(self.ln(x))

class MHSA(nn.Module):
    def __init__(self, dim, h=4, drop=0.1):
        super().__init__()
        self.ln = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, h, dropout=drop, batch_first=True)
        self.do = nn.Dropout(drop)
    def forward(self, x):
        y, _ = self.attn(self.ln(x), self.ln(x), self.ln(x))
        return x + self.do(y)

class ConformerBlock(nn.Module):
    def __init__(self, dim, h=4, k=15, exp=4, drop=0.1):
        super().__init__()
        self.ff1 = FeedForwardModule(dim, exp, drop)
        self.mhsa = MHSA(dim, h, drop)
        self.conv = ConvModule(dim, k)
        self.ff2 = FeedForwardModule(dim, exp, drop)
    def forward(self, x): return self.ff2(self.conv(self.mhsa(self.ff1(x))))

class MFAConformer(nn.Module):
    def __init__(self, n_mels=80, dim=224, L=5, h=4, k=11, agg=(2,4,5), emb_dim=192):
        super().__init__()
        self.proj = nn.Linear(n_mels, dim)
        self.blocks = nn.ModuleList([ConformerBlock(dim, h, k) for _ in range(L)])
        self.agg = set(agg)
        self.post = nn.Linear(dim*len(agg)*2, emb_dim)
        self.bn = nn.BatchNorm1d(emb_dim)
    def forward(self, x):
        x = x.transpose(1,2)
        x = self.proj(x)
        feats = []
        for i, b in enumerate(self.blocks, 1):
            x = b(x)
            if i in self.agg: feats.append(x)
        h = torch.cat(feats, -1)
        mean, std = h.mean(1), h.std(1).clamp(min=1e-6)
        out = torch.cat([mean, std], 1)
        emb = self.bn(self.post(out))
        return F.normalize(torch.nan_to_num(emb), p=2, dim=1)

# ============================================================
# 🔍 Load model + inference
# ============================================================

def load_model(ckpt_path="best_model.pt"):
    model = MFAConformer().to(DEVICE)
    ckpt = torch.load(ckpt_path, map_location=DEVICE)
    state_dict = ckpt["model"] if "model" in ckpt else ckpt
    model.load_state_dict(state_dict)
    model.eval()
    return model

@torch.no_grad()
def extract_embedding(model, audio_path):
    wav, sr = torchaudio.load(audio_path)
    wav = wav.mean(0, keepdim=True)  # mono
    wav = torchaudio.functional.resample(wav, sr, 16000)

    # mel-spectrogram
    mel_spec = torchaudio.transforms.MelSpectrogram(
        sample_rate=16000,
        n_fft=512,
        hop_length=160,
        n_mels=80
    )(wav)
    mel_spec = mel_spec.clamp(min=1e-5).log()

    # ✅ Fix: chuẩn hóa chiều dài đầu vào
    max_len = 224   # chiều mel model mong đợi
    if mel_spec.shape[-1] < max_len:
        pad = max_len - mel_spec.shape[-1]
        mel_spec = torch.nn.functional.pad(mel_spec, (0, pad))
    elif mel_spec.shape[-1] > max_len:
        mel_spec = mel_spec[:, :, :max_len]

    with torch.no_grad():
        emb = model(mel_spec.to(DEVICE)).squeeze().cpu().numpy()
    return emb


