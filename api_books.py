"""Open Library 도서 검색 기능: tkinter 공부 타이머에 메뉴로 추가한다.

Python 표준 라이브러리만 사용한다. API 키는 필요 없다.
"""

from __future__ import annotations

import json
import re
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_ENDPOINT = "https://openlibrary.org/search.json"


def search_books(keyword: str) -> list[dict[str, str]]:
    """검색어와 관련된 도서 최대 다섯 권의 공개 서지 정보를 가져온다."""
    keyword = keyword.strip()
    if not keyword:
        raise ValueError("검색어를 입력해 주세요.")

    params = urlencode({
        "q": keyword,
        "fields": "key,title,author_name,first_publish_year",
        "limit": 5,
    })
    request = Request(
        f"{API_ENDPOINT}?{params}",
        headers={
            "User-Agent": "StudyTimeRecorder/1.1 (educational book search)",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=8) as response:
        payload = json.load(response)

    if not isinstance(payload, dict) or not isinstance(payload.get("docs"), list):
        raise ValueError("API 응답 형식이 올바르지 않습니다.")

    books: list[dict[str, str]] = []
    for item in payload["docs"]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "제목 없음")
        authors = item.get("author_name")
        author = ", ".join(str(a) for a in authors[:2]) if isinstance(authors, list) else "저자 미상"
        year = str(item.get("first_publish_year") or "미상")
        key = str(item.get("key") or "")
        work_id = key.rsplit("/", 1)[-1]
        url = f"https://openlibrary.org/works/{work_id}" if re.fullmatch(r"OL\d+W", work_id) else ""
        books.append({"title": title, "author": author or "저자 미상", "year": year, "url": url})
    return books


def open_book_search(root: tk.Misc) -> None:
    """공부 중인 주제와 관련된 도서를 검색하는 별도의 창을 연다."""
    window = tk.Toplevel(root)
    window.title("학습 도서 검색 · Open Library API")
    window.geometry("840x420")
    window.minsize(630, 340)

    tk.Label(window, text="학습 주제로 도서 찾기", font=("맑은 고딕", 16, "bold")).pack(pady=(14, 3))
    tk.Label(window, text="예: Python, Quantum Computing, Calculus  |  API 키 불필요").pack(pady=(0, 10))

    form = ttk.Frame(window, padding=(12, 0))
    form.pack(fill="x")
    query = ttk.Entry(form)
    query.pack(side="left", fill="x", expand=True, padx=(0, 8))
    query.insert(0, "Python")
    search_button = ttk.Button(form, text="도서 검색")
    search_button.pack(side="left")

    columns = ("title", "author", "year")
    table_frame = ttk.Frame(window, padding=(12, 10))
    table_frame.pack(fill="both", expand=True)
    table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
    for column, heading, width in (
        ("title", "도서 제목", 360), ("author", "저자", 250), ("year", "첫 출판 연도", 105)
    ):
        table.heading(column, text=heading)
        table.column(column, width=width, minwidth=85, stretch=True)
    scroll = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)
    table.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    status = tk.StringVar(value="검색어를 입력하고 [도서 검색]을 눌러 주세요.")
    ttk.Label(window, textvariable=status, padding=(12, 0)).pack(anchor="w")
    current_books: list[dict[str, str]] = []

    def apply_results(books: list[dict[str, str]] | None, error: str = "") -> None:
        if not window.winfo_exists():
            return
        search_button.configure(state="normal")
        for row in table.get_children():
            table.delete(row)
        current_books.clear()
        if error:
            status.set(f"검색 실패: {error}  |  인터넷 연결을 확인해 주세요.")
            return
        current_books.extend(books or [])
        for index, book in enumerate(current_books):
            table.insert("", "end", iid=str(index), values=(book["title"], book["author"], book["year"]))
        status.set(f"검색 완료: {len(current_books)}권" if current_books else "검색된 도서가 없습니다.")

    def run_search() -> None:
        keyword = query.get().strip()
        if not keyword:
            messagebox.showwarning("검색어 필요", "검색어를 입력해 주세요.", parent=window)
            return
        search_button.configure(state="disabled")
        status.set("Open Library API에서 도서를 검색하고 있습니다...")

        # 네트워크 지연 중에도 타이머 GUI가 멈추지 않도록 별도 스레드 사용.
        def worker() -> None:
            try:
                result = search_books(keyword)
                try:
                    root.after(0, lambda: apply_results(result))
                except RuntimeError:
                    pass
            except Exception as exc:  # HTTP 오류·시간 초과·JSON 오류를 UI에 표시
                error = str(exc)
                try:
                    root.after(0, lambda: apply_results(None, error))
                except RuntimeError:
                    pass

        threading.Thread(target=worker, daemon=True).start()

    def open_selected() -> None:
        selection = table.selection()
        if not selection:
            messagebox.showinfo("도서 선택", "먼저 도서를 선택해 주세요.", parent=window)
            return
        book = current_books[int(selection[0])]
        if not book["url"]:
            messagebox.showinfo("링크 없음", "이 도서에는 연결할 페이지가 없습니다.", parent=window)
            return
        webbrowser.open(book["url"])

    search_button.configure(command=run_search)
    query.bind("<Return>", lambda _event: run_search())
    table.bind("<Double-1>", lambda _event: open_selected())
    ttk.Button(window, text="선택한 도서 페이지 열기", command=open_selected).pack(pady=10)
    query.focus_set()


def attach_book_search(root: tk.Misc) -> None:
    """기존 타이머 창 레이아웃을 바꾸지 않고 API 메뉴를 추가한다."""
    existing = root.cget("menu")
    if existing:
        menu = root.nametowidget(existing)
    else:
        menu = tk.Menu(root)
        root.configure(menu=menu)

    api_menu = tk.Menu(menu, tearoff=False)
    api_menu.add_command(label="학습 도서 검색 (Ctrl+B)", command=lambda: open_book_search(root))
    menu.add_cascade(label="학습 API", menu=api_menu)
    root.bind("<Control-b>", lambda _event: open_book_search(root))
