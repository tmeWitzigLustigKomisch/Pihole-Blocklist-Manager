# 🛡️ Pi-hole Blocklist Manager v2.2

Ein vollautomatisches, AES-verschlüsseltes Python-Tool mit grafischer Oberfläche (GUI) zur Verwaltung, Zusammenführung und automatischen Verteilung von Pi-hole Blocklisten.

## 🛑 Das Problem: Verschwindende Blocklisten-Einträge
Das Standardverhalten von Pi-hole ist darauf ausgelegt, die Filterdatenbank (`gravity.db`) bei jedem Update-Vorgang (`pihole -g`) komplett neu aufzubauen. 
Wenn Pi-hole dabei auf eine Blocklisten-URL stößt, die nicht mehr erreichbar ist (z. B. Server offline, Projekt eingestellt), schlägt der Download fehl. Pi-hole stuft diese Liste in diesem Moment als leer ein.
**Die Folge:** Alle Domains, die durch diese Liste zuvor blockiert wurden, werden beim Neubau unbemerkt aus der Datenbank entfernt. Ehemalige Schutzfilter fallen unwiderruflich weg!

## 🚧 Work in Progress, Kompatibilität & Bekannte Fehler
Bitte beachte: Dieses Programm befindet sich noch in der aktiven Entwicklung (**Work in Progress**).
* **Getestetes System:** Das Skript wurde aktuell ausschließlich unter **Linux Mint 22.3** getestet. Auf anderen Systemen kann es zu Abweichungen kommen.
* **Bekannter Fehler:** Aktuell gibt es noch **Sortierfehler** beim Zusammenführen der verschiedenen Listen. Die Einträge in der Master-Liste werden dadurch stellenweise nicht zu 100 % perfekt alphabetisch geordnet. Daran wird in zukünftigen Updates gearbeitet. 
* **Ladezeiten:** Das Generieren und Zusammenführen der großen Listen dauert aktuell **unglaublich lange**. Da es währenddessen kaum Rückmeldungen im GUI gibt, scheint das Skript manchmal zu hängen. Bitte habe etwas Geduld! Eine verbesserte Status-Rückmeldung ist für kommende Updates geplant.
* *Wichtig:* Die grundlegende Funktionalität und das Blocken der Domains im Pi-hole werden durch die Sortierung oder die Ladezeit **nicht beeinträchtigt**!

## 💡 Die Lösung: Die Offline-Master-Liste
Dieses Skript (`Pihole_blocklistmanager_v2.2.py`) löst genau dieses Problem. Es fungiert als intelligenter Aggregator:
1. Es lädt alle favorisierten externen Listen herunter (z.B. aus der Datei `Pihole_Quell_Links.txt`).
2. Es bereinigt sie (entfernt Duplikate, Kommentare und ungültige Präfixe wie `127.0.0.1` oder `::`).
3. Es fügt sie mit deinen bestehenden, lokal gesicherten Listen (z.B. der 2,5 GB Liste) zu einer gigantischen Master-Blockliste zusammen.
4. Diese fertige Master-Liste wird via SFTP auf einen lokalen Webserver geladen. Dem Pi-hole wird nur noch diese eine, lokale URL übergeben. Selbst wenn Listen im Internet verschwinden, bleiben die Domains dauerhaft erhalten!

## ✨ Features im Detail
Das Skript ist extrem mächtig und bietet folgende, tief ineinandergreifende Funktionen:

