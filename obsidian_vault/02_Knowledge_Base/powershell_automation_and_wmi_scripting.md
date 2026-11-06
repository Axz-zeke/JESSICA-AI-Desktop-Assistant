# PowerShell Automation & WMI/CIM Systems Scripting

## Modern CIM vs Deprecated WMI
Modern PowerShell scripts should prioritize `Get-CimInstance` over legacy `Get-WmiObject` because CIM uses WS-Management (WinRM / port 5985) over firewalls instead of legacy DCOM.

## Essential Administrative Commands
```powershell
# Query physical RAM capacity and speed across all DIMM slots
Get-CimInstance Win32_PhysicalMemory | Select-Object DeviceLocator, Capacity, Speed, Manufacturer

# Extract Top 5 memory-hungry processes
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 5 Name, @{N='Memory_MB';E={[math]::Round($_.WorkingSet64/1MB,1)}}

# Test TCP port reachability
Test-NetConnection -ComputerName 1.1.1.1 -Port 443
```
