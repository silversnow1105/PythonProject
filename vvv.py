import tkinter as tk
from tkinter import messagebox, simpledialog #정보 표시, 대화상자(입력받을때)
import calendar #tkinter gui 라이브러리에서 달력 위젯을 제공하는 라이브러리
import json #java script object notation의 약자 데이터 교환 형식, xml 형식보다 코딩을 적게 가능,처리속도 빠름
import os #operating system의 약자 운영체제, 시스템 제어 유용한 모듈, 파일/폴더 경로조작 및 존재여부 확인 또는 생성
from datetime import datetime #날짜와 시간 가져오기
import requests #http 요청을 보내고 응답을 받는데 사용되는 라이브러리

BASE_URL = "http://192.168.192.102:8000/" # FastAPI 서버가 실행될 주소

def load_json(filename):
    if not os.path.exists(filename): #파일경로
        return {}
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


TODO_FILE = "todo.json"
DIARY_FILE = "diary.json"
TIMETABLE_FILE = "timetable.json"
NOTICE_FILE = "notice.json"

#로그인과 회원가입을 위한 창을 만드는 클래스
class LoginApp:
    #Gui 창 초기화를 위한 생성자 메서드
    def __init__(self, root):
        self.root = root
        self.root.title("로그인")
        self.root.geometry("300x200")

        tk.Label(root, text="아이디", font=("맑은 고딕", 12)).pack(pady=5)
        self.id_entry = tk.Entry(root, font=("맑은 고딕", 12))
        self.id_entry.pack()

        tk.Label(root, text="비밀번호", font=("맑은 고딕", 12)).pack(pady=5)
        self.pw_entry = tk.Entry(root, show="*", font=("맑은 고딕", 12))
        self.pw_entry.pack()

        tk.Button(root, text="로그인", font=("맑은 고딕", 12), command=self.login).pack(pady=5)
        tk.Button(root, text="회원가입", font=("맑은 고딕", 12), command=self.signup).pack()
    #로그인 데이터 입력 받고 요청 처리하는 메서드
    def login(self):
        uid = self.id_entry.get().strip()
        pw = self.pw_entry.get().strip()

        if not uid or not pw:
            messagebox.showerror("로그인 실패", "아이디와 비밀번호를 모두 입력해주세요.")
            return

        try:
            response = requests.post(f"{BASE_URL}/login", json={"username": uid, "password": pw})
            response_data = response.json()

            if response.status_code == 200:
                messagebox.showinfo("로그인 성공", response_data["message"])
                self.show_main(response_data["username"], response_data["role"])
            else:
                messagebox.showerror("로그인 실패", response_data.get("detail", "알 수 없는 오류 발생"))

        except requests.exceptions.ConnectionError:
            messagebox.showerror("연결 오류", "서버에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인하세요.")
        except Exception as e:
            messagebox.showerror("오류", f"로그인 중 오류 발생: {e}")
    #회원가입 데이터 입력받고 요청 처리하는 메서드
    def signup(self):
        uid = simpledialog.askstring("회원가입", "아이디를 입력하세요.")
        if not uid:
            return

        pw = simpledialog.askstring("회원가입", "비밀번호를 입력하세요.", show="*")
        if not pw:
            return

        admin_password_attempt = None

        ask_admin_pw = messagebox.askyesno("관리자 등록", "관리자로 회원가입 하시겠습니까? (관리자 비밀번호 필요)")
        if ask_admin_pw:
            admin_password_attempt = simpledialog.askstring("관리자 등록", "관리자 비밀번호를 입력하세요.", show="*")
            if not admin_password_attempt:
                messagebox.showwarning("회원가입 취소", "관리자 비밀번호 입력이 취소되었습니다.")
                return

        payload = {"username": uid, "password": pw}
        if admin_password_attempt:
            payload["admin_password_attempt"] = admin_password_attempt

        try:
            response = requests.post(f"{BASE_URL}/register", json=payload)
            response_data = response.json()

            if response.status_code == 200:
                messagebox.showinfo("회원가입 성공", response_data["message"])
            else:
                messagebox.showerror("회원가입 실패", response_data.get("detail", "알 수 없는 오류 발생"))

        except requests.exceptions.ConnectionError:
            messagebox.showerror("연결 오류", "서버에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인하세요.")
        except Exception as e:
            messagebox.showerror("오류", f"회원가입 중 오류 발생: {e}")
    #로그인 성공시 메인화면 창으로 이동하게 하는 메서드
    def show_main(self, uid, role):
        self.root.destroy()
        root = tk.Tk()
        app = MainApp(root, uid, role)
        root.mainloop()

