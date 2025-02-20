import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QRadioButton, QLineEdit, QPushButton, 
                            QLabel, QFileDialog, QTextEdit, QProgressBar, 
                            QButtonGroup, QMessageBox, QTabWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt

class CharacterMapEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Tablo başlığı
        table_label = QLabel("Karakter Eşleştirme Tablosu")
        table_label.setObjectName("logLabel")
        layout.addWidget(table_label)
        
        # Tablo
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Değiştirilecek Karakter", "Yeni Karakter"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Yeni Eşleştirme")
        add_button.clicked.connect(self.add_row)
        add_button.setObjectName("actionButton")
        
        remove_button = QPushButton("Seçiliyi Sil")
        remove_button.clicked.connect(self.remove_selected_row)
        remove_button.setObjectName("actionButton")
        
        save_button = QPushButton("Kaydet")
        save_button.clicked.connect(self.save_mappings)
        save_button.setObjectName("saveButton")
        
        load_button = QPushButton("Yükle")
        load_button.clicked.connect(self.load_mappings)
        load_button.setObjectName("actionButton")
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(load_button)
        
        layout.addLayout(button_layout)
        
    def add_row(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
    def remove_selected_row(self):
        selected_rows = set(item.row() for item in self.table.selectedItems())
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)
            
    def get_mappings(self):
        mappings = {}
        for row in range(self.table.rowCount()):
            source = self.table.item(row, 0)
            target = self.table.item(row, 1)
            if source and target and source.text() and target.text():
                mappings[source.text()] = target.text()
        return mappings
        
    def set_mappings(self, mappings):
        self.table.setRowCount(0)
        for source, target in mappings.items():
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(source))
            self.table.setItem(row_position, 1, QTableWidgetItem(target))
            
    def save_mappings(self):
        mappings = self.get_mappings()
        if not mappings:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek eşleştirme bulunamadı!")
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Eşleştirmeleri Kaydet",
            "",
            "JSON files (*.json)"
        )
        
        if file_name:
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(mappings, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Başarılı", "Eşleştirmeler kaydedildi!")
            
    def load_mappings(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Eşleştirmeleri Yükle",
            "",
            "JSON files (*.json)"
        )
        
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    mappings = json.load(f)
                self.set_mappings(mappings)
                QMessageBox.information(self, "Başarılı", "Eşleştirmeler yüklendi!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya yüklenirken hata: {str(e)}")

class ModernCharacterConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Karakter Dönüştürücü\n by ati")
        self.setMinimumSize(900, 600)
        
        # Varsayılan karakter eşleştirmeleri
        self.default_mappings = {
            'Ğ': 'ß', 'ş': 'é', 'İ': 'Î',
            'Ş': 'É', 'ğ': 'ê', 'Ç': 'Á',
            'ı': 'ì'
        }
        
        self.init_ui()
        self.apply_styles()
        
    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Başlık
        title_label = QLabel("Karakter Dönüştürücü\n by ati")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)
        
        # Tab widget
        tab_widget = QTabWidget()
        tab_widget.setObjectName("tabWidget")
        
        # Dönüştürme sekmesi
        converter_tab = QWidget()
        converter_layout = QVBoxLayout(converter_tab)
        
        # Seçim alanı
        selection_layout = QHBoxLayout()
        self.button_group = QButtonGroup()
        
        self.file_radio = QRadioButton("Tek Dosya")
        self.folder_radio = QRadioButton("Klasör")
        self.file_radio.setChecked(True)
        
        self.button_group.addButton(self.file_radio)
        self.button_group.addButton(self.folder_radio)
        
        selection_layout.addWidget(self.file_radio)
        selection_layout.addWidget(self.folder_radio)
        selection_layout.addStretch()
        
        converter_layout.addLayout(selection_layout)
        
        # Dosya seçimi
        file_layout = QHBoxLayout()
        self.path_entry = QLineEdit()
        self.path_entry.setPlaceholderText("Dosya veya klasör yolu...")
        
        select_button = QPushButton("Seç")
        select_button.clicked.connect(self.select_path)
        select_button.setObjectName("selectButton")
        
        file_layout.addWidget(self.path_entry)
        file_layout.addWidget(select_button)
        
        converter_layout.addLayout(file_layout)
        
        # Kaydedilecek klasör seçimi
        self.save_folder_entry = QLineEdit()
        self.save_folder_entry.setPlaceholderText("Kaydedilecek klasör yolu...")
        
        save_folder_button = QPushButton("Kaydedilecek Klasörü Seç")
        save_folder_button.clicked.connect(self.select_save_folder)
        save_folder_button.setObjectName("selectButton")
        
        converter_layout.addWidget(self.save_folder_entry)
        converter_layout.addWidget(save_folder_button)
        
        # Dönüştür butonu
        convert_button = QPushButton("Dönüştür")
        convert_button.clicked.connect(self.convert)
        convert_button.setObjectName("convertButton")
        convert_button.setMinimumHeight(50)
        converter_layout.addWidget(convert_button)
        
        # Log alanı
        log_label = QLabel("İşlem Logları")
        log_label.setObjectName("logLabel")
        converter_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        converter_layout.addWidget(self.log_text)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        converter_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        converter_layout.addWidget(self.status_label)
        
        # Karakter eşleştirme sekmesi
        self.char_map_editor = CharacterMapEditor()
        self.char_map_editor.set_mappings(self.default_mappings)
        
        # Sekmeleri ekle
        tab_widget.addTab(converter_tab, "Dönüştürme")
        tab_widget.addTab(self.char_map_editor, "Karakter Eşleştirme")
        
        main_layout.addWidget(tab_widget)
        
    def apply_styles(self):
        style = """
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 12px;
            }
            #titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                margin: 20px;
            }
            QTabWidget::pane {
                border: 1px solid #333333;
            }
            QTabBar::tab {
                background-color: #2b2b2b;
                color: #ffffff;
                padding: 8px 20px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                font-weight: bold;
            }
            QTableWidget {
                background-color: #2b2b2b;
                border: 1px solid #333333;
                gridline-color: #333333;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                padding: 5px;
                border: 1px solid #333333;
            }
            QRadioButton {
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #666666;
            }
            QRadioButton::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #2196F3;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #333333;
                border-radius: 5px;
                background-color: #2b2b2b;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            #convertButton {
                font-size: 14px;
            }
            #actionButton {
                background-color: #424242;
            }
            #actionButton:hover {
                background-color: #616161;
            }
            #saveButton {
                background-color: #4CAF50;
            }
            #saveButton:hover {
                background-color: #388E3C;
            }
            QTextEdit {
                background-color: #2b2b2b;
                border: 2px solid #333333;
                border-radius: 5px;
                padding: 8px;
            }
            #logLabel {
                font-size: 16px;
                font-weight: bold;
            }
            QProgressBar {
                border: 2px solid #333333;
                border-radius: 5px;
                background-color: #2b2b2b;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
            #statusLabel {
                color: #9e9e9e;
            }
        """
        self.setStyleSheet(style)
        
    def select_path(self):
        if self.file_radio.isChecked():
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Dönüştürülecek Dosyayı Seçin",
                "",
                "Text files (*.txt)"
            )
        else:
            path = QFileDialog.getExistingDirectory(
                self,
                "Dönüştürülecek Klasörü Seçin"
            )
            
        if path:
            self.path_entry.setText(path)
            
    def select_save_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Kaydedilecek Klasörü Seçin"
        )
        
        if folder:
            self.save_folder_entry.setText(folder)
            
    def log_message(self, message):
        self.log_text.append(message)
        
    def convert_single_file(self, input_file, save_folder=None):
        try:
            file_name = os.path.basename(input_file)
            if save_folder:
                output_file = os.path.join(save_folder, file_name)
            else:
                file_path = os.path.dirname(input_file)
                output_file = os.path.join(file_path, file_name)
            
            with open(input_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Güncel karakter eşleştirmelerini kullan
            char_map = self.char_map_editor.get_mappings()
            for old_char, new_char in char_map.items():
                content = content.replace(old_char, new_char)
            
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(content)
                
            self.log_message(f"✅ Başarılı: {output_file}")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Hata: {str(e)}")
            return False
            
    def convert(self):
        path = self.path_entry.text()
        if not path:
            QMessageBox.critical(self, "Hata", "Lütfen bir dosya veya klasör seçin!")
            return
            
        save_folder = self.save_folder_entry.text() if self.save_folder_entry.text() else None
        
        self.log_text.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("İşlem başlatılıyor...")
        
        if self.file_radio.isChecked():
            self.convert_single_file(path, save_folder)
            self.status_label.setText("İşlem tamamlandı!")
            self.progress_bar.setValue(100)
        else:
            # Klasör içindeki tüm dosyaları dönüştür
            files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.txt')]
            total_files = len(files)
            if total_files == 0:
                QMessageBox.critical(self, "Hata", "Klasörde dönüştürülecek .txt dosyası bulunamadı!")
                return
            
            self.status_label.setText(f"{total_files} dosya bulundu, dönüştürme başlatılıyor...")
            success_count = 0
            
            for i, file in enumerate(files):
                if self.convert_single_file(file, save_folder):
                    success_count += 1
                self.progress_bar.setValue(int((i + 1) / total_files * 100))
                self.status_label.setText(f"{i + 1}/{total_files} dosya işlendi...")
            
            self.status_label.setText(f"İşlem tamamlandı! {success_count}/{total_files} dosya başarıyla dönüştürüldü.")
            self.progress_bar.setValue(100)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernCharacterConverter()
    window.show()
    sys.exit(app.exec())