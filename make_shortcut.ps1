$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $DesktopPath "Jessica Mission Control.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "E:\Documents\GitHub\JESSICA\Launch_Jessica.bat"
$Shortcut.WorkingDirectory = "E:\Documents\GitHub\JESSICA"
$Shortcut.Description = "Jessica Sovereign AI Mission Control"
$Shortcut.Save()
Write-Host "Desktop shortcut created at: $ShortcutPath"