#메인앱 클래스
class MainApp:
    #이앱의 시작 생성자, 모든 기능을 연결, 인터페이스 초기화
    def __init__(self, root, uid, role):
        self.root = root
        self.uid = uid
        self.role = role
        self.root.title(f"메인 - {uid}({role})")
        self.root.geometry("700x450")
        self.setup_ui()
    #메인메뉴 버튼 구성
    def setup_ui(self):
        menu = tk.Frame(self.root)
        menu.pack(pady=10)
        tk.Button(menu, text="공지 달력", font=("맑은 고딕", 12), command=self.open_notice).pack(side=tk.LEFT, padx=5)
        tk.Button(menu, text="투두리스트", font=("맑은 고딕", 12), command=self.open_todo).pack(side=tk.LEFT, padx=5)
        tk.Button(menu, text="일기장", font=("맑은 고딕", 12), command=self.open_diary).pack(side=tk.LEFT, padx=5)
        tk.Button(menu, text="시간표", font=("맑은 고딕", 12), command=self.open_timetable).pack(side=tk.LEFT, padx=5)
        tk.Button(menu, text="게시판", font=("맑은 고딕", 12), command=self.open_board).pack(side=tk.LEFT, padx=5)
        if self.role == "admin":
            tk.Button(menu, text="관리자 승인", font=("맑은 고딕", 12), command=self.open_approval).pack(side=tk.LEFT, padx=5)
    #기능메서드
    def open_notice(self):
        win = tk.Toplevel(self.root)
        NoticeCalendarApp(win, self.uid, self.role)
    def open_todo(self):
        win = tk.Toplevel(self.root)
        TodoApp(win, self.uid)
    def open_diary(self):
        win = tk.Toplevel(self.root)
        DiaryApp(win, self.uid)
    def open_timetable(self):
        win = tk.Toplevel(self.root)
        TimetableApp(win, self.uid)
    def open_approval(self):
        win = tk.Toplevel(self.root)
        ApprovalApp(win)
    def open_board(self):
        win = tk.Toplevel(self.root)
        BoardApp(win, self.uid)

