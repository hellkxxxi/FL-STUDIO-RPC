import asyncio
import ctypes
import os
import sys
import time
from pypresence import Presence
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

DISCORD_ID = "1569412253961167038"
APP_VERSION = "v1.0.0"

user32 = ctypes.windll.user32


def load_app_icon():
    search_dirs = []
    if hasattr(sys, "_MEIPASS"):
        search_dirs.append(sys._MEIPASS)
    if getattr(sys, "frozen", False):
        search_dirs.append(os.path.dirname(sys.executable))
    search_dirs.append(os.path.dirname(os.path.abspath(__file__)))

    for folder in search_dirs:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.lower().endswith((".ico", ".png")):
                    return QIcon(os.path.join(folder, file))

    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#000000"))
    painter.setPen(QColor("#ff6b00"))
    painter.drawRoundedRect(2, 2, 60, 60, 14, 14)
    painter.setFont(QFont("Segoe UI", 28, QFont.Weight.Black))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "FL")
    painter.end()
    return QIcon(pixmap)


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


class RPCWorker(QThread):
    update_ui = pyqtSignal(str, str, str, str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.start_time = None

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        rpc = None
        while self.running and not rpc:
            try:
                rpc = Presence(DISCORD_ID)
                rpc.connect()
            except:
                self.update_ui.emit(
                    "Waiting for Discord...",
                    "Discord not detected",
                    "Make sure Discord is open",
                    "",
                )
                time.sleep(5)

        wait_counter = 1

        while self.running:
            try:
                info = get_fl_studio_info()

                if not info:
                    self.start_time = None
                    self.update_ui.emit(
                        f"[{wait_counter}] waiting for FL Studio...",
                        "FL Studio is closed",
                        "Launch FL Studio to start RPC",
                        "",
                    )
                    wait_counter += 1
                    rpc.clear()
                    time.sleep(5)
                    continue

                wait_counter = 1
                if self.start_time is None:
                    self.start_time = int(time.time())

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
                    start=self.start_time,
                )

                self.update_ui.emit("ACTIVE", details, state_text, version)

            except Exception:
                self.start_time = None
                try:
                    rpc.clear()
                except:
                    pass
                self.update_ui.emit(
                    f"[{wait_counter}] waiting for FL Studio...",
                    "FL Studio is closed",
                    "Launch FL Studio to start RPC",
                    "",
                )
                wait_counter += 1

            time.sleep(5)


