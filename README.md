# 공부 시간 기록 프로그램 — API 확장판

5주차에 제작한 Python `tkinter` 공부 시간 기록 프로그램에 **Open Library 도서 검색 API**를 추가했다. 공부 시간을 기록하면서 학습 주제와 관련된 도서를 바로 찾아볼 수 있다.

## 1. 실행 환경과 설치

- Python 3.12 이상 권장, [uv](https://docs.astral.sh/uv/) 설치
- Windows 등 `tkinter` GUI가 가능한 데스크톱 환경
- 기존 `pyproject.toml`과 `uv.lock`을 사용하므로 새 Python 패키지를 설치할 필요 없음

```powershell
# 공개 저장소이거나 접근 권한이 있는 GitHub 계정으로 실행
git clone https://github.com/dbcks2026/study-time-recoding-program.git
cd <저장소-폴더명>
uv sync
uv run python main.py
```

`git clone`이 `Repository not found`로 실패하면 저장소 주소, 공개 여부 및 GitHub 로그인 권한을 확인한다.

## 2. 주요 기능과 사용 방법

**기존 기능:** 할 일 입력 → 시작 버튼 → 타이머 측정 → 종료 버튼 → 공부 시간 기록 저장. 저장한 기록을 목록에서 확인하고 삭제할 수 있으며, 오늘의 총 공부 시간을 계산한다. 타이머가 실행 중일 때 창을 닫으면 저장하지 않은 시간이 있을 수 있다.

**추가 기능(API):** 프로그램 창 상단의 **학습 API → 학습 도서 검색**을 클릭한다. `Ctrl+B` 단축키로도 열 수 있다. `Python`, `Quantum Computing` 등 키워드를 입력하고 **도서 검색**을 누르면 Open Library에서 도서 최대 5권의 제목·저자·최초 출판 연도를 받아 목록으로 표시한다. 도서를 선택하고 **선택한 도서 페이지 열기**를 누르면 브라우저로 이동한다.

## 3. 코드 구조와 핵심 동작

| 파일 | 역할 |
|---|---|
| `main.py` | 기존 타이머·기록·GUI, 도서 검색 메뉴 등록 |
| `api_books.py` | API 요청, JSON 해석, 도서 검색 결과 창 |
| `api-plan.md` | API 적용 목적, 흐름 및 점검 항목 |
| `pyproject.toml`, `uv.lock` | UV 실행 환경 및 의존성 재현 |
| `.gitignore` | 가상환경·캐시·비밀키·로컬 기록 제외 |
| `conversation_history.md`, `AI_대화원문_추가.md` | AI 대화 원문 기록 (전체 기록 여부 확인 필요) |

API 검색 실행 흐름: `attach_book_search(root)`가 기존 창에 메뉴를 붙인다 → `open_book_search()`가 검색 창을 만든다 → `search_books()`가 `https://openlibrary.org/search.json`에 GET 요청을 보낸다 → JSON의 `docs`를 읽어 제목·저자·출판 연도·링크를 정리한다 → `tkinter.Treeview`에 출력한다. 네트워크 통신은 별도 스레드에서 실행하여 타이머 GUI가 멈추지 않도록 했다.

### 실패 처리 및 보안

- 검색어가 비어 있으면 입력 안내를 표시한다.
- 인터넷 연결이 끊기거나 API 응답이 실패하면 검색 창에 오류를 표시하며 타이머는 유지된다.
- **API Key는 필요 없다.** `.env` 파일을 만들 필요도 없고 별도로 제출할 키도 없다.
- 향후 키가 필요한 API를 사용할 경우 `.env`에 `API_KEY=발급받은_키` 형식으로 저장하고 GitHub에는 업로드하지 않는다.

## 4. 재현 테스트

```powershell
uv sync
uv run python -m unittest test_api_books.py -v
uv run python main.py
```

1. 공부할 일을 입력하여 타이머를 시작·종료하고 기록이 남는지 확인한다.
2. 학습 API 메뉴에서 `Python`을 검색해 결과가 나타나는지 확인한다.
3. 도서 선택 후 원본 Open Library 페이지가 열리는지 확인한다.
4. 인터넷이 끊어진 경우 검색 오류를 안내하고 타이머 기능은 유지되는지 확인한다.

**API 제공자:** Open Library (https://openlibrary.org/dev/docs/api/search).  교육용 낮은 빈도의 검색만 사용한다. API는 네트워크 연결이 있어야 동작한다.


## 5. GitHub 브랜치 업데이트

기존 저장소에서 새 기능 브랜치를 만들거나 `apiplan` 브랜치를 사용하고 API 코드와 문서를 커밋한 뒤 PR을 `main`으로 병합한다. 가상환경, `records.json`, 설치 ZIP, 백업 파일은 업로드하지 않는다. 제출 전 `git remote -v`와 `git status`를 확인한다.
