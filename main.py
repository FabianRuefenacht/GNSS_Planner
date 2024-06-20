import sys
import time
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
from PyQt5 import uic
from multiprocessing import Pool

# Funktionen, die in separaten Prozessen bzw. seriell ausgeführt werden sollen
def func1(num):
    s = 0
    for i in range(num):
        s += i
    return s

def func2(num):
    s = 0
    for i in range(num):
        s += i
    return s

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('./frontend/gnss_planner_dialog_base.ui', self)

        self.test_button = self.findChild(QPushButton, "Test")
        self.test_button.clicked.connect(self.run_tasks)

    def run_tasks(self):
        num_iterations = 100_000_000  # Anzahl der Iterationen für jede Funktion

        # Zeitmessung für parallele Ausführung
        start_time_parallel = time.time()
        with Pool() as pool:
            results_parallel = pool.map_async(func1, [num_iterations])
            results_parallel2 = pool.map_async(func2, [num_iterations])
            results_parallel3 = pool.map_async(func2, [num_iterations])
            results_parallel4 = pool.map_async(func2, [num_iterations])
            results_parallel5 = pool.map_async(func2, [num_iterations])
            results_parallel6 = pool.map_async(func2, [num_iterations])
            results_parallel7 = pool.map_async(func2, [num_iterations])
            results_parallel8 = pool.map_async(func2, [num_iterations])
            results_parallel9 = pool.map_async(func2, [num_iterations])
            results_parallel10 = pool.map_async(func2, [num_iterations])
            results_parallel.wait()  # Warten, bis die Ergebnisse verfügbar sind
            results_parallel2.wait()
            results_parallel3.wait()
            results_parallel4.wait()
            results_parallel5.wait()
            results_parallel6.wait()
            results_parallel7.wait()
            results_parallel8.wait()
            results_parallel9.wait()
            results_parallel10.wait()
        end_time_parallel = time.time()
        
        # Zeitmessung für serielle Ausführung
        start_time_serial = time.time()
        results_serial = [func1(num_iterations), func2(num_iterations), func2(num_iterations), func2(num_iterations), func2(num_iterations), func2(num_iterations), func2(num_iterations), func2(num_iterations), func2(num_iterations), func2(num_iterations)]
        end_time_serial = time.time()

        # Ausgabe der Ergebnisse und Zeitmessung
        print("Parallel execution time: {:.4f} seconds".format(end_time_parallel - start_time_parallel))
        print("Func1 result (parallel):", results_parallel.get()[0])
        print("Func2 result (parallel):", results_parallel2.get()[0])
        print("------------------------------------")
        print("Serial execution time: {:.4f} seconds".format(end_time_serial - start_time_serial))
        print("Func1 result (serial):", results_serial[0])
        print("Func2 result (serial):", results_serial[1])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