* **🔒 Eingebauter Passwort-Tresor (Self-Modifying Code):** Eines der Hauptmerkmale. Das Skript speichert alle eingegebenen SSH-Zugangsdaten (Hosts, User, Passwörter, Pfade) sowie die konfigurierten Quell-Links nicht in einer unsicheren externen Config-Datei, sondern modifiziert seinen eigenen Python-Quellcode. Die Daten werden mit AES-256 (Fernet) verschlüsselt und sicher in den Variablen `__ENCRYPTED_PAYLOAD__`, `__PAYLOAD_SALT__` und `__PLAINTEXT_LINKS__` hinterlegt. Das Skript verlangt beim ersten Start die Erstellung eines Master-Passworts, um diese Daten beim nächsten Start wieder zu entschlüsseln.
* **📦 Vollautomatischer Installer & Abhängigkeiten-Prüfung:** Direkt beim Start prüft das Skript, ob die benötigten Python-Module (`requests`, `paramiko`, `cryptography`) auf dem System vorhanden sind. Fehlen diese, **installiert das Skript alle Abhängigkeiten vollautomatisch nach** und startet sich danach selbst neu. Dabei nutzt es den `--break-system-packages` Parameter, um Konflikte mit PEP 668 auf modernen Debian/Mint-Systemen zu umgehen.
* **🚀 Intelligentes 1-Klick Deployment:** Über die Buttons in der GUI können Aktionen selektiv gesteuert werden. Du kannst wählen zwischen "Nur Upload", "Nur Update" oder "Upload & Update". Der Upload erfolgt via SFTP auf deinen bereitgestellten Webserver. Das Update führt anschließend über eine SSH-Verbindung (mittels `paramiko`) vollautomatisch den `pihole -g` Befehl auf deinem Pi-hole Server aus und triggert einen Reboot.
* **🛡️ Lokaler Import riesiger Offline-Dateien:** Neben den URL-Downloads unterstützt das Tool den Import extrem großer lokaler `.txt`-Dateien (wie die unten beschriebene 2,5 GB Mega-Blockliste) über den "Blockliste Import" Button. Diese Datei wird zwischengespeichert und beim Starten des Prozesses in die finale Master-Liste gemerged.
* **🖥️ Erweiterte GUI (Tkinter):** 
    * **Theme & Sprache:** Die GUI unterstützt ein Dark/Light-Theme und ist zweisprachig (DE/EN) verfügbar.
    * **Live-Log & Status:** Ein integriertes Textfeld zeigt die forensischen Konsolen-Outputs, Download-Größen und Schätzungen zum RAM-Verbrauch live an. Das Log lässt sich exportieren.
    * **Integriertes SSH-Terminal:** Das Skript kann direkt aus der GUI heraus ein Terminal (Gnome, Xfce4, Konsole, Xterm) öffnen und per `sshpass` (falls installiert) eine automatische SSH-Sitzung zu den konfigurierten Servern (Webserver oder Pi-hole) aufbauen.
* **🐧 Wayland/X11 Crash-Protection & Threading:** Das Skript nutzt einen speziellen, asynchronen GUI-Bootloader mit Verzögerungen (`root.after`), um gefürchtete Segfault-Abstürze bei Fenster-Resizes unter modernen Linux-Desktops zu verhindern. Downloads und Verarbeitung laufen in ausgelagerten Thread-Pools, um ein Einfrieren der GUI zu minimieren.
* **🔄 Intelligente Remote-Listen-Prüfung:** Vor dem Generieren einer neuen Liste verbindet sich das Skript mit dem konfigurierten Webserver und prüft, ob dort bereits eine alte Version der Master-Liste existiert. Wenn ja, fragt es, ob diese heruntergeladen und mit den neuen Links gemerged werden soll.

## 💾 Die 2,5 GB Ultimate Master-Blockliste
In diesem Projekt stelle ich meine über Jahre gewachsene **2,5 GB Master-Blockliste** zur Verfügung. Sie enthält unzählige Filter, darunter auch seltene oder bereits offline gegangene Filter (z. B. spezifische Microsoft-Telemetrie-Sperren), die nicht mehr über URLs verfügbar sind und extrem effektiv arbeiten.

Da Plattformen wie GitHub strenge Limits für Dateiuploads haben (25 MB im Web, max 100 MB via CLI) und automatisierte Bots Repositories gerne wegen bestimmter blockierter URLs flaggen, wird die Datei geschützt zur Verfügung gestellt. Da es sich um reinen Text handelt, lässt sich die Datei extrem gut komprimieren (von 2,5 GB auf ca. 433 MB) und ist mit einem Passwort geschützt.

**Download-Möglichkeiten:**
* **Google Drive (Verfügbar):** [Download Link via Google Drive](https://drive.google.com/file/d/1EMXInrwyJ8Wq1CBWxdHaZn3WrvDV62sJ/view?usp=sharing)
* **GitHub (Geplant):** Die Liste wird in naher Zukunft zusätzlich als gesplittete 7z-Dateien (Parts unter 100 MB) in einem separaten Unterordner dieses Repositories hochgeladen.

🔑 **Passwort zum Entpacken der Archivdateien (sowohl Google Drive ZIP als auch GitHub 7z-Parts):** 
`3007`

*Anwendung:* Lade die Datei herunter, entpacke sie mit dem Passwort und lade die resultierende `.txt` Datei im Programm über den Button **"🛡️ Blockliste Import"** hoch.

## 🛠️ Installation & Workflow
**WICHTIG:** Das Skript **muss zwingend mit `sudo` (Root-Rechten)** ausgeführt werden! Dies ist zwingend erforderlich, da der vollautomatische Auto-Installer bei fehlenden Python-Modulen Systemeingriffe vornimmt und das Skript für die SSH/SFTP-Netzwerkoperationen entsprechende Rechte benötigt.

1. **Voraussetzungen:** Ein lauffähiges Linux-System (getestet: Linux Mint 22.3) mit Python 3. Unter manchen Linux-Distributionen muss `python3-tk` für die grafische Oberfläche manuell nachinstalliert werden. Zudem benötigst du einen Pi-hole Server und einen Webserver für den Datei-Upload.
2. **Starten:** Führe das Skript im Terminal aus:
   ```bash
   sudo python3 Pihole_blocklistmanager_v2.2.py
   ```
3. **Tresor einrichten:** Beim allerersten Start fordert dich das Tool auf, ein Master-Passwort festzulegen. Mit diesem wird das Skript fortan verschlüsselt.
4. **Links Importieren:** Klicke links auf **"🔗 Quell-Links Import"** und wähle die beigelegte Datei `Pihole_Quell_Links.txt`. Darin befinden sich über 140 verifizierte Basis-URLs, die sofort geladen werden.
5. **Server konfigurieren:** Trage rechts deine Server-Daten ein:
    * *Upload Server (Webserver):* IP, SSH-User, Passwort und der exakte absolute Zielpfad auf dem Server (z.B. `/var/www/html/blocklist/BlocklisteFertig.txt`).
    * *Pi-Hole Server:* IP, SSH-User, Passwort und der auszuführende Befehl (Standard: `pihole -g; reboot`).
6. **Ausführen:** Klicke auf **"▶ Speichern & Start"**. Das Skript lädt die externen Links herunter, entpackt deine lokal importierte Liste, bereinigt Duplikate, lädt die Datei per SFTP hoch und stößt anschließend den Pi-hole Update-Prozess an.

### ⚠️ Wichtige Hinweise für Entwickler und Forks (Self-Modifying Code)
Dieses Skript nutzt eine Technik, bei der es seinen eigenen Quellcode überschreibt, um die verschlüsselten Daten (`__PAYLOAD_SALT__`, `__ENCRYPTED_PAYLOAD__`, `__PLAINTEXT_LINKS__`) persistent zu speichern.
**Vorsicht beim Committen/Teilen:** Wenn du das Skript gestartet und konfiguriert hast, enthält es deinen verschlüsselten Datensatz! Lade diese veränderte Datei niemals direkt auf GitHub oder in Foren hoch. Um eine saubere, "leere" Version zum Hochladen zu erhalten, musst du in der GUI zwingend auf den Button **"🗑 Tresor leeren"** klicken. Dadurch löscht das Skript alle persönlichen Payloads und Passwörter aus sich heraus und versetzt sich in den "Werkszustand" zurück.

---
*Ein besonderer Dank geht an Sempervideo für die jahrelange großartige Aufklärungsarbeit und die ursprünglichen Inspirationen rund um das Thema Pi-hole auf Proxmox, die den Anstoß für dieses Tool gegeben haben!*
