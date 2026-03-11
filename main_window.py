import sys
import datetime
from dateutil.relativedelta import relativedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
from db import DB, DB_CONFIG 
from memo_dialog import MemoDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("학원생 관리 프로그램")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("QMainWindow { font-size: 11pt; }")

        self.db = DB(**DB_CONFIG)
        self.selected_student_id = None

        # --- UI 구성 ---
        central = QWidget()
        self.setCentralWidget(central)
        main_vbox = QVBoxLayout(central)

        # 입력 폼 레이아웃 (Grid)
        form_grid = QGridLayout()
        form_grid.addWidget(QLabel("학교:"), 0, 0); self.input_school = QLineEdit()
        form_grid.addWidget(self.input_school, 0, 1)
        form_grid.addWidget(QLabel("학년:"), 0, 2); self.input_grade = QSpinBox(); self.input_grade.setRange(1, 6)
        form_grid.addWidget(self.input_grade, 0, 3)
        form_grid.addWidget(QLabel("이름:"), 1, 0); self.input_name = QLineEdit()
        form_grid.addWidget(self.input_name, 1, 1)
        form_grid.addWidget(QLabel("결제여부:"), 1, 2); self.combo_commit = QComboBox(); self.combo_commit.addItems(["미납", "완납"])
        form_grid.addWidget(self.combo_commit, 1, 3)
        form_grid.addWidget(QLabel("등록일:"), 2, 0); self.input_reg_date = QDateEdit(QDate.currentDate()); self.input_reg_date.setCalendarPopup(True)
        self.input_reg_date.setDisplayFormat("yyyy-MM-dd")
        form_grid.addWidget(self.input_reg_date, 2, 1)
        form_grid.addWidget(QLabel("결제일:"), 2, 2); self.input_due_date = QDateEdit(QDate.currentDate().addMonths(1)); self.input_due_date.setCalendarPopup(True)
        self.input_due_date.setDisplayFormat("yyyy-MM-dd")
        form_grid.addWidget(self.input_due_date, 2, 3)
        form_grid.setColumnStretch(1, 1); form_grid.setColumnStretch(3, 1)
        
        # 버튼 레이아웃
        button_box = QHBoxLayout()
        self.btn_add = QPushButton("추가")
        self.btn_update = QPushButton("수정")
        self.btn_delete = QPushButton("삭제")
        self.btn_refresh = QPushButton("월 갱신") # '새로고침' -> '월 갱신'
        button_box.addStretch(1)
        button_box.addWidget(self.btn_add); button_box.addWidget(self.btn_update)
        button_box.addWidget(self.btn_delete); button_box.addWidget(self.btn_refresh)
        
        # 테이블 위젯
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "학교", "학년", "이름", "등록일", "결제일", "결제여부", "특이사항"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False); self.table.setColumnHidden(0, True)
        header = self.table.horizontalHeader(); header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)

        # 전체 조립
        main_vbox.addLayout(form_grid)
        main_vbox.addLayout(button_box)
        main_vbox.addWidget(self.table)

        # 시그널 연결
        self.table.cellClicked.connect(self.cell_clicked)
        self.btn_add.clicked.connect(self.add_student)
        self.btn_update.clicked.connect(self.update_student)
        self.btn_delete.clicked.connect(self.delete_student)
        self.btn_refresh.clicked.connect(self.process_monthly_billing) # 새로고침 -> 월 갱신 기능 연결
        
        self.load_data()

    def load_data(self):
        self.table.clearSelection()
        rows = self.db.fetch_students()
        self.table.setRowCount(len(rows))
        today = datetime.date.today()
        for r_idx, row_data in enumerate(rows):
            student_id, _, _, _, _, due_date_str, commit_status, _ = row_data
            for c_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                item.setTextAlignment(Qt.AlignCenter)
                if c_idx == 6:
                    if commit_status == "완납": item.setBackground(QColor('#ccffcc'))
                    elif commit_status == "미납":
                        try:
                            due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
                            days_overdue = (today - due_date).days
                            if days_overdue > 0:
                                clamped_days = min(days_overdue, 30); intensity = max(100, 204 - clamped_days * 4)
                                item.setBackground(QColor(255, intensity, intensity))
                            else: item.setBackground(QColor('#ffcccb'))
                        except ValueError: item.setBackground(QColor('#ffcccb'))
                self.table.setItem(r_idx, c_idx, item)
            btn_memo = QPushButton("메모")
            btn_memo.clicked.connect(lambda _, sid=student_id: self.open_memo_dialog(sid))
            self.table.setCellWidget(r_idx, 7, btn_memo)
        self.clear_inputs()

    def cell_clicked(self, row, col):
        self.selected_student_id = int(self.table.item(row, 0).text())
        self.input_school.setText(self.table.item(row, 1).text())
        self.input_grade.setValue(int(self.table.item(row, 2).text()))
        self.input_name.setText(self.table.item(row, 3).text())
        reg_date = QDate.fromString(self.table.item(row, 4).text(), "yyyy-MM-dd")
        due_date = QDate.fromString(self.table.item(row, 5).text(), "yyyy-MM-dd")
        self.input_reg_date.setDate(reg_date); self.input_due_date.setDate(due_date)
        self.combo_commit.setCurrentText(self.table.item(row, 6).text())

    def clear_inputs(self):
        self.selected_student_id = None
        self.input_school.clear(); self.input_name.clear()
        self.input_grade.setValue(1); self.combo_commit.setCurrentIndex(0)
        self.input_reg_date.setDate(QDate.currentDate())
        self.input_due_date.setDate(QDate.currentDate().addMonths(1))
        self.table.clearSelection()

    def add_student(self):
        school = self.input_school.text().strip(); grade = self.input_grade.value()
        name = self.input_name.text().strip(); commit = self.combo_commit.currentText()
        if not school or not name:
            QMessageBox.warning(self, "입력 오류", "학교와 이름은 반드시 입력해야 합니다.")
            return
        today = datetime.date.today(); reg_date = today.strftime("%Y-%m-%d")
        due_date = (today + relativedelta(months=1)).strftime("%Y-%m-%d")
        ok = self.db.add_student(school, grade, name, reg_date, due_date, commit)
        if ok: self.load_data()
        else: QMessageBox.critical(self, "실패", "학생 정보 추가에 실패했습니다.")
            
    def update_student(self):
        if self.selected_student_id is None:
            QMessageBox.warning(self, "선택 오류", "먼저 테이블에서 수정할 학생을 선택하세요.")
            return
        school = self.input_school.text().strip(); grade = self.input_grade.value()
        name = self.input_name.text().strip(); reg_date = self.input_reg_date.date().toString("yyyy-MM-dd")
        new_commit = self.combo_commit.currentText()
        if not school or not name:
            QMessageBox.warning(self, "입력 오류", "학교와 이름은 반드시 입력해야 합니다.")
            return
        row = self.table.currentRow(); original_commit = self.table.item(row, 6).text()
        due_date = self.input_due_date.date().toString("yyyy-MM-dd")
        if original_commit == "미납" and new_commit == "완납":
            today = datetime.date.today()
            due_date = (today + relativedelta(months=1)).strftime("%Y-%m-%d")
        ok = self.db.update_student(self.selected_student_id, school, grade, name, reg_date, due_date, new_commit)
        if ok: self.load_data()
        else: QMessageBox.critical(self, "실패", "학생 정보 수정에 실패했습니다.")

    def delete_student(self):
        if self.selected_student_id is None:
            QMessageBox.warning(self, "선택 오류", "먼저 테이블에서 삭제할 학생을 선택하세요.")
            return
        school = self.input_school.text(); grade = self.input_grade.text(); name = self.input_name.text()
        reply = QMessageBox.question(self, '삭제 확인', f"학교: {school}\n학년: {grade}\n이름: {name}\n\n이 학생의 정보를 정말 삭제하시겠습니까?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok = self.db.delete_student(self.selected_student_id)
            if ok: self.load_data()
            else: QMessageBox.critical(self, "실패", "학생 정보 삭제에 실패했습니다.")

    def open_memo_dialog(self, student_id):
        current_memo = ""
        rows = self.db.fetch_students()
        for row in rows:
            if row[0] == student_id: current_memo = row[7]; break
        dialog = MemoDialog(current_memo, self)
        if dialog.exec_() == QDialog.Accepted:
            new_memo = dialog.get_text(); ok = self.db.update_memo(student_id, new_memo)
            if ok: self.load_data()
            else: QMessageBox.critical(self, "실패", "메모 저장에 실패했습니다.")

    # main_window.py의 MainWindow 클래스 내부에 있는 함수

    # main_window.py의 MainWindow 클래스 내부에 있는 함수

    def process_monthly_billing(self):
        """'월 갱신' 버튼 기능: '완납' 학생 명단을 확인 창에 보여주고, 동의 시 '미납'으로 변경"""
        
        # 1. DB에서 '완납' 상태인 학생들을 미리 찾습니다.
        all_students = self.db.fetch_students()
        paid_students = []
        for student in all_students:
            # student[6]은 '결제여부' 컬럼을 의미합니다.
            if student[6] == "완납":
                paid_students.append(student)

        # 2. 갱신할 학생이 없는 경우, 알림 후 함수를 종료합니다.
        if not paid_students:
            QMessageBox.information(self, "알림", "갱신할 '완납' 상태의 학생이 없습니다.")
            return

        # 3. 확인 메시지에 학생 명단을 포함하여 보여줍니다.
        # student[3]은 '이름' 컬럼을 의미합니다.
        names_to_update_str = "\n".join([student[3] for student in paid_students])
        confirmation_message = f"아래 학생들을 다음 달 청구 대상('미납')으로 변경하시겠습니까?\n\n{names_to_update_str}"
        
        reply = QMessageBox.question(self, '월 갱신 확인', confirmation_message,
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # 4. 사용자가 'Yes'를 누른 경우에만 업데이트를 진행합니다.
        if reply == QMessageBox.Yes:
            updated_students_names = []
            today = datetime.date.today()
            next_due_date = (today + relativedelta(months=1)).strftime("%Y-%m-%d")
            
            # 미리 찾아둔 '완납' 학생들만 순회하며 업데이트합니다.
            for student in paid_students:
                student_id, school, grade, name, reg_date, _, _, _ = student
                ok = self.db.update_student(student_id, school, grade, name, reg_date, next_due_date, "미납")
                if ok:
                    updated_students_names.append(name)
            
            # 최종 완료 메시지 (명단 포함)
            if updated_students_names:
                names_str = "\n".join(updated_students_names)
                QMessageBox.information(self, "월 갱신 완료", f"아래 학생들의 정보가 갱신되었습니다:\n\n{names_str}")
            
            self.load_data()