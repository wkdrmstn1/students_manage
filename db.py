import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '20011030', 
    'db': 'academydb',
    'charset': 'utf8'
}


class DB:
    def __init__(self, **kwargs):
        self.config = kwargs

    def connect(self):
        return pymysql.connect(**self.config)

    def fetch_students(self):
        try:
            with self.connect() as con:
                with con.cursor() as cur:
                    sql = "SELECT id, school, grade, name, date, d_date, commit, etc FROM students ORDER BY name"
                    cur.execute(sql)
                    return cur.fetchall()
        except Exception as e:
            print(f"학생 목록 로드 실패: {e}")
            return []

    def add_student(self, school, grade, name, date, d_date, commit):
        """새로운 학생을 추가합니다."""
        try:
            with self.connect() as con:
                with con.cursor() as cur:
                    sql = "INSERT INTO students (school, grade, name, date, d_date, commit, etc) VALUES (%s, %s, %s, %s, %s, %s, '')"
                    cur.execute(sql, (school, grade, name, date, d_date, commit))
                con.commit()
            return True
        except Exception as e:
            print(f"학생 추가 실패: {e}")
            return False

    def update_student(self, student_id, school, grade, name, date, d_date, commit):
        """학생 정보를 수정합니다."""
        try:
            with self.connect() as con:
                with con.cursor() as cur:
                    sql = "UPDATE students SET school=%s, grade=%s, name=%s, date=%s, d_date=%s, commit=%s WHERE id=%s"
                    cur.execute(sql, (school, grade, name, date, d_date, commit, student_id))
                con.commit()
            return True
        except Exception as e:
            print(f"학생 수정 실패: {e}")
            return False

    def delete_student(self, student_id):
        """학생을 삭제합니다."""
        try:
            with self.connect() as con:
                with con.cursor() as cur:
                    sql = "DELETE FROM students WHERE id=%s"
                    cur.execute(sql, (student_id,))
                con.commit()
            return True
        except Exception as e:
            print(f"학생 삭제 실패: {e}")
            return False

    def update_memo(self, student_id, memo):
        """특이사항 메모를 업데이트합니다."""
        try:
            with self.connect() as con:
                with con.cursor() as cur:
                    sql = "UPDATE students SET etc=%s WHERE id=%s"
                    cur.execute(sql, (memo, student_id))
                con.commit()
            return True
        except Exception as e:
            print(f"메모 업데이트 실패: {e}")
            return False