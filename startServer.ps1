Write-Output "Virtuelle Umgebung 'venv' gefunden. Aktiviere..."
& ./venv/Scripts/activate

Write-Output "Starte den Server..."
python server.py


Write-Output "Das Skript ist fertig. Drücken Sie Strg+C, um es zu beenden."
while ($true) {
    Start-Sleep -Seconds 1
}