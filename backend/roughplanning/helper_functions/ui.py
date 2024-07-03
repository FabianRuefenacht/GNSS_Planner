from PyQt5.QtWidgets import QLabel, QProgressBar, QApplication

def update_progresBar(bar: QProgressBar, label: QLabel, value: int, text: str) -> None:
    bar.setValue(value) # update progressBar
    label.setText(text) # update text-hint for user

    QApplication.processEvents() # ensure function is terminated before next action in main is called

    return