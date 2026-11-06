# Project Jessica - Live QLoRA Training Terminal Monitor
$host.ui.RawUI.WindowTitle = "Project Jessica - Live QLoRA Training Monitor (PID 9248)"

Clear-Host
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "            PROJECT JESSICA - LIVE QLORA TRAINING MONITOR                 " -ForegroundColor Yellow
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "Target Model : 8.03B Llama-3.1 NF4 (Full-Linear Projections: r=16, alpha=32)" -ForegroundColor White
Write-Host "Training Mode: Target-Only Loss Masking on 2,500 Spoken Dialogue Samples   " -ForegroundColor White
Write-Host "Compute Device: NVIDIA GeForce RTX 4060 (8GB VRAM)                         " -ForegroundColor White
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host ""

$stagesFile = "E:\Documents\GitHub\JESSICA\datasets\marathon_training_stages.json"

while ($true) {
    $proc = Get-Process -Id 9248 -ErrorAction SilentlyContinue
    
    if ($proc) {
        $cpuSec = [math]::Round($proc.CPU, 1)
        $wsMb = [math]::Round($proc.WorkingSet64 / 1MB, 1)
        Write-Host "[LIVE STATUS] Python Trainer (PID 9248) ACTIVE | CPU Time: ${cpuSec}s | RAM: ${wsMb} MB" -ForegroundColor Green
    } else {
        Write-Host "[LIVE STATUS] Python Trainer Process Completed or Inactive" -ForegroundColor Magenta
    }

    if (Test-Path $stagesFile) {
        try {
            $stages = Get-Content $stagesFile -Raw | ConvertFrom-Json
            Write-Host "`n--- COMPLETED STAGES ($($stages.Count)/5) ---" -ForegroundColor Yellow
            foreach ($s in $stages) {
                Write-Host "  [STAGE $($s.stage)/5]" -ForegroundColor Cyan -NoNewline
                Write-Host " Train Loss: " -NoNewline
                Write-Host "$($s.train_loss)" -ForegroundColor White -NoNewline
                Write-Host " | Val Loss: " -NoNewline
                Write-Host "$($s.val_loss)" -ForegroundColor White -NoNewline
                Write-Host " | Val PPL: " -NoNewline
                Write-Host "$($s.val_perplexity)" -ForegroundColor Green -NoNewline
                Write-Host " | Time: " -NoNewline
                Write-Host "$([math]::Round($s.duration_seconds/60, 1))m" -ForegroundColor White
                Write-Host "    Sample: ""$($s.sample_generation)""" -ForegroundColor Gray
            }
            if ($stages.Count -lt 5 -and $proc) {
                Write-Host "`n>>> [STAGE $($stages.Count + 1)/5 IS CURRENTLY TRAINING ON GPU] <<<" -ForegroundColor Yellow
            }
        } catch {}
    }

    Write-Host "`n(Refreshing every 5 seconds... Press Ctrl+C to close monitor)" -ForegroundColor DarkGray
    Start-Sleep -Seconds 5
    Clear-Host
    Write-Host "===========================================================================" -ForegroundColor Cyan
    Write-Host "            PROJECT JESSICA - LIVE QLORA TRAINING MONITOR                 " -ForegroundColor Yellow
    Write-Host "===========================================================================" -ForegroundColor Cyan
}

