import sys
import os
import json
import yaml
import xmltodict
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject

# Task 2 do 7: Wczytywanie, walidacja i zapis
def load_data(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if ext == '.json':
        return json.loads(content)
    elif ext in ['.yml', '.yaml']:
        return yaml.safe_load(content)
    elif ext == '.xml':
        return xmltodict.parse(content)
    else:
        raise ValueError(f"Zły format: {ext}")

def save_data(data, file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.json':
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    elif ext in ['.yml', '.yaml']:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f)
    elif ext == '.xml':
        if not isinstance(data, dict) or len(data) != 1:
            data = {"root": data}
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xmltodict.unparse(data, pretty=True))

# Task 1: Parsowanie argumentów z wiersza poleceń
def run_cli():
    if len(sys.argv) != 3:
        print("Użycie: program.exe pathFile1.x pathFile2.y")
        sys.exit(1)
    
    in_path, out_path = sys.argv[1], sys.argv[2]
    try:
        data = load_data(in_path)
        save_data(data, out_path)
        print("Konwersja udana.")
    except Exception as e:
        print(f"Błąd: {e}")

# Task 9: Asynchroniczność
class WorkerSignals(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

# Task 8: Prosty UI w PyQt
class AppUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Konwerter Danych")
        self.setGeometry(100, 100, 300, 200)
        self.in_file = ""
        self.out_file = ""
        
        layout = QVBoxLayout()
        
        self.btn_in = QPushButton("Wybierz plik wejściowy")
        self.btn_in.clicked.connect(self.select_in)
        layout.addWidget(self.btn_in)
        
        self.btn_out = QPushButton("Wybierz plik wyjściowy")
        self.btn_out.clicked.connect(self.select_out)
        layout.addWidget(self.btn_out)
        
        self.btn_convert = QPushButton("Konwertuj")
        self.btn_convert.clicked.connect(self.convert)
        layout.addWidget(self.btn_convert)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_in(self):
        self.in_file, _ = QFileDialog.getOpenFileName(self, "Plik wejściowy")
        self.btn_in.setText(self.in_file or "Wybierz plik wejściowy")

    def select_out(self):
        self.out_file, _ = QFileDialog.getSaveFileName(self, "Plik wyjściowy")
        self.btn_out.setText(self.out_file or "Wybierz plik wyjściowy")

    def convert(self):
        if not self.in_file or not self.out_file:
            QMessageBox.warning(self, "Błąd", "Wybierz oba pliki!")
            return
            
        self.signals = WorkerSignals()
        self.signals.finished.connect(lambda m: QMessageBox.information(self, "Sukces", m))
        self.signals.error.connect(lambda e: QMessageBox.critical(self, "Błąd", e))
        
        # Wątek w tle
        threading.Thread(target=self.do_work, daemon=True).start()

    def do_work(self):
        try:
            data = load_data(self.in_file)
            save_data(data, self.out_file)
            self.signals.finished.emit("Udało się!")
        except Exception as e:
            self.signals.error.emit(str(e))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_cli()
    else:
        app = QApplication(sys.argv)
        window = AppUI()
        window.show()
        sys.exit(app.exec_())