<h1 align="center">hellkai's FL Studio RPC</h1>

<p align="center">
Lightweight Discord Rich Presence client for FL Studio featuring a clean AMOLED interface and system tray integration.
</p>

<p align="center">
<img width="392" height="312" alt="FL-STUDIO-RPC" src="https://github.com/user-attachments/assets/907dcb7e-5892-4c56-b1c6-d5d371544e5c" />
<p align="center">
GUI version
</p>

<p align="center">
<img width="1113" height="626" alt="FL-STUDIO-RPC-CLI" src="https://github.com/user-attachments/assets/25ab151a-118b-4ed8-ae58-fa0351d9e0d6" />

<p align="center">
CLI version
</p>

<p align="center">
<img width="243" height="108" alt="DISCORD-RPC" src="https://github.com/user-attachments/assets/4333686b-771f-42d1-a8ea-a6e95db44fbe" />
<p align="center">
Discord RPC
</p>

  <p align="center">
  <img src="https://img.shields.io/github/v/release/hellkxxxi/FL-STUDIO-RPC?color=ff6b00&label=version&style=flat-square">
  <img src="https://img.shields.io/github/license/hellkxxxi/FL-STUDIO-RPC?color=ff6b00&style=flat-square">
  <img src="https://img.shields.io/github/downloads/hellkxxxi/FL-STUDIO-RPC/total?color=ff6b00&style=flat-square">
</p>

## ☆ Features
- **Live Project Detection:** Automatically displays the name of the `.flp` project you are currently working on (or `In Empty Project` when starting a new beat).
- **DAW Version Detection:** Detects and displays your exact FL Studio version (FL Studio 20 / 21 / 2024).
- **Elapsed Time Tracking:** Displays total session time spent producing in DAW.
- **Two Editions:**
  - **GUI Edition (`FL-STUDIO-RPC.exe`):** Minimalist AMOLED window (`PyQt6`) that minimizes cleanly to the Windows system tray.
  - **CLI Edition (`FL-STUDIO-RPC-CLI.exe`):** Ultra-lightweight console version with minimal resource usage.
- **Zero Overhead:** Uses native Windows Win32 window hooks without injecting into FL Studio or affecting audio buffer performance.

## =▷ Download & Usage
No Python installation required!
1. Go to the [**Releases**](../../releases) page and download the version you prefer:
   - `FL-STUDIO-RPC.exe` — **AMOLED GUI + System Tray**
   - `FL-STUDIO-RPC-CLI.exe` — **Lightweight Console**
2. Make sure **Discord** is running.
3. Run `FL-STUDIO-RPC.exe` (before or after launching FL Studio).

## ↧ Running from Source
If you want to run or build the script yourself:

```
pip install pypresence PyQt6
python fl_status.py
python fl_status_cli.py
```
```
pip install pyinstaller
pyinstaller --noconsole --onefile --icon=icon.ico --add-data "icon.ico;." --name "FL-STUDIO-RPC" fl_status.py
pyinstaller --onefile --icon=icon.ico --exclude-module PyQt6 --name "FL-STUDIO-RPC-CLI" fl_status_cli.py
```

Сreated by **hellkai \\ hellkxxxi**
