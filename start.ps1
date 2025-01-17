
if (Test-Path -Path "./venv") {
    Write-Output "Virtuelle Umgebung 'venv' gefunden. Aktiviere..."
    
    & ./venv/Scripts/activate
} else {
    Write-Output "Virtuelle Umgebung 'venv' nicht gefunden. Erstelle..."
    
    python -m venv venv
  
    & ./venv/Scripts/activate
}
Write-Output "Installiere Abhängigkeiten aus requirements.txt..."
pip install -r requirements.txt

Write-Output "Starte startServer.ps1 in einer neuen Konsole..."
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", ".\startServer.ps1"

Write-Output "Starte startclient.ps1 in einer neuen Konsole..."
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", ".\startclient.ps1"

Write-Output "Wechsle in den Ordner 'opcuaDash'..."
Set-Location -Path "./opcuaDash"


Write-Output "Starte den Django-Server..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "manage.py runserver"




Write-Output "Das Skript ist fertig. Drücken Sie Strg+C, um es zu beenden."
while ($true) {
    Start-Sleep -Seconds 1
}
