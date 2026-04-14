$ZipFile="D:\work\python\monitor_control\color\color.zip"
$RegFile="D:\work\python\monitor_control\color\color.reg"
Compress-Archive -Path "C:\Windows\System32\spool\drivers\color\*" -DestinationPath $ZipFile -Force
reg export "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ICM" $RegFile /y
Write-Host "backup complete" -ForegroundColor Green