#공지앱
class NoticeCalendarApp:#공지 달력을 생성하고 관리하는 역할
    #공지앱 class의 생성자
    def __init__(self, root, uid, role): #생성자 메서드
        self.root = root #tkinter의 메인 윈도우, 속성초기화
        self.uid = uid #사용자 ID, 속성 초기화
        self.role = role #사용자 역할 (관리자인지 일반 사용자인지), 속성 초기화
        self.root.title("공지 달력") #공지달력으로 설정
        self.root.geometry("500x500") #크기를 500x500 픽셀

        self.notices = {}#공지 데이터를 저장할 빈 딕셔너리를 만듬
        self.load_notices() #공지 데이터를 저장할 빈 딕셔너리를 만들고, load_notices()를 호출해 서버에서 공지 데이터를 가져옴

        now = datetime.now() #현재 날짜 정보를 가져오기
        self.current_year = now.year #현재 연도
        self.current_month = now.month #현재 월

        self.setup_ui() #setup_ui() 호출
    #tkcalendar.calendar위젯 생성 달력을 화면 표시
    def load_notices(self):#공지 데이터를 서버에서 가져오는 메서드
        try:
            response = requests.get(f"{BASE_URL}/notices") #서버에서 공지를 가져옴
            self.notices = response.json() #self.notice에 저장함
        except: #오류가 발생하면
            self.notices = {} #빈 딕셔너리로 설정
    #공지사항을서버에서get을이용하여불러오는메서드
    def setup_ui(self): #ui를 구성하는 메서드
        self.lbl = tk.Label(self.root, text="공지 달력 - 공지 날짜는 * 표시", font=("맑은 고딕", 14))
        self.lbl.pack(pady=5) #제목 라벨을 생성하고 화면에 배치합니다,
        self.draw_calendar() #달력을 화면에 표시하는 draw_calendar()
    #실제 달력 화면을 그리는 메서드, 공지 있는 날짜는 *표시
    def draw_calendar(self): #실제 달력을 화면에 그리는 메서드
        if hasattr(self, 'calendar_frame'):
            self.calendar_frame.destroy() #기존 달력 프레임이 있으면 제거

        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack() #새로운 프레임을 생성하고 배치합니다.

        nav = tk.Frame(self.calendar_frame) #달력의 네비게이션(이전/다음 달 이동 버튼)을 포함할 프레임을 생성
        nav.grid(row=0, column=0, columnspan=7)
        tk.Button(nav, text="◀", command=self.prev_month).pack(side="left")
        tk.Label(nav, text=f"{self.current_year}년 {self.current_month}월", font=("Arial", 12)).pack(side="left", padx=10)
        tk.Button(nav, text="▶", command=self.next_month).pack(side="left")#이전 달, 현재 달 표시, 다음 달 이동 버튼을 생성

        days = ['월', '화', '수', '목', '금', '토', '일']
        for i, d in enumerate(days):
            tk.Label(self.calendar_frame, text=d, font=("맑은 고딕", 11, "bold")).grid(row=1, column=i)
            #요일을 표시하는 라벨을 생성
        cal = calendar.Calendar() #달력 객체를 생성
        row = 2
        for week in cal.monthdayscalendar(self.current_year, self.current_month): #달력의 주(week)를 반복하면서 각 날짜를 배치
            for col, day in enumerate(week):
                if day == 0:
                    tk.Label(self.calendar_frame, text="").grid(row=row, column=col) #해당 주에 날짜가 없는 셀(빈칸)을 채움
                else:
                    date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}" #날짜를 문자열(string) 형태로 변환하는 코드

                    label = f"{day}*" if date_str in self.notices else str(day)#공지사항이 등록된 날짜는 * 표시를 붙임
                    btn = tk.Button(self.calendar_frame, text=label, #각 날짜에 버튼을 추가해 클릭 가능하게 만듬

                                    command=lambda d=date_str: self.on_date_click(d)) #- 버튼을 클릭하면 해당 날짜 정보(date_str)를 on_date_click() 메서드로 전달하여 공지 확인 또는 등록 기능이 실행

                    btn.grid(row=row, column=col, padx=2, pady=2) #부분은 버튼을 배치
            row += 1 #다음줄로 이동
    #날짜 클릭시 호출되는 핵심 메서드
    def on_date_click(self, date_str): #날짜 버튼을 클릭했을 때 실행되는 메서드
        if self.role == "admin": #사용자가 관리자일 경우 추가적인 기능을 제공
            if date_str in self.notices:
                overwrite = messagebox.askyesno("공지 존재", #날짜를 클릭했을 때, 해당 날짜에 이미 공지가 등록되어 있다면 사용자에게 새 공지를 덮어쓸 것인지 확인하는 메시지를 표시
                                                f"{date_str}에 등록된 공지가 있습니다:\n\n{self.notices[date_str]}\n\n새 공지를 등록하시겠습니까?")
                if not overwrite:
                    return #사용자가 덮어쓰기를 원하지 않으면 메서드를 종료
            content = simpledialog.askstring("공지 추가", f"{date_str} 공지 내용을 입력하세요:") #새로운 공지 내용을 입력받는 다이얼로그를 띄움
            if content:
                try:
                    response = requests.post(f"{BASE_URL}/notices", json={
                        "date": date_str,
                        "content": content
                    }) #사용자가 내용을 입력하면, 이를 서버에 POST 요청을 통해 저장
                    if response.status_code == 200: #200은 요청이 성공적으로 처리되었음을 의미

                        messagebox.showinfo("등록 완료", "공지 등록이 완료되었습니다.")
                        self.load_notices()
                        self.draw_calendar() #공지 등록이 성공하면 사용자에게 알림을 표시하고, 공지 데이터를 다시 로드한 후 달력을 새로 그림
                    else:
                        messagebox.showerror("실패", "공지 등록에 실패했습니다.") #공지 등록이 실패하면 오류 메시지를 표시
                except Exception as e:
                    messagebox.showerror("오류", f"서버 요청 실패: {e}") #예외 처리 코드입니다. 서버 요청 과정에서 오류가 발생하면 사용자에게 알림을 제공
        else:
            if date_str in self.notices:
                messagebox.showinfo("공지 내용", f"{date_str} 공지:\n\n{self.notices[date_str]}") #관리자가 아닌 경우, 사용자가 공지를 클릭하면 해당 날짜의 공지 내용을 보여줌
            else:
                messagebox.showinfo("공지 없음", f"{date_str}에는 공지가 없습니다.") #해당 날짜에 공지가 없는 경우, 없다는 메시지를 표시
    #달력에서 이전달/다음달로 이동할 수 있도록
    #현재 년/월 조정하고 draw_calender()다시호출
    def prev_month(self): #이전 달로 이동하는 메서드
        if self.current_month == 1:#현재 월이 1월이면 연도를 하나 줄이고 월을 12월로 변경
            self.current_month = 12 #그 외의 경우, 월을 하나 감소
            self.current_year -= 1 #변경된 월을 반영해 다시 달력을 그림
        else:
            self.current_month -= 1 #1월 이면 연도를 줄임
        self.draw_calendar()
    def next_month(self): #다음 달로 이동하는 메서드
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1 #현재 월이 12월이면 연도를 하나 증가시키고 월을 1월로 변경
        else:
            self.current_month += 1 #그 외의 경우, 월을 하나 증가
        self.draw_calendar() #변경된 월을 반영해 다시 달력을 그림


#객세속성저장
class TodoApp:
    #유저 인터페이스를 설정
    def __init__(self, root, uid):
        self.root = root
        self.uid = uid
        self.root.title(f"{uid}님의 투두리스트")
        self.root.geometry("420x400")
        self.todo_data = load_json(TODO_FILE)
        if self.uid not in self.todo_data:
            self.todo_data[self.uid] = []
        self.setup_ui()
    #화면을 새로고침(변경된 내용을 가져와 반영)
    def setup_ui(self):
        self.task_frame = tk.Frame(self.root)
        self.task_frame.pack(pady=10)

        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=5)

        self.entry = tk.Entry(input_frame, width=25, font=("맑은 고딕", 12))
        self.entry.pack(side=tk.LEFT, padx=5)

        tk.Button(input_frame, text="추가", font=("맑은 고딕", 12), command=self.add_todo).pack(side=tk.LEFT)

        self.refresh()
    #입력창에 입력된 텍스트 가져와 할일에 추가
    def refresh(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.todo_data[self.uid]):
            row = tk.Frame(self.task_frame)
            row.pack(fill="x", pady=2)

            var = tk.BooleanVar(value=item.get("done", False))

            cb = tk.Checkbutton(row, variable=var, command=lambda i=idx, v=var: self.toggle_done(i, v))
            cb.pack(side=tk.LEFT)

            lbl = tk.Label(row, text=item["task"], font=("맑은 고딕", 12))
            lbl.pack(side=tk.LEFT, padx=5)
            if item.get("done"):
                lbl.config(fg="#999999")
            else:
                lbl.config(fg="#000000")

            del_btn = tk.Button(row, text="삭제", font=("맑은 고딕", 10),
                                command=lambda i=idx: self.delete_task(i))
            del_btn.pack(side=tk.RIGHT)
    #입력창에 입력된 텍스트를 가져와 할 일에 추가
    def add_todo(self):
        task = self.entry.get().strip()
        if not task:
            return
        self.todo_data[self.uid].append({"task": task, "done": False})
        save_json(TODO_FILE, self.todo_data)
        self.entry.delete(0, tk.END)
        self.refresh()
    #클릭된 항목의 done 값을 변경
    def toggle_done(self, idx, var):
        self.todo_data[self.uid][idx]["done"] = var.get()
        save_json(TODO_FILE, self.todo_data)
        self.refresh()
    #'삭제' 버튼을 누르면 실행되어 해당 할 일 데이터 삭제
    def delete_task(self, idx):
        del self.todo_data[self.uid][idx]
        save_json(TODO_FILE, self.todo_data)
        self.refresh()

#일기장을 만들기 위한 클래스 정의
class DiaryApp:
    #diaryapp 클래스의 생성자
    def __init__(self, root, uid):
        self.root = root
        self.uid = uid
        self.root.title(f"{uid}님의 일기장")
        self.root.geometry("500x500")

        self.diary_data = load_json(DIARY_FILE)

        if self.uid not in self.diary_data:
            self.diary_data[self.uid] = {}

        self.setup_ui()
    #일기 내용을 사용자의 화면에 표시하는 메서드
    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="날짜 (YYYY-MM-DD)", font=("맑은 고딕", 12)).pack(side=tk.LEFT)
        self.date_entry = tk.Entry(top_frame, font=("맑은 고딕", 12), width=15)
        self.date_entry.pack(side=tk.LEFT, padx=5)

        load_btn = tk.Button(top_frame, text="📅", font=("맑은 고딕", 14), command=self.show_diary)
        load_btn.pack(side=tk.LEFT, padx=5)

        self.display_frame = tk.Frame(self.root, relief=tk.SOLID, borderwidth=1)
        self.display_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.date_label = tk.Label(self.display_frame, font=("맑은 고딕", 20, "bold"), fg="black")
        self.date_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.content_text = tk.Text(self.display_frame, font=("맑은 고딕", 12), wrap=tk.WORD, height=10)
        self.content_text.pack(padx=10, pady=(5, 10), fill=tk.BOTH, expand=True)

        tk.Button(self.root, text="저장", font=("맑은 고딕", 12), command=self.save_diary).pack()
        tk.Button(self.root, text="일기 목록 보기", font=("맑은 고딕", 12), command=self.show_diary_list).pack(pady=(5, 0))
    #사용자가 작성한 모든 일기 목록을 한눈에 보여주는 기능
    def show_diary(self):
        date = self.date_entry.get().strip()
        if not date:
            messagebox.showerror("오류", "날짜를 입력하세요.")
            return
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("오류", "날짜 형식이 올바르지 않습니다.")
            return

        content = self.diary_data[self.uid].get(date, "")
        self.date_label.config(text=date)
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert(tk.END, content if content else "")
    #사용자가 작성한 일기 내용을 지정된 파일(json)에 저장하는 메서드
    def save_diary(self):
        date = self.date_entry.get().strip()
        if not date:
            messagebox.showerror("오류", "날짜를 입력하세요.")
            return
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("오류", "날짜 형식이 올바르지 않습니다.")
            return

        content = self.content_text.get("1.0", tk.END).strip()
        self.diary_data[self.uid][date] = content
        save_json(DIARY_FILE, self.diary_data)

        messagebox.showinfo("저장 완료", "일기가 저장되었습니다.")
    #Tkinter의 Listbox에서 항목을 선택했을 때 자동으로 실행되는 함수
    def show_diary_list(self):
        if not self.diary_data[self.uid]:
            messagebox.showinfo("알림", "작성된 일기가 없습니다.")
            return

        list_window = tk.Toplevel(self.root)
        list_window.title("일기 목록")
        list_window.geometry("300x400")

        tk.Label(list_window, text="작성된 일기 목록", font=("맑은 고딕", 14, "bold")).pack(pady=10)

        sorted_dates = sorted(self.diary_data[self.uid].keys())

        listbox = tk.Listbox(list_window, font=("맑은 고딕", 12))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for date in sorted_dates:
            preview = self.diary_data[self.uid][date].strip().split('\n')[0][:20]
            listbox.insert(tk.END, f"{date} - {preview}")

        def on_select(event):
            selection = listbox.curselection()
            if selection:
                selected = listbox.get(selection[0])
                selected_date = selected.split(' - ')[0]
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, selected_date)
                self.show_diary()
                list_window.destroy()

        listbox.bind("<<ListboxSelect>>", on_select)

