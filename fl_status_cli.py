import ctypes
import os
import sys
import time
from pypresence import Presence

DISCORD_ID = "1569412253961167038"
APP_VERSION = "v1.0.0"

ORANGE = "\033[38;2;255;107;0m"
CYAN = "\033[38;2;0;229;255m"
GREEN = "\033[38;2;0;255;136m"
GRAY = "\033[38;2;118;128;121m"
WHITE = "\033[38;2;236;232;225m"
RESET = "\033[0m"

BANNER = f"""{ORANGE}
 ███████╗██╗          ███████╗████████╗██╗   ██╗██████╗ ██╗ ██████╗       ██████╗ ██████╗  ██████╗
 ██╔════╝██║          ██╔════╝╚══██╔══╝██║   ██║██╔══██╗██║██╔═══██╗      ██╔══██╗██╔══██╗██╔════╝
 █████╗  ██║    █████╗███████╗   ██║   ██║   ██║██║  ██║██║██║   ██║█████╗██████╔╝██████╔╝██║     
 ██╔══╝  ██║    ╚════╝╚════██║   ██║   ██║   ██║██║  ██║██║██║   ██║╚════╝██╔══██╗██╔═══╝ ██║     
 ██║     ███████╗     ███████║   ██║   ╚██████╔╝██████╔╝██║╚██████╔╝      ██║  ██║██║     ╚██████╗
 ╚═╝     ╚══════╝     ╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝       ╚═╝  ╚═╝╚═╝      ╚═════╝{RESET}
                                                                            {GRAY}{APP_VERSION} | github.com/hellkxxxi{RESET}
"""

user32 = ctypes.windll.user32


def setup_console():
    os.system("cls" if os.name == "nt" else "clear")
    if os.name == "nt":
        ctypes.windll.kernel32.SetConsoleTitleW(f"FL STUDIO RPC {APP_VERSION}")
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    print(BANNER)


def print_status(text):
    sys.stdout.write(f"\r\033[K{text}")
    sys.stdout.flush()


def get_window_title(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def get_fl_studio_info():
    hwnd = user32.FindWindowW("TFruityLoopsMainForm", None)
    title = get_window_title(hwnd) if hwnd else ""

    if not title:
        found_titles = []

        def enum_cb(h, _):
            if user32.IsWindowVisible(h):
                t = get_window_title(h)
                if " - FL Studio" in t or t.startswith("FL Studio "):
                    found_titles.append(t)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(
            ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p
        )
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        if found_titles:
            title = found_titles[0]

    if not title:
        return None

    if " - FL Studio" in title:
        parts = title.rsplit(" - FL Studio", 1)
        project = parts[0].strip()
        version = ("FL Studio" + parts[1]).strip()
        return {"project": project, "version": version}
    elif title.startswith("FL Studio"):
        return {"project": "Untitled Project", "version": title.strip()}
    else:
        return {"project": title.strip(), "version": "FL Studio"}


def main():
    setup_console()
    print(f" {ORANGE}connecting to Discord...{RESET}")
    rpc = None
    while not rpc:
        try:
            rpc = Presence(DISCORD_ID)
            rpc.connect()
        except:
            print_status(f" {CYAN}waiting for Discord...{RESET}")
            time.sleep(5)

    start_time = None
    wait_counter = 1

    while True:
        try:
            info = get_fl_studio_info()

            if not info:
                start_time = None
                print_status(
                    f" {WHITE}[{wait_counter}]{RESET} {CYAN}waiting for FL Studio...{RESET}"
                )
                wait_counter += 1
                rpc.clear()
                time.sleep(5)
                continue

            wait_counter = 1
            if start_time is None:
                start_time = int(time.time())

            project = info["project"]
            version = info["version"]

            if project == "Untitled Project":
                details = "In Empty Project"
                state_text = "Idling / Starting a new beat"
            else:
                details = f"Working on: {project}"
                state_text = "Producing in DAW"

            rpc.update(
                details=details,
                state=state_text,
                large_image="logo",
                large_text=version,
                start=start_time,
            )

            print_status(
                f" {GREEN}[ACTIVE]{RESET} {WHITE}{details}{RESET} {GRAY}|{RESET} {ORANGE}{version}{RESET}"
            )

        except Exception:
            start_time = None
            try:
                rpc.clear()
            except:
                pass
            print_status(
                f" {WHITE}[{wait_counter}]{RESET} {CYAN}waiting for FL Studio...{RESET}"
            )
            wait_counter += 1

        time.sleep(5)


if __name__ == "__main__":
    main()