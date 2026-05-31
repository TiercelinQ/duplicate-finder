import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt

from config import APP_NAME, ORG_NAME, SCAN_SECTION, Theme
from models.preferences import Preferences
from views.main_window import MainWindow
from controllers.scan_controller import ScanController
from controllers.file_controller import FileController


def load_stylesheet(app: QApplication, path: Path) -> None:
    """Load and apply QSS stylesheet."""
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    icon_path = Path(__file__).resolve().parent / "resources" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))


def apply_theme(window: MainWindow, prefs: Preferences, app: QApplication) -> None:
    """Determine and apply the correct theme."""
    theme_val = prefs.theme
    if theme_val == Theme.SYSTEM.value:
        palette = app.styleHints()
        is_dark = palette.colorScheme() == Qt.ColorScheme.Dark
    else:
        is_dark = theme_val == Theme.DARK.value

    window.setProperty("darkMode", is_dark)
    window.topbar.update_theme_icon(is_dark)
    app.setStyle("Fusion")


def create_splash(icon_path: Path) -> QSplashScreen | None:
    """Create a fixed-size splash screen with the app icon centered."""
    if not icon_path.exists():
        return None

    splash_size = 200
    pixmap = QPixmap(splash_size, splash_size)
    pixmap.fill(Qt.GlobalColor.transparent)

    icon_pixmap = QPixmap(str(icon_path)).scaled(
        splash_size,
        splash_size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )

    from PyQt6.QtGui import QPainter
    painter = QPainter(pixmap)
    x = (splash_size - icon_pixmap.width()) // 2
    y = (splash_size - icon_pixmap.height()) // 2
    painter.drawPixmap(x, y, icon_pixmap)
    painter.end()

    splash = QSplashScreen(pixmap, Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen)
    splash.setFixedSize(splash_size, splash_size)
    return splash


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    icon_path = Path(__file__).resolve().parent / "resources" / "app_icon.png"
    splash = create_splash(icon_path)
    if splash:
        splash.show()
        app.processEvents()

    prefs = Preferences()

    qss_path = Path(__file__).resolve().parent / "resources" / "styles.qss"
    load_stylesheet(app, qss_path)

    window = MainWindow()
    apply_theme(window, prefs, app)

    window.restore_geometry_from_prefs(prefs.window)

    scan_controller = ScanController(window, prefs)
    file_controller = FileController(window)

    def on_section_changed(section_id: str) -> None:
        window.show_section(section_id)

    def on_theme_toggled() -> None:
        current = prefs.theme
        if current == Theme.DARK.value:
            prefs.theme = Theme.LIGHT.value
            window.setProperty("darkMode", False)
            window.topbar.update_theme_icon(False)
        else:
            prefs.theme = Theme.DARK.value
            window.setProperty("darkMode", True)
            window.topbar.update_theme_icon(True)
        prefs.save()
        load_stylesheet(app, qss_path)

    def on_close() -> None:
        scan_controller.abort()
        geo = window.geometry()
        prefs.window = {
            "width": geo.width(),
            "height": geo.height(),
            "x": geo.x(),
            "y": geo.y(),
        }
        prefs.save()

    window.sidebar.section_changed.connect(on_section_changed)
    window.topbar.theme_toggled.connect(on_theme_toggled)
    app.aboutToQuit.connect(on_close)

    window.sidebar.set_active(SCAN_SECTION)
    window.show_section(SCAN_SECTION)
    window.show()

    if splash:
        splash.finish(window)

    window.raise_()
    window.activateWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()