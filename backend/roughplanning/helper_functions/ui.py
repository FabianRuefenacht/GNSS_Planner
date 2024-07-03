from PyQt5.QtWidgets import QLabel, QProgressBar, QApplication

def update_progresBar(bar: QProgressBar, label: QLabel, value: int, text: str) -> None:
    bar.setValue(value)
    label.setText(text)

    QApplication.processEvents()

    return