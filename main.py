import json
import os
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "records.json")


def format_seconds(seconds: int) -> str:
    """초를 HH:MM:SS 문자열로 변환합니다."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_total(seconds: int) -> str:
    """총 공부 시간을 한국어 형식으로 변환합니다."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    parts = []
    if h > 0:
        parts.append(f"{h}시간")
    if m > 0:
        parts.append(f"{m}분")
    if s > 0 or not parts:
        parts.append(f"{s}초")
    return " ".join(parts)


class StudyTimerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("공부 시간 기록 프로그램")
        self.root.geometry("480x540")
        self.root.resizable(False, False)

        self.records = self.load_records()
        self.is_running = False
        self.elapsed_seconds = 0
        self.timer_job = None

        self.setup_ui()
        self.refresh_records_view()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_records(self) -> list:
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_records(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)

    def setup_ui(self):
        font_main = ("Malgun Gothic", 10)
        font_bold = ("Malgun Gothic", 10, "bold")

        # 할 일 입력
        input_frame = tk.Frame(self.root, pady=10)
        input_frame.pack(fill="x", padx=15)
        tk.Label(input_frame, text="할 일:", font=font_bold).pack(side="left")
        self.task_entry = tk.Entry(input_frame, font=font_main)
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self.task_entry.bind("<Return>", lambda e: self.start_timer())

        # 타이머 표시
        self.timer_label = tk.Label(self.root, text="00:00:00", font=("Malgun Gothic", 32, "bold"), fg="#2c3e50")
        self.timer_label.pack(pady=5)

        # 시작/종료 버튼
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        self.start_btn = tk.Button(btn_frame, text="시작", width=12, font=font_bold, bg="#4CAF50", fg="white",
                                   command=self.start_timer, cursor="hand2")
        self.start_btn.pack(side="left", padx=6)
        self.stop_btn = tk.Button(btn_frame, text="종료", width=12, font=font_bold, bg="#e74c3c", fg="white",
                                  state="disabled", command=self.stop_timer, cursor="hand2")
        self.stop_btn.pack(side="left", padx=6)

        # 구분선 및 오늘의 총 시간
        tk.Frame(self.root, height=1, bg="#dcdcdc").pack(fill="x", padx=15, pady=10)
        self.total_label = tk.Label(self.root, text="오늘의 총 공부 시간: 0초", font=("Malgun Gothic", 11, "bold"), fg="#1a5276")
        self.total_label.pack(anchor="w", padx=15, pady=(0, 5))

        # 기록 목록 (Treeview)
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)
        self.tree = ttk.Treeview(list_frame, columns=("date", "task", "time"), show="headings", selectmode="browse", height=9)
        self.tree.heading("date", text="날짜")
        self.tree.heading("task", text="할 일")
        self.tree.heading("time", text="공부 시간")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("task", width=220, anchor="w")
        self.tree.column("time", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 삭제 버튼
        bottom_frame = tk.Frame(self.root, pady=8)
        bottom_frame.pack(fill="x", padx=15)
        self.del_btn = tk.Button(bottom_frame, text="선택한 기록 삭제", font=font_main, command=self.delete_record)
        self.del_btn.pack(side="right")

    def start_timer(self):
        if self.is_running:
            return
        task = self.task_entry.get().strip()
        if not task:
            messagebox.showwarning("입력 오류", "할 일을 입력해주세요.")
            return

        self.is_running = True
        self.elapsed_seconds = 0
        self.timer_label.config(text="00:00:00")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.task_entry.config(state="disabled")
        self.timer_job = self.root.after(1000, self.tick)

    def tick(self):
        if self.is_running:
            self.elapsed_seconds += 1
            self.timer_label.config(text=format_seconds(self.elapsed_seconds))
            self.timer_job = self.root.after(1000, self.tick)

    def stop_timer(self):
        if not self.is_running:
            return
        self.is_running = False
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        task = self.task_entry.get().strip()
        today_str = date.today().strftime("%Y-%m-%d")
        record = {
            "date": today_str,
            "task": task,
            "seconds": self.elapsed_seconds,
            "time_str": format_seconds(self.elapsed_seconds),
        }
        self.records.append(record)
        self.save_records()

        self.task_entry.config(state="normal")
        self.task_entry.delete(0, tk.END)
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.elapsed_seconds = 0
        self.timer_label.config(text="00:00:00")
        self.refresh_records_view()

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("알림", "삭제할 기록을 목록에서 선택해주세요.")
            return
        idx = int(self.tree.item(selected[0], "text"))
        del self.records[idx]
        self.save_records()
        self.refresh_records_view()

    def refresh_records_view(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        today_str = date.today().strftime("%Y-%m-%d")
        today_total = 0
        for i, r in enumerate(self.records):
            self.tree.insert("", "end", text=str(i), values=(r["date"], r["task"], r["time_str"]))
            if r.get("date") == today_str:
                today_total += r.get("seconds", 0)
        self.total_label.config(text=f"오늘의 총 공부 시간: {format_total(today_total)}")

    def on_close(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTimerApp(root)
    root.mainloop()