#시간표를 만들기 위한 클래스
class TimetableApp:
    #TimetableApp 클래스의 생성자
    def __init__(self, root, uid):
        self.root = root
        self.uid = uid
        self.root.title("시간표")
        self.root.geometry("800x600")

        self.time_slots = self.generate_time_slots()
        self.days = ["월", "화", "수", "목", "금"]

        self.timetable_data = load_json(TIMETABLE_FILE)

        if self.uid not in self.timetable_data:
            self.timetable_data[self.uid] = {day: [""] * len(self.time_slots) for day in self.days}

        self.setup_ui()
    #시간 슬롯(교시, 시간 등)을 자동으로 생성하는 함수
    def generate_time_slots(self):
        times = []
        hour = 9
        minute = 0
        while hour < 18:
            times.append(f"{hour:02}:{minute:02}")
            minute += 30
            if minute == 60:
                minute = 0
                hour += 1
        return times
    #TimetableApp 클래스 내부에서 GUI를 구성하는 메서드
    def setup_ui(self):
        self.entries = {}
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        for i, day in enumerate(self.days):
            tk.Label(frame, text=day, font=("맑은 고딕", 12)).grid(row=0, column=i + 1, padx=5)

        for i, time in enumerate(self.time_slots):
            tk.Label(frame, text=time, font=("맑은 고딕", 10)).grid(row=i + 1, column=0, padx=5, sticky="e")

        for i, time in enumerate(self.time_slots):
            for j, day in enumerate(self.days):
                e = tk.Entry(frame, width=15, font=("맑은 고딕", 10))
                e.grid(row=i + 1, column=j + 1, padx=2, pady=1)
                e.insert(0, self.timetable_data[self.uid][day][i])
                self.entries[(day, i)] = e

        tk.Button(self.root, text="저장", font=("맑은 고딕", 12), command=self.save_timetable).pack(pady=10)
    #사용자가 입력한 시간표 데이터를 파일에 저장하는 기능
    def save_timetable(self):
        for (day, i), entry in self.entries.items():
            self.timetable_data[self.uid][day][i] = entry.get().strip()
        save_json(TIMETABLE_FILE, self.timetable_data)
        messagebox.showinfo("저장 완료", "시간표가 저장되었습니다.")


