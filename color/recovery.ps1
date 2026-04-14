$ZipFile="D:\work\python\monitor_control\color\color.zip"
$RegFile="D:\work\python\monitor_control\color\color.reg"
takeown /f "C:\Windows\System32\spool\drivers\color\*" /a
icacls "C:\Windows\System32\spool\drivers\color\*" /grant administrators:F
Expand-Archive -Path $ZipFile -DestinationPath C:\Windows\System32\spool\drivers\ -Force
reg import $RegFile
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ICM" -Name "DoReload" -Value 1 -Type DWORD
Stop-Service Wcmsvc -Force
Restart-Service Wcmsvc
while ((Get-Service -Name Wcmsvc).Status -ne 'Running') {
    Start-Sleep -Seconds 1
}
Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ICM" -Name "DoReload" -Force
Write-Host "recovery complete" -ForegroundColor Green
