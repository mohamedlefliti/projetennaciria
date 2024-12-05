import sys
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTableWidget, QTableWidgetItem, QMessageBox,
                            QFrame, QHeaderView, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon
import pandas as pd

class FinancialManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة المالية للمؤسسة التعليمية")
        self.setGeometry(100, 100, 1200, 800)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # Add RTL support
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QWidget {
                font-family: 'Arial';
                font-size: 12px;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
                min-height: 30px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                min-width: 100px;
                min-height: 35px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 5px;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Initialize database
        self.init_database()
        
        # Setup UI
        self.setup_ui()
        
        # Load data
        self.load_data()

    def init_database(self):
        try:
            self.conn = sqlite3.connect('financial_data.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    description TEXT,
                    amount REAL,
                    type TEXT,
                    category TEXT
                )
            ''')
            self.conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في قاعدة البيانات: {str(e)}")

    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title Label
        title_label = QLabel("نظام إدارة المالية")
        title_label.setStyleSheet("""
            font-size: 24px;
            color: #1976D2;
            font-weight: bold;
            margin-bottom: 20px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Input Container
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        input_layout = QVBoxLayout(input_container)

        # Input fields with labels
        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(15)

        # Create input groups
        self.description_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.category_input = QLineEdit()
        self.type_input = QLineEdit()

        input_groups = [
            ("الوصف", self.description_input),
            ("المبلغ", self.amount_input),
            ("الفئة", self.category_input),
            ("النوع", self.type_input)
        ]

        for label_text, input_widget in input_groups:
            group_layout = QVBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("color: #666; font-weight: bold;")
            group_layout.addWidget(label)
            input_widget.setPlaceholderText(f"أدخل {label_text}")
            group_layout.addWidget(input_widget)
            fields_layout.addLayout(group_layout)

        input_layout.addLayout(fields_layout)
        layout.addWidget(input_container)

        # Buttons
        button_container = QFrame()
        button_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(15)

        buttons = [
            ("إضافة", "#4CAF50", self.add_transaction),
            ("تحديث", "#2196F3", self.update_transaction),
            ("حذف", "#F44336", self.delete_transaction),
            ("تصدير إلى Excel", "#FF9800", self.export_to_excel)
        ]

        for text, color, handler in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    min-width: 120px;
                }}
                QPushButton:hover {{
                    background-color: {color}dd;
                }}
            """)
            btn.clicked.connect(handler)
            button_layout.addWidget(btn)

        layout.addWidget(button_container)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "التاريخ", "الوصف", "المبلغ", "النوع", "الفئة"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.clicked.connect(self.select_row)
        layout.addWidget(self.table)

    def load_data(self):
        try:
            self.cursor.execute("SELECT * FROM transactions")
            data = self.cursor.fetchall()
            self.table.setRowCount(len(data))
            
            for row, record in enumerate(data):
                for col, value in enumerate(record):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في تحميل البيانات: {str(e)}")

    def add_transaction(self):
        try:
            description = self.description_input.text()
            amount = float(self.amount_input.text())
            category = self.category_input.text()
            trans_type = self.type_input.text()
            date = datetime.now().strftime("%Y-%m-%d")

            if not all([description, amount, category, trans_type]):
                QMessageBox.warning(self, "تنبيه", "الرجاء ملء جميع الحقول")
                return

            self.cursor.execute('''
                INSERT INTO transactions (date, description, amount, type, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, description, amount, trans_type, category))
            self.conn.commit()
            self.load_data()
            self.clear_inputs()
            QMessageBox.information(self, "نجاح", "تمت إضافة المعاملة بنجاح")
        except ValueError:
            QMessageBox.warning(self, "خطأ", "الرجاء إدخال رقم صحيح في حقل المبلغ")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")

    def update_transaction(self):
        try:
            selected_row = self.table.currentRow()
            if selected_row >= 0:
                transaction_id = int(self.table.item(selected_row, 0).text())
                description = self.description_input.text()
                amount = float(self.amount_input.text())
                category = self.category_input.text()
                trans_type = self.type_input.text()

                if not all([description, amount, category, trans_type]):
                    QMessageBox.warning(self, "تنبيه", "الرجاء ملء جميع الحقول")
                    return

                self.cursor.execute('''
                    UPDATE transactions 
                    SET description=?, amount=?, type=?, category=?
                    WHERE id=?
                ''', (description, amount, trans_type, category, transaction_id))
                self.conn.commit()
                self.load_data()
                self.clear_inputs()
                QMessageBox.information(self, "نجاح", "تم تحديث المعاملة بنجاح")
            else:
                QMessageBox.warning(self, "تنبيه", "الرجاء اختيار معاملة للتحديث")
        except ValueError:
            QMessageBox.warning(self, "خطأ", "الرجاء إدخال رقم صحيح في حقل المبلغ")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")

    def delete_transaction(self):
        try:
            selected_row = self.table.currentRow()
            if selected_row >= 0:
                transaction_id = int(self.table.item(selected_row, 0).text())
                reply = QMessageBox.question(self, "تأكيد", 
                                          "هل أنت متأكد من حذف هذه المعاملة؟",
                                          QMessageBox.StandardButton.Yes | 
                                          QMessageBox.StandardButton.No)
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.cursor.execute("DELETE FROM transactions WHERE id=?", 
                                      (transaction_id,))
                    self.conn.commit()
                    self.load_data()
                    self.clear_inputs()
                    QMessageBox.information(self, "نجاح", "تم حذف المعاملة بنجاح")
            else:
                QMessageBox.warning(self, "تنبيه", "الرجاء اختيار معاملة للحذف")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")

    def export_to_excel(self):
        try:
            self.cursor.execute("SELECT * FROM transactions")
            data = self.cursor.fetchall()
            df = pd.DataFrame(data, columns=["ID", "التاريخ", "الوصف", "المبلغ", 
                                           "النوع", "الفئة"])
            df.to_excel("financial_report.xlsx", index=False)
            QMessageBox.information(self, "نجاح", 
                                  "تم تصدير البيانات إلى ملف Excel بنجاح")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء التصدير: {str(e)}")

    def select_row(self):
        try:
            selected_row = self.table.currentRow()
            self.description_input.setText(self.table.item(selected_row, 2).text())
            self.amount_input.setText(self.table.item(selected_row, 3).text())
            self.type_input.setText(self.table.item(selected_row, 4).text())
            self.category_input.setText(self.table.item(selected_row, 5).text())
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في تحديد الصف: {str(e)}")

    def clear_inputs(self):
        self.description_input.clear()
        self.amount_input.clear()
        self.type_input.clear()
        self.category_input.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FinancialManager()
    window.show()
    sys.exit(app.exec())
