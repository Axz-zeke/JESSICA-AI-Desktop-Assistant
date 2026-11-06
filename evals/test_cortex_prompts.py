import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch
from brain.cortex_tokenizer import CortexTokenizer
from brain.cortex_net import JessicaCortexNet

device = torch.device('cuda:0')
tok = CortexTokenizer('brain/cortex_vocab.json')
ckpt = torch.load('brain/cortex_v2.pt', map_location=device)
model = JessicaCortexNet(vocab_size=ckpt['vocab_size'], d_model=384, n_heads=8, num_layers=6, d_ff=1536, max_seq_len=128).to(device)
model.load_state_dict(ckpt['model_state_dict'])
model.eval()

# Test 4: GPU Telemetry
prompt4 = '<user> Check my RTX 4060 GPU temperature and system telemetry <context> none <action> {"gpu_temp_c": 37.0, "vram_used_mb": 428, "cpu_usage_pct": 2.1, "ram_used_gb": 11.2} <jessica>'
ids4 = tok.encode(prompt4, add_bos_eos=False)
out4 = model.generate(torch.tensor([ids4], device=device), max_new_tokens=45, temperature=0.1)
print('EVAL 4:', tok.decode(out4[0].tolist()))

# Test 5: Vault Thermals
prompt5 = '<user> What are the thermal limits in my Obsidian vault? <context> Obsidian Vault SOP Hardware Telemetry: Safe < 75C, Throttle 83C, Critical Shutdown 87C for RTX 4060 <action> none <jessica>'
ids5 = tok.encode(prompt5, add_bos_eos=False)
out5 = model.generate(torch.tensor([ids5], device=device), max_new_tokens=55, temperature=0.1)
print('EVAL 5:', tok.decode(out5[0].tolist()))

# Test 6: Internet Connection
prompt6 = '<user> Is my internet connection working? <context> none <action> {"connected": true, "ping_ms": 14.8, "target": "8.8.8.8", "status": "online"} <jessica>'
ids6 = tok.encode(prompt6, add_bos_eos=False)
out6 = model.generate(torch.tensor([ids6], device=device), max_new_tokens=45, temperature=0.1)
print('EVAL 6:', tok.decode(out6[0].tolist()))