class MainWindow(QMainWindow):

    def __init__(self, icon):
        super().__init__()
        self.app_icon = icon
        self.setWindowTitle(f"FL STUDIO RPC {APP_VERSION}")
        self.setWindowIcon(self.app_icon)
        self.setFixedSize(390, 280)

        try:
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                int(self.winId()), 20, ctypes.byref(ctypes.c_int(1)), 4
            )
        except:
            pass

        self.setStyleSheet("""
            QMainWindow { background-color: #000000; }
            QLabel#Header {
                color: #ff6b00;
                font-family: 'Segoe UI', sans-serif;
                font-size: 21px;
                font-weight: 900;
                letter-spacing: 2px;
            }
            QLabel#Version {
                color: #555555;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            QLabel#ConnStatus {
                color: #00e5ff;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                font-weight: bold;
            }
            QFrame#Card {
                background-color: #0a0a0c;
                border: 1px solid #1c1c21;
                border-left: 4px solid #ff6b00;
                border-radius: 6px;
            }
            QLabel#CardTitle {
                color: #555555;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QLabel#Details {
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 15px;
                font-weight: bold;
            }
            QLabel#State {
                color: #b5bac1;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QLabel#Extra {
                color: #ff6b00;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                font-weight: bold;
            }
            QLabel#Timer {
                color: #23a55a;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #0d0d10;
                color: #ece8e1;
                border: 1px solid #222228;
                border-radius: 4px;
                padding: 7px;
                font-weight: bold;
                font-size: 12px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #ff6b00;
                border-color: #ff6b00;
                color: #ffffff;
            }
            QLabel#GithubLink {
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 14, 20, 12)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        self.header_lbl = QLabel("FL-STUDIO-RPC")
        self.header_lbl.setObjectName("Header")
        self.ver_lbl = QLabel(APP_VERSION)
        self.ver_lbl.setObjectName("Version")
        header_layout.addWidget(self.header_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.ver_lbl)
        layout.addLayout(header_layout)

        self.conn_lbl = QLabel("[1] waiting for FL Studio...")
        self.conn_lbl.setObjectName("ConnStatus")
        layout.addWidget(self.conn_lbl)

        self.card = QFrame()
        self.card.setObjectName("Card")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(3)

        self.card_title = QLabel("DISCORD RICH PRESENCE PREVIEW")
        self.card_title.setObjectName("CardTitle")
        self.details_lbl = QLabel("Initializing...")
        self.details_lbl.setObjectName("Details")
        self.state_lbl = QLabel("...")
        self.state_lbl.setObjectName("State")

        bottom_card_layout = QHBoxLayout()
        self.extra_lbl = QLabel("")
        self.extra_lbl.setObjectName("Extra")
        self.timer_lbl = QLabel("")
        self.timer_lbl.setObjectName("Timer")
        bottom_card_layout.addWidget(self.extra_lbl)
        bottom_card_layout.addStretch()
        bottom_card_layout.addWidget(self.timer_lbl)

        card_layout.addWidget(self.card_title)
        card_layout.addWidget(self.details_lbl)
        card_layout.addWidget(self.state_lbl)
        card_layout.addLayout(bottom_card_layout)
        layout.addWidget(self.card)

        btn_layout = QHBoxLayout()
        self.tray_btn = QPushButton("HIDE TO TRAY")
        self.tray_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tray_btn.clicked.connect(self.hide)

        self.quit_btn = QPushButton("QUIT")
        self.quit_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.quit_btn.clicked.connect(self.quit_app)

        btn_layout.addWidget(self.tray_btn)
        btn_layout.addWidget(self.quit_btn)
        layout.addLayout(btn_layout)

        self.github_lbl = QLabel(
            '<a href="https://github.com/hellkxxxi" style="color: #666666; text-decoration: none;">github.com/hellkxxxi</a>'
        )
        self.github_lbl.setObjectName("GithubLink")
        self.github_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.github_lbl.setOpenExternalLinks(True)
        layout.addWidget(self.github_lbl)

        self.tray_icon = QSystemTrayIcon(self.app_icon, self)
        self.tray_icon.setToolTip(f"FL STUDIO RPC {APP_VERSION}")

        tray_menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.showNormal)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_click)
        self.tray_icon.show()

        self.worker = RPCWorker()
        self.worker.update_ui.connect(self.on_status_update)
        self.worker.start()

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_elapsed_time)
        self.ui_timer.start(1000)

    def update_elapsed_time(self):
        if self.worker.start_time:
            elapsed = int(time.time()) - self.worker.start_time
            mins, secs = divmod(elapsed, 60)
            hours, mins = divmod(mins, 60)
            if hours > 0:
                self.timer_lbl.setText(f"{hours}:{mins:02d}:{secs:02d}")
            else:
                self.timer_lbl.setText(f"{mins:02d}:{secs:02d}")
        else:
            self.timer_lbl.setText("")

    def on_status_update(self, conn_status, details, state, extra):
        self.conn_lbl.setText(conn_status)
        if conn_status == "ACTIVE":
            self.conn_lbl.setStyleSheet(
                "color: #00ff88; font-family: 'Consolas', monospace; font-size: 13px; font-weight: bold;"
            )
        else:
            self.conn_lbl.setStyleSheet(
                "color: #00e5ff; font-family: 'Consolas', monospace; font-size: 13px; font-weight: bold;"
            )

        self.details_lbl.setText(details)
        self.state_lbl.setText(state)
        self.extra_lbl.setText(extra)
        self.update_elapsed_time()

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()
                self.activateWindow()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def quit_app(self):
        self.worker.running = False
        self.tray_icon.hide()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    icon = load_app_icon()
    window = MainWindow(icon)
    window.show()
    sys.exit(app.exec())