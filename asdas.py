import os
import webbrowser
import pyperclip
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, 
    QMessageBox, QHBoxLayout, QListWidget, QSplitter, QPlainTextEdit,
    QProgressBar, QMainWindow, QStatusBar, QMenu, QMenuBar, QAction,
    QFontDialog, QInputDialog
)

from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QSyntaxHighlighter, QIcon
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize

class FileLoader(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                content = []
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)
                
                chunk_size = 8192
                bytes_read = 0
                
                while True:
                    data = file.read(chunk_size)
                    if not data:
                        break
                    content.append(data)
                    bytes_read += len(data.encode('utf-8'))
                    progress = int((bytes_read / file_size) * 100)
                    self.progress.emit(progress)
                
                self.finished.emit("".join(content))
        except Exception as e:
            self.finished.emit(f"Hata: {str(e)}")

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []
        self.setup_rules()
        
    def setup_rules(self):
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor("red"))
        tag_format.setFontWeight(QFont.Bold)
        
        key_format = QTextCharFormat()
        key_format.setForeground(QColor("#FFD700"))  # Altın sarısı
        
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#98FB98"))  # Açık yeşil
        
        self.rules = [
            (r'\[.*?\]', tag_format),  # Köşeli parantez içindekiler
            (r'".*?"', string_format),  # Tırnak içindeki metinler
            (r'[A-Z][A-Za-z]*:', key_format),  # Büyük harfle başlayan kelimeler
        ]
    
    def highlightBlock(self, text):
        for pattern, format in self.rules:
            import re
            for match in re.finditer(pattern, text):
                start = match.start()
                length = match.end() - match.start()
                self.setFormat(start, length, format)

class TranslationTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Çeviri Aracı")
        self.setGeometry(100, 100, 1200, 800)
        
        # Merkezi widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Menü bar
        self.create_menu_bar()
        
        # Header - Küçük boyutlu
        self.header = QLabel("Çeviri Aracı")
        self.header.setFixedHeight(30)  # Yüksekliği sabitle
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 5px;
                color: white;
                background-color: #2c3e50;
                border-radius: 5px;
                margin: 2px;
            }
        """)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        self.progress_bar.hide()
        
        # Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Dosya listesi
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #2e2e2e;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
            }
        """)
        self.file_list.itemClicked.connect(self.load_selected_file)
        
        # Text Edit
        self.text_edit = QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: white;
                font-size: 14px;
                font-family: Consolas;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.text_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        
        # Syntax Highlighter
        self.highlighter = SyntaxHighlighter(self.text_edit.document())
        
        # Splitter'a widget'ları ekle
        self.splitter.addWidget(self.file_list)
        self.splitter.addWidget(self.text_edit)
        self.splitter.setSizes([200, 800])
        
        # Kontrol Butonları
        self.controls_layout = QHBoxLayout()
        
        button_style = """
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """
        
        self.load_folder_button = QPushButton("📁 Klasör Yükle")
        self.load_file_button = QPushButton("📄 Dosya Yükle")
        self.save_button = QPushButton("💾 Kaydet")
        self.translate_button = QPushButton("🌐 Çevir")
        self.find_button = QPushButton("🔍 Bul")
        
        buttons = [self.load_folder_button, self.load_file_button, 
                  self.save_button, self.translate_button, self.find_button]
        
        for button in buttons:
            button.setStyleSheet(button_style)
            self.controls_layout.addWidget(button)
        
        self.save_button.setEnabled(False)
        self.translate_button.setEnabled(False)
        self.find_button.setEnabled(False)
        
        # Ana layout'a eklemeler
        self.main_layout.addWidget(self.header)
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.splitter)
        self.main_layout.addLayout(self.controls_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Bağlantılar
        self.load_folder_button.clicked.connect(self.load_folder)
        self.load_file_button.clicked.connect(self.load_file)
        self.save_button.clicked.connect(self.save_file)
        self.translate_button.clicked.connect(self.translate_selection)
        self.find_button.clicked.connect(self.find_text)
        
        # Değişkenler
        self.folder_path = None
        self.current_file_path = None
        self.file_loader = None
        self.last_search = ""
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # Dosya menüsü
        file_menu = menubar.addMenu('Dosya')
        
        new_file = QAction('Yeni', self)
        new_file.setShortcut('Ctrl+N')
        new_file.triggered.connect(self.new_file)
        
        open_file = QAction('Aç', self)
        open_file.setShortcut('Ctrl+O')
        open_file.triggered.connect(self.load_file)
        
        save_file = QAction('Kaydet', self)
        save_file.setShortcut('Ctrl+S')
        save_file.triggered.connect(self.save_file)
        
        file_menu.addAction(new_file)
        file_menu.addAction(open_file)
        file_menu.addAction(save_file)
        
        # Düzen menüsü
        edit_menu = menubar.addMenu('Düzen')
        
        change_font = QAction('Yazı Tipi...', self)
        change_font.triggered.connect(self.change_font)
        
        edit_menu.addAction(change_font)
        
        # Görünüm menüsü
        view_menu = menubar.addMenu('Görünüm')
        
        toggle_wrap = QAction('Sözcük Kaydırma', self)
        toggle_wrap.setCheckable(True)
        toggle_wrap.triggered.connect(self.toggle_word_wrap)
        
        view_menu.addAction(toggle_wrap)
    
    def new_file(self):
        self.text_edit.clear()
        self.text_edit.setReadOnly(False)
        self.current_file_path = None
        self.save_button.setEnabled(True)
        self.translate_button.setEnabled(True)
        self.find_button.setEnabled(True)
        self.status_bar.showMessage('Yeni dosya oluşturuldu')
    
    def change_font(self):
        font, ok = QFontDialog.getFont(self.text_edit.font(), self)
        if ok:
            self.text_edit.setFont(font)
    
    def toggle_word_wrap(self, checked):
        self.text_edit.setLineWrapMode(
            QPlainTextEdit.WidgetWidth if checked else QPlainTextEdit.NoWrap
        )
    
    def find_text(self):
        text, ok = QInputDialog.getText(self, 'Metin Bul',
            'Aranacak metin:', text=self.last_search)
        
        if ok and text:
            self.last_search = text
            cursor = self.text_edit.document().find(text)
            if not cursor.isNull():
                self.text_edit.setTextCursor(cursor)
            else:
                QMessageBox.information(self, "Sonuç",
                    f"'{text}' metni bulunamadı.")
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.status_bar.showMessage(f'Dosya yükleniyor... %{value}')
    
    def file_loading_finished(self, content):
        self.text_edit.setPlainText(content)
        self.text_edit.setReadOnly(False)
        self.save_button.setEnabled(True)
        self.translate_button.setEnabled(True)
        self.find_button.setEnabled(True)
        self.progress_bar.hide()
        self.status_bar.showMessage('Dosya yüklendi')
        
        # Dosya bilgilerini göster
        if self.current_file_path:
            file_size = os.path.getsize(self.current_file_path) / 1024  # KB
            line_count = len(content.splitlines())
            self.status_bar.showMessage(
                f'Dosya: {os.path.basename(self.current_file_path)} | '
                f'Boyut: {file_size:.1f} KB | '
                f'Satır: {line_count}'
            )
    
    def load_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        
        if folder_path:
            self.folder_path = folder_path
            self.file_list.clear()
            
            for file_name in os.listdir(folder_path):
                if file_name.endswith((".txt", ".csv", ".json")):
                    self.file_list.addItem(file_name)
            
            self.status_bar.showMessage(
                f'{len(os.listdir(folder_path))} dosya bulundu'
            )
    
    def load_file(self, file_path=None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Dosya Seç", "", 
                "Desteklenen Dosyalar (*.txt *.csv *.json);;Tüm Dosyalar (*)"
            )
        
        if file_path:
            self.current_file_path = file_path
            self.text_edit.clear()
            self.progress_bar.show()
            self.progress_bar.setValue(0)
            
            self.file_loader = FileLoader(file_path)
            self.file_loader.progress.connect(self.update_progress)
            self.file_loader.finished.connect(self.file_loading_finished)
            self.file_loader.start()
    
    def load_selected_file(self, item):
        if not self.folder_path:
            return
        
        file_path = os.path.join(self.folder_path, item.text())
        if os.path.exists(file_path):
            self.load_file(file_path)
    
    def save_file(self):
        if not self.current_file_path:
            self.current_file_path, _ = QFileDialog.getSaveFileName(
                self, 'Dosyayı Kaydet', '', 
                'Metin Dosyası (*.txt);;Tüm Dosyalar (*)'
            )
        
        if self.current_file_path:
            try:
                with open(self.current_file_path, "w", encoding="utf-8") as file:
                    content = self.text_edit.toPlainText()
                    file.write(content)
                self.status_bar.showMessage('Dosya kaydedildi')
                QMessageBox.information(self, "Başarılı", "Değişiklikler kaydedildi.")
            except Exception as e:
                self.status_bar.showMessage('Dosya kaydedilemedi')
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilirken hata oluştu: {str(e)}")
    
    def translate_selection(self):
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            pyperclip.copy(selected_text)
            url = "https://www.deepl.com/translator#en/tr/"
            webbrowser.open(url)
            QTimer.singleShot(2000, self.auto_paste_deepl)
            self.status_bar.showMessage('Çeviri için DeepL açıldı')
        else:
            QMessageBox.warning(self, "Hata", "Çevrilecek metin seçilmedi.")
    
    def auto_paste_deepl(self):
        pyperclip.paste()

if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    
    # Dark tema ayarları
    dark_palette = app.palette()
    dark_palette.setColor(dark_palette.Window, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.WindowText, Qt.white)
    dark_palette.setColor(dark_palette.Base, QColor(15, 15, 15))
    dark_palette.setColor(dark_palette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.ToolTipBase, Qt.white)
    dark_palette.setColor(dark_palette.ToolTipText, Qt.white)
    dark_palette.setColor(dark_palette.Text, Qt.white)
    dark_palette.setColor(dark_palette.Button, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.ButtonText, Qt.white)
    dark_palette.setColor(dark_palette.BrightText, Qt.red)
    dark_palette.setColor(dark_palette.Link, QColor(42, 130, 218))
    dark_palette.setColor(dark_palette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(dark_palette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)
    
    tool = TranslationTool()
    tool.show()
    app.exec_()