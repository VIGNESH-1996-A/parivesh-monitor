# Run this script once to schedule PARIVESH monitor every hour.
# Right-click -> Run with PowerShell (or run in PowerShell as Administrator if needed).

$taskName = "PARIVESH_EC_Monitor"
$pythonScript = "v:\PARIVESH\parivesh_monitor.py"
$workDir = "v:\PARIVESH"

# Find python.exe (same one you use for 'python' in terminal)
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) {
    $python = (Get-Command py -ErrorAction SilentlyContinue).Source
}
if (-not $python) {
    Write-Host "Python not found in PATH. Install Python or add it to PATH."
    exit 1
}

# Remove existing task if present
Unregister-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

# Run every hour: start at next full hour, repeat every 1 hour indefinitely
$action = New-ScheduledTaskAction -Execute $python -Argument "`"$pythonScript`"" -WorkingDirectory $workDir
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "PARIVESH EC Agenda/MoM monitor - SMS to 9940944929 when TN, KA, TS updated (runs every hour)"

Write-Host "Done. Task '$taskName' is scheduled to run every hour."
Write-Host "To change: Task Scheduler -> find '$taskName' -> Properties -> Triggers -> Edit."
