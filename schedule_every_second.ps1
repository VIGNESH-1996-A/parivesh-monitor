# Run this once to start checking PARIVESH every second (starts when you log in).
# The monitor runs in the background and checks every 1 second for new agenda/MoM.

$taskName = "PARIVESH_EC_Monitor"
$pythonScript = "v:\PARIVESH\run_every_second.py"
$workDir = "v:\PARIVESH"

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { $python = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $python) {
    Write-Host "Python not found in PATH."
    exit 1
}

Unregister-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

# Start at logon; script runs forever and checks every second
$action = New-ScheduledTaskAction -Execute $python -Argument "`"$pythonScript`"" -WorkingDirectory $workDir
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "PARIVESH monitor - checks every 1 sec, SMS to 9940944929 when TN/KA/TS agenda or MoM updated"

Write-Host "Done. At every logon, the monitor will start and check every second."
Write-Host "To start now (without logging off): run 'python run_every_second.py' in v:\PARIVESH and leave the window open."
Write-Host "To stop: Task Scheduler -> disable or delete '$taskName'; or close the window running run_every_second.py."