class ApprovalApp:
    #객체 속성 저장
    def __init__(self, root):
        self.root = root
        self.root.title("회원 승인")
        self.root.geometry("300x400")
        self.setup_ui()
    # 리스트 박스와 버튼을 생성하여 화면을 구성하는 메서드
    def setup_ui(self):
        self.listbox = tk.Listbox(self.root, width=30, height=15, font=("맑은 고딕", 12))
        self.listbox.pack(pady=10)
        tk.Button(self.root, text="승인", font=("맑은 고딕", 12), command=self.approve).pack(pady=5)
        self.refresh()
    #서버에서 승인 대기 중인 회원 목록을 가져와 리스트 박스에 표시하는 메서드
    def refresh(self):
        self.listbox.delete(0, tk.END)
        try:
            response = requests.get(f"{BASE_URL}/pending_approvals")
            response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생시킵니다.
            pending_users = response.json().get("pending_users", [])
            for uid in pending_users:
                self.listbox.insert(tk.END, uid)
        except requests.exceptions.ConnectionError:
            messagebox.showerror("연결 오류", "서버에 연결할 수 없습니다.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("오류", f"승인 대기 목록 불러오기 실패: {e}")
    #선택한 회원을 승인하는 기능을 수행하는 메서드
    def approve(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("선택 필요", "승인할 회원을 선택하세요.")
            return

        uid = self.listbox.get(sel[0])
        admin_pw = simpledialog.askstring("관리자 비밀번호", "관리자 비밀번호를 입력하세요:", show="*")
        if not admin_pw:
            return

        try:
            response = requests.post(f"{BASE_URL}/approve_user", json={"username": uid, "admin_password": admin_pw})
            response_data = response.json()

            if response.status_code == 200:
                messagebox.showinfo("승인 완료", response_data["message"])
                self.refresh()
            else:
                messagebox.showerror("승인 실패", response_data.get("detail", "알 수 없는 오류 발생"))
        except requests.exceptions.ConnectionError:
            messagebox.showerror("연결 오류", "서버에 연결할 수 없습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"승인 중 오류 발생: {e}")

#게시판의 메인 로직을 담당하는 클래스
class BoardApp:
    #App이 실행될 때 생성되는 생성자 메서드
    def __init__(self, root, uid):
        self.root = root
        self.uid = uid
        self.root.title("게시판")
        self.root.geometry("700x500")

        self.posts = []
        self.setup_ui()
        self.refresh()
    #GUI 요소(위젯)들을 화면에 배치하는 기능을 수행하는 메서드
    def setup_ui(self):
        self.listbox = tk.Listbox(self.root, font=("맑은 고딕", 12), height=15, width=90)
        self.listbox.pack(pady=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack()

        tk.Button(btn_frame, text="새 글 작성", command=self.new_post).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="내용 보기", command=self.view_post).pack(side=tk.LEFT, padx=5)
    #게시글 목록을 서버에서 가져와 화면에 갱신하는 메서드
    def refresh(self):
        try:
            response = requests.get(f"{BASE_URL}/posts")
            self.posts = response.json().get("posts", [])
        except:
            self.posts = []

        self.listbox.delete(0, tk.END)
        for i, post in enumerate(self.posts):
            like_count = len(post.get("likes", []))
            self.listbox.insert(tk.END, f"{i+1}. {post['title']} - {post['author']} ❤️{like_count}")
    #새 게시글을 사용자로부터 입력받고, 서버에 전송해등록하는 메서드
    def new_post(self):
        title = simpledialog.askstring("제목", "게시글 제목을 입력하세요:")
        if not title:
            return
        content = simpledialog.askstring("내용", "게시글 내용을 입력하세요:")
        if not content:
            return

        try:
            response = requests.post(f"{BASE_URL}/posts", json={
                "title": title,
                "content": content,
                "author": self.uid
            })
            if response.status_code == 200:
                messagebox.showinfo("성공", "게시글이 등록되었습니다.")
                self.refresh()
            else:
                messagebox.showerror("실패", "게시글 등록에 실패했습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"서버 요청 실패: {e}")
    #사용자가 선택한 게시글의 상세내용 표시하는 메서드
    def view_post(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("선택 필요", "확인할 게시글을 선택하세요.")
            return
        idx = sel[0]
        post = self.posts[idx]

        info = f"작성자: {post['author']}\n날짜: {post['datetime']}\n\n{post['content']}\n\n❤️ 좋아요: {len(post['likes'])}\n\n[댓글]"
        for c in post.get("comments", []):
            info += f"\n- {c['author']} ({c['datetime']}): {c['comment']}"

        def add_comment():
            comment = simpledialog.askstring("댓글", "댓글 내용을 입력하세요:")
            if comment:
                try:
                    response = requests.post(f"{BASE_URL}/posts/comment", json={
                        "post_id": idx,
                        "comment": comment,
                        "author": self.uid
                    })
                    if response.status_code == 200:
                        messagebox.showinfo("성공", "댓글이 등록되었습니다.")
                        self.refresh()
                        popup.destroy()
                        self.view_post()
                    else:
                        messagebox.showerror("실패", "댓글 등록에 실패했습니다.")
                except Exception as e:
                    messagebox.showerror("오류", f"서버 요청 실패: {e}")

        def like_post():
            try:
                response = requests.post(f"{BASE_URL}/posts/like", json={
                    "post_id": idx,
                    "user": self.uid
                })
                if response.status_code == 200:
                    messagebox.showinfo("성공", "좋아요 완료.")
                    self.refresh()
                    popup.destroy()
                    self.view_post()
                else:
                    messagebox.showerror("실패", response.json().get("detail", "요청 실패"))
            except Exception as e:
                messagebox.showerror("오류", f"서버 요청 실패: {e}")

        popup = tk.Toplevel(self.root)
        popup.title(post["title"])
        popup.geometry("500x500")

        tk.Label(popup, text=info, justify=tk.LEFT, wraplength=480, font=("맑은 고딕", 11)).pack(pady=10)
        tk.Button(popup, text="좋아요", command=like_post).pack(pady=3)
        tk.Button(popup, text="댓글 작성", command=add_comment).pack()



if __name__ == "__main__":
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()
