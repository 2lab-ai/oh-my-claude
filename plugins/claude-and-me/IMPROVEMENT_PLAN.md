# Claude-and-Me 개선 계획서

> **Version**: 1.0
> **Date**: 2026-01-23
> **Current Version**: 1.0.30
> **Author**: Claude Code Analysis

---

## 목차

1. [현재 상태 분석](#1-현재-상태-분석)
2. [Phase 1: 성능 최적화](#2-phase-1-성능-최적화)
3. [Phase 2: 안정성 강화](#3-phase-2-안정성-강화)
4. [Phase 3: 기능 확장](#4-phase-3-기능-확장)
5. [Phase 4: 개발자 경험](#5-phase-4-개발자-경험)
6. [구현 로드맵](#6-구현-로드맵)
7. [기술 부채](#7-기술-부채)

---

## 1. 현재 상태 분석

### 1.1 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ SessionEnd Event                                         ││
│  │   └─► transcript_path, session_id, fork_info            ││
│  └─────────────────────────────────────────────────────────┘│
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                claude-and-me.py (701 lines)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Config Mgr   │  │ Raw Log Mgr  │  │ Chat Log Gen │      │
│  │              │  │              │  │              │      │
│  │ - JSON 로드   │  │ - 중복제거    │  │ - MD/JSON    │      │
│  │ - 기본값      │  │ - 라인비교    │  │ - 헤더생성    │      │
│  │ - 경로해석    │  │ - 날짜이동    │  │ - 요약생성    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Output Files                            │
│  .claude/                                                    │
│  ├── raw_logs/                                              │
│  │   └── YYYY-MM-DD/                                        │
│  │       └── {session_id}.jsonl                             │
│  └── chat_logs/                                             │
│      ├── YYYY-MM-DD/                                        │
│      │   └── {session_id}.YYYY-MM-DD.HH_mm_ss.md           │
│      └── .summaries/                                        │
│          └── {session_id}.json                              │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 핵심 기능

| 기능 | 설명 | 상태 |
|------|------|------|
| Raw Log 관리 | JSONL 원본 백업, 라인 기반 중복 제거 | ✅ 완료 |
| Chat Log 변환 | Markdown/JSON 형식 변환 | ✅ 완료 |
| 세션 연속성 | 동일 세션 재개 시 이전 파일 연결 | ✅ 완료 |
| Fork 지원 | 분기 세션 부모 참조 유지 | ✅ 완료 |
| Progressive Headers | 저장 횟수에 따른 동적 헤더 | ✅ 완료 |
| 요약 생성 | Claude CLI를 통한 자동 요약 | ✅ 완료 (선택적) |
| UUID 중복제거 | 메시지 UUID 기반 방어적 처리 | ✅ 완료 |

### 1.3 현재 제한사항

#### 성능 관련
- `subprocess.run()` + `find` 명령어로 파일 탐색 (5초 타임아웃)
- 요약 생성이 동기/순차 방식 (블로킹)
- 대용량 세션에서 전체 파일 재파싱

#### 안정성 관련
- 에러 발생 시 무음 실패 (로그만 기록)
- 출력 파일 권한 사전 검증 없음
- 프로세스 인터럽트 시 정리 로직 없음

#### 기능 관련
- 제한된 콘텐츠 타입 지원 (텍스트, thinking, tool_use만)
- 이미지/파일 참조 미지원
- 검색/필터링 기능 없음

---

## 2. Phase 1: 성능 최적화

> **목표**: 훅 실행 시간 50% 단축, 리소스 사용 최적화
> **우선순위**: 높음
> **예상 복잡도**: 중간

### 2.1 파일 탐색 최적화

#### 현재 구현
```python
# 현재: subprocess + find 명령어
def find_files(pattern):
    result = subprocess.run(
        ["find", base_dir, "-name", pattern],
        capture_output=True, timeout=5
    )
    return result.stdout.decode().strip().split('\n')
```

#### 개선 방안
```python
# 개선: pathlib + glob 사용
from pathlib import Path

def find_files(base_dir: Path, pattern: str) -> list[Path]:
    """Pure Python 파일 탐색"""
    return list(base_dir.glob(f"**/{pattern}"))

# 또는 캐시 적용
from functools import lru_cache

@lru_cache(maxsize=128)
def find_files_cached(base_dir: str, pattern: str) -> tuple[str, ...]:
    """캐시된 파일 탐색 (세션 내 재사용)"""
    return tuple(str(p) for p in Path(base_dir).glob(f"**/{pattern}"))
```

#### 작업 목록
- [ ] `find_previous_files()` 함수를 `pathlib.glob()` 기반으로 변경
- [ ] `find_raw_log_file()` 함수 개선
- [ ] subprocess 의존성 제거 (find 명령)
- [ ] 단위 테스트 추가

### 2.2 요약 생성 비동기화

#### 현재 구현
```python
# 현재: 동기 순차 처리
for file in previous_files:
    summary = generate_summary(file)  # 블로킹 (30초 타임아웃)
    summaries.append(summary)
```

#### 개선 방안
```python
# 개선안 A: concurrent.futures 사용
from concurrent.futures import ThreadPoolExecutor, as_completed

def generate_summaries_parallel(files: list[str], max_workers: int = 3):
    """병렬 요약 생성"""
    summaries = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(generate_summary, f): f
            for f in files
        }
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                summaries[file] = future.result(timeout=30)
            except Exception as e:
                summaries[file] = f"Summary unavailable: {e}"
    return summaries
```

```python
# 개선안 B: asyncio 기반 (더 현대적)
import asyncio

async def generate_summary_async(file: str) -> str:
    """비동기 요약 생성"""
    proc = await asyncio.create_subprocess_exec(
        "claude", "-p", "--model", model, "--no-session-persistence", prompt,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
    return stdout.decode().strip()

async def generate_all_summaries(files: list[str]):
    """모든 요약 동시 생성"""
    tasks = [generate_summary_async(f) for f in files]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

#### 작업 목록
- [ ] `generate_summary()` 함수 비동기 버전 구현
- [ ] 최대 동시 요청 수 설정 옵션 추가
- [ ] 요약 실패 시 graceful fallback
- [ ] 테스트 및 벤치마크

### 2.3 증분 파싱

#### 현재 구현
```python
# 현재: 전체 파일 파싱 후 skip_count로 필터링
def parse_messages(transcript_path, skip_count=0):
    messages = []
    for i, line in enumerate(open(transcript_path)):
        if i < skip_count:
            continue
        messages.append(json.loads(line))
    return messages
```

#### 개선 방안
```python
# 개선: seek으로 직접 위치 이동
def parse_messages_incremental(transcript_path: str, start_line: int = 0):
    """증분 메시지 파싱 (새 라인만 처리)"""
    messages = []
    with open(transcript_path) as f:
        # 이전 라인 건너뛰기 (최적화된 방식)
        for _ in range(start_line):
            f.readline()

        # 새 라인만 처리
        for line in f:
            if line.strip():
                messages.append(json.loads(line))

    return messages
```

#### 작업 목록
- [ ] 라인 오프셋 기반 증분 파싱 구현
- [ ] 메모리 사용량 최적화
- [ ] 대용량 파일 스트리밍 처리

---

## 3. Phase 2: 안정성 강화

> **목표**: 에러 복구율 향상, 데이터 무결성 보장
> **우선순위**: 중간
> **예상 복잡도**: 중간

### 3.1 에러 처리 강화

#### 개선 방안
```python
from dataclasses import dataclass
from enum import Enum
import sys

class ErrorSeverity(Enum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class HookResult:
    success: bool
    message: str
    severity: ErrorSeverity = ErrorSeverity.WARNING

    def to_hook_response(self) -> str:
        """Claude Code 훅 응답 형식"""
        if self.success:
            return json.dumps({"continue": True})
        return json.dumps({
            "continue": True,  # 훅 실패해도 세션은 유지
            "message": f"[{self.severity.value}] {self.message}"
        })

def run_with_recovery(func, *args, max_retries=3, **kwargs):
    """재시도 로직이 포함된 실행"""
    last_error = None
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            log_error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # exponential backoff

    return HookResult(
        success=False,
        message=f"Failed after {max_retries} attempts: {last_error}",
        severity=ErrorSeverity.ERROR
    )
```

#### 작업 목록
- [ ] `HookResult` 데이터 클래스 도입
- [ ] 재시도 로직 구현 (exponential backoff)
- [ ] 에러 분류 및 심각도 레벨 정의
- [ ] 사용자 알림 메커니즘 (stderr로 메시지 출력)

### 3.2 권한 및 경로 검증

#### 개선 방안
```python
from pathlib import Path
import os

def validate_output_path(path: Path) -> tuple[bool, str]:
    """출력 경로 사전 검증"""
    # 부모 디렉토리 존재 확인
    parent = path.parent
    if not parent.exists():
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            return False, f"Cannot create directory: {parent}"

    # 쓰기 권한 확인
    if not os.access(parent, os.W_OK):
        return False, f"No write permission: {parent}"

    # 기존 파일인 경우 쓰기 가능 확인
    if path.exists() and not os.access(path, os.W_OK):
        return False, f"Cannot overwrite file: {path}"

    return True, "OK"

def safe_write(path: Path, content: str) -> HookResult:
    """안전한 파일 쓰기 (atomic write)"""
    valid, msg = validate_output_path(path)
    if not valid:
        return HookResult(False, msg, ErrorSeverity.ERROR)

    # Atomic write: 임시 파일에 쓰고 이동
    temp_path = path.with_suffix(path.suffix + '.tmp')
    try:
        temp_path.write_text(content, encoding='utf-8')
        temp_path.rename(path)
        return HookResult(True, f"Written: {path}")
    except Exception as e:
        temp_path.unlink(missing_ok=True)
        return HookResult(False, str(e), ErrorSeverity.ERROR)
```

#### 작업 목록
- [ ] `validate_output_path()` 함수 구현
- [ ] Atomic write 패턴 적용
- [ ] 디스크 공간 확인 로직 추가
- [ ] 경로 순회 공격 방지 (path traversal)

### 3.3 Graceful Shutdown

#### 개선 방안
```python
import signal
import atexit
from contextlib import contextmanager

class HookState:
    """훅 실행 상태 관리"""
    def __init__(self):
        self.temp_files: list[Path] = []
        self.partial_writes: list[Path] = []
        self._shutdown = False

    def register_temp_file(self, path: Path):
        self.temp_files.append(path)

    def cleanup(self):
        """정리 작업 실행"""
        if self._shutdown:
            return
        self._shutdown = True

        for path in self.temp_files:
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass

        for path in self.partial_writes:
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass

_state = HookState()

def setup_signal_handlers():
    """시그널 핸들러 설정"""
    def handler(signum, frame):
        _state.cleanup()
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)
    atexit.register(_state.cleanup)

@contextmanager
def tracked_write(path: Path):
    """추적되는 파일 쓰기 컨텍스트"""
    _state.partial_writes.append(path)
    try:
        yield
        _state.partial_writes.remove(path)
    except Exception:
        raise
```

#### 작업 목록
- [ ] `HookState` 클래스 구현
- [ ] SIGTERM, SIGINT 핸들러 등록
- [ ] atexit 정리 로직 추가
- [ ] 컨텍스트 매니저로 리소스 관리

### 3.4 데이터 무결성 검증

#### 개선 방안
```python
import hashlib

def compute_checksum(content: str) -> str:
    """SHA-256 체크섬 계산"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

def write_with_checksum(path: Path, content: str):
    """체크섬 포함 파일 쓰기"""
    checksum = compute_checksum(content)

    # 체크섬을 파일 끝에 주석으로 추가
    if path.suffix == '.md':
        content_with_checksum = f"{content}\n\n<!-- checksum: {checksum} -->\n"
    elif path.suffix == '.json':
        # JSON의 경우 메타데이터에 포함
        data = json.loads(content)
        data['_checksum'] = checksum
        content_with_checksum = json.dumps(data, ensure_ascii=False, indent=2)
    else:
        content_with_checksum = content

    path.write_text(content_with_checksum, encoding='utf-8')

def verify_checksum(path: Path) -> bool:
    """파일 체크섬 검증"""
    content = path.read_text(encoding='utf-8')

    if path.suffix == '.md':
        match = re.search(r'<!-- checksum: ([a-f0-9]+) -->\s*$', content)
        if not match:
            return True  # 체크섬 없으면 검증 스킵
        stored = match.group(1)
        actual_content = re.sub(r'\n\n<!-- checksum: [a-f0-9]+ -->\s*$', '', content)
        return compute_checksum(actual_content) == stored

    return True
```

#### 작업 목록
- [ ] 체크섬 계산 함수 구현
- [ ] 출력 파일에 체크섬 포함
- [ ] 읽기 시 체크섬 검증 옵션
- [ ] 손상 파일 감지 및 리포트

---

## 4. Phase 3: 기능 확장

> **목표**: 사용자 요구 기능 추가, 유연성 향상
> **우선순위**: 낮음
> **예상 복잡도**: 높음

### 4.1 커스텀 헤더 템플릿

#### 개선 방안
```python
from jinja2 import Environment, BaseLoader

DEFAULT_HEADER_TEMPLATE = """
# Chat Log: {{ date }}{% if is_fork %} (Forked){% endif %}

{% if history_table %}
| No | Date | Link | Summary |
|---|---|---|---|
{% for entry in history %}
| {{ entry.number }} | {{ entry.date }} | [{{ entry.filename }}]({{ entry.path }}) | {{ entry.summary }} |
{% endfor %}
{% elif previous_file %}
> **Started from**: [{{ previous_file.name }}]({{ previous_file.path }})
{% endif %}

{% if is_fork %}
**Forked from session**: `{{ parent_session_id }}`
{% endif %}

Session: `{{ session_id }}`

---
"""

class HeaderGenerator:
    def __init__(self, template: str = None):
        self.env = Environment(loader=BaseLoader())
        self.template = self.env.from_string(template or DEFAULT_HEADER_TEMPLATE)

    def render(self, **context) -> str:
        return self.template.render(**context).strip()
```

**설정 파일 확장:**
```json
{
  "header_template": "path/to/custom_header.j2",
  "header_variables": {
    "project_name": "My Project",
    "team": "DevOps"
  }
}
```

#### 작업 목록
- [ ] Jinja2 의존성 추가
- [ ] 기본 템플릿 분리
- [ ] 커스텀 템플릿 로드 로직
- [ ] 템플릿 유효성 검증
- [ ] 문서화

### 4.2 검색 및 인덱스

#### 개선 방안
```python
import sqlite3
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SearchResult:
    session_id: str
    file_path: str
    date: datetime
    snippet: str
    relevance: float

class SessionIndex:
    """세션 로그 검색 인덱스"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    date TEXT NOT NULL,
                    content TEXT NOT NULL,
                    UNIQUE(session_id, file_path)
                )
            """)
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts
                USING fts5(session_id, content, content=sessions, content_rowid=id)
            """)

    def index_file(self, session_id: str, file_path: Path):
        """파일을 인덱스에 추가"""
        content = file_path.read_text()
        date = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sessions (session_id, file_path, date, content)
                VALUES (?, ?, ?, ?)
            """, (session_id, str(file_path), date, content))

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """전문 검색"""
        with sqlite3.connect(self.db_path) as conn:
            results = conn.execute("""
                SELECT s.session_id, s.file_path, s.date,
                       snippet(sessions_fts, 1, '<mark>', '</mark>', '...', 32) as snippet,
                       bm25(sessions_fts) as relevance
                FROM sessions_fts
                JOIN sessions s ON sessions_fts.rowid = s.id
                WHERE sessions_fts MATCH ?
                ORDER BY relevance
                LIMIT ?
            """, (query, limit)).fetchall()

        return [
            SearchResult(r[0], r[1], datetime.fromisoformat(r[2]), r[3], r[4])
            for r in results
        ]
```

#### 작업 목록
- [ ] SQLite FTS5 기반 인덱스 구현
- [ ] 자동 인덱싱 (훅 실행 시)
- [ ] CLI 검색 명령 추가
- [ ] 날짜/세션 필터링

### 4.3 내보내기 형식

#### 개선 방안
```python
from abc import ABC, abstractmethod

class Exporter(ABC):
    @abstractmethod
    def export(self, content: str, output_path: Path) -> None:
        pass

class HTMLExporter(Exporter):
    """HTML 내보내기"""

    def export(self, content: str, output_path: Path):
        import markdown
        html_content = markdown.markdown(
            content,
            extensions=['tables', 'fenced_code', 'codehilite']
        )

        html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Chat Log</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; }}
        pre {{ background: #f4f4f4; padding: 16px; overflow-x: auto; }}
        code {{ background: #f4f4f4; padding: 2px 6px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

        output_path.write_text(html_doc)

class PDFExporter(Exporter):
    """PDF 내보내기"""

    def export(self, content: str, output_path: Path):
        # weasyprint 또는 pdfkit 사용
        from weasyprint import HTML

        html_exporter = HTMLExporter()
        temp_html = output_path.with_suffix('.html.tmp')
        html_exporter.export(content, temp_html)

        HTML(str(temp_html)).write_pdf(str(output_path))
        temp_html.unlink()

# 팩토리 함수
def get_exporter(format: str) -> Exporter:
    exporters = {
        'html': HTMLExporter,
        'pdf': PDFExporter,
    }
    return exporters[format]()
```

#### 작업 목록
- [ ] `Exporter` 인터페이스 정의
- [ ] HTML 내보내기 구현
- [ ] PDF 내보내기 구현 (선택적 의존성)
- [ ] CLI 내보내기 명령 추가

### 4.4 필터링 및 쿼리

#### 개선 방안
```python
from dataclasses import dataclass
from datetime import date
from typing import Optional
import fnmatch

@dataclass
class FilterOptions:
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    session_pattern: Optional[str] = None  # glob pattern
    content_keyword: Optional[str] = None
    message_type: Optional[str] = None  # user, assistant, all

class SessionFilter:
    def __init__(self, options: FilterOptions):
        self.options = options

    def filter_files(self, files: list[Path]) -> list[Path]:
        """파일 목록 필터링"""
        result = files

        if self.options.date_from or self.options.date_to:
            result = [f for f in result if self._check_date(f)]

        if self.options.session_pattern:
            result = [f for f in result
                      if fnmatch.fnmatch(f.stem, self.options.session_pattern)]

        if self.options.content_keyword:
            result = [f for f in result
                      if self.options.content_keyword.lower() in f.read_text().lower()]

        return result

    def _check_date(self, file: Path) -> bool:
        """날짜 범위 확인"""
        # 파일명에서 날짜 추출: session_id.YYYY-MM-DD.HH_mm_ss.md
        try:
            parts = file.stem.split('.')
            if len(parts) >= 2:
                file_date = date.fromisoformat(parts[1])
                if self.options.date_from and file_date < self.options.date_from:
                    return False
                if self.options.date_to and file_date > self.options.date_to:
                    return False
        except ValueError:
            return True  # 날짜 파싱 실패 시 포함
        return True
```

#### 작업 목록
- [ ] `FilterOptions` 데이터 클래스 구현
- [ ] 날짜 범위 필터
- [ ] 세션 ID 패턴 매칭
- [ ] 콘텐츠 키워드 검색
- [ ] CLI 필터 옵션 추가

### 4.5 타임존 지원

#### 개선 방안
```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

class DateTimeHandler:
    def __init__(self, tz: str = None):
        if tz:
            self.tz = ZoneInfo(tz)
        else:
            # 시스템 로컬 타임존 감지
            self.tz = datetime.now().astimezone().tzinfo

    def now(self) -> datetime:
        """현재 시간 (타임존 인식)"""
        return datetime.now(self.tz)

    def format_date(self, dt: datetime = None) -> str:
        """날짜 형식화 (YYYY-MM-DD)"""
        dt = dt or self.now()
        return dt.strftime('%Y-%m-%d')

    def format_time(self, dt: datetime = None) -> str:
        """시간 형식화 (HH_mm_ss)"""
        dt = dt or self.now()
        return dt.strftime('%H_%M_%S')

    def to_utc(self, dt: datetime) -> datetime:
        """UTC로 변환"""
        return dt.astimezone(timezone.utc)
```

**설정 파일 확장:**
```json
{
  "timezone": "Asia/Seoul",
  "date_format": "%Y-%m-%d",
  "time_format": "%H_%M_%S"
}
```

#### 작업 목록
- [ ] `DateTimeHandler` 클래스 구현
- [ ] 설정에서 타임존 읽기
- [ ] 기존 코드 마이그레이션
- [ ] UTC 저장 + 로컬 표시 옵션

---

## 5. Phase 4: 개발자 경험

> **목표**: 테스트 품질 향상, 모니터링 추가, CLI 개선
> **우선순위**: 지속적
> **예상 복잡도**: 낮음-중간

### 5.1 테스트 강화

#### Property-Based Testing
```python
from hypothesis import given, strategies as st

@given(
    session_id=st.text(min_size=1, max_size=100),
    content=st.text(min_size=0, max_size=10000),
    message_count=st.integers(min_value=0, max_value=100)
)
def test_roundtrip_parsing(session_id, content, message_count):
    """파싱 왕복 테스트"""
    # 메시지 생성 -> 파싱 -> 검증
    messages = generate_test_messages(message_count, content)
    transcript = create_transcript(messages)
    parsed = parse_transcript(transcript)
    assert len(parsed) == message_count
```

#### 성능 벤치마크
```python
import pytest

@pytest.mark.benchmark
def test_large_session_performance(benchmark):
    """대용량 세션 처리 성능"""
    # 1000개 메시지 세션 생성
    large_transcript = create_large_transcript(1000)

    result = benchmark(process_session, large_transcript)

    # 성능 기준
    assert benchmark.stats['mean'] < 5.0  # 5초 이내

@pytest.mark.benchmark
def test_summary_generation_performance(benchmark):
    """요약 생성 성능 (mock)"""
    with mock.patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = b"Summary text"

        result = benchmark(generate_summaries, test_files)

        assert benchmark.stats['mean'] < 1.0  # 1초 이내 (mock)
```

#### 작업 목록
- [ ] hypothesis 기반 property test 추가
- [ ] pytest-benchmark 도입
- [ ] 엣지 케이스 테스트 (유니코드, 대용량, 빈 파일)
- [ ] 코드 커버리지 90% 이상 유지

### 5.2 모니터링 및 통계

#### 개선 방안
```python
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class SessionStats:
    """세션 처리 통계"""
    session_id: str
    timestamp: datetime
    message_count: int
    raw_log_size: int
    chat_log_size: int
    dedup_ratio: float  # 중복 제거율
    processing_time_ms: int
    summary_generated: bool
    errors: list[str] = field(default_factory=list)

class StatsCollector:
    """통계 수집기"""

    def __init__(self, stats_file: Path):
        self.stats_file = stats_file
        self.current: SessionStats = None

    def start_session(self, session_id: str):
        self.current = SessionStats(
            session_id=session_id,
            timestamp=datetime.now(),
            message_count=0,
            raw_log_size=0,
            chat_log_size=0,
            dedup_ratio=0.0,
            processing_time_ms=0,
            summary_generated=False
        )
        self._start_time = datetime.now()

    def end_session(self):
        if self.current:
            elapsed = datetime.now() - self._start_time
            self.current.processing_time_ms = int(elapsed.total_seconds() * 1000)
            self._save()

    def _save(self):
        """통계를 파일에 추가"""
        stats = []
        if self.stats_file.exists():
            stats = json.loads(self.stats_file.read_text())

        stats.append({
            'session_id': self.current.session_id,
            'timestamp': self.current.timestamp.isoformat(),
            'message_count': self.current.message_count,
            'raw_log_size': self.current.raw_log_size,
            'chat_log_size': self.current.chat_log_size,
            'dedup_ratio': self.current.dedup_ratio,
            'processing_time_ms': self.current.processing_time_ms,
            'summary_generated': self.current.summary_generated,
            'errors': self.current.errors
        })

        # 최근 1000개만 유지
        stats = stats[-1000:]
        self.stats_file.write_text(json.dumps(stats, indent=2))

    def get_summary(self) -> dict:
        """전체 통계 요약"""
        if not self.stats_file.exists():
            return {}

        stats = json.loads(self.stats_file.read_text())
        if not stats:
            return {}

        return {
            'total_sessions': len(stats),
            'total_messages': sum(s['message_count'] for s in stats),
            'total_storage_kb': sum(s['raw_log_size'] + s['chat_log_size'] for s in stats) // 1024,
            'avg_processing_time_ms': sum(s['processing_time_ms'] for s in stats) // len(stats),
            'avg_dedup_ratio': sum(s['dedup_ratio'] for s in stats) / len(stats),
            'error_count': sum(len(s['errors']) for s in stats)
        }
```

#### 작업 목록
- [ ] `StatsCollector` 클래스 구현
- [ ] 훅 실행 시 자동 통계 수집
- [ ] CLI 통계 조회 명령 추가
- [ ] 대시보드 출력 (선택적)

### 5.3 CLI 인터페이스 개선

#### 개선 방안
```python
import argparse

def create_cli():
    parser = argparse.ArgumentParser(
        prog='claude-and-me',
        description='Claude Code 세션 아카이버'
    )

    subparsers = parser.add_subparsers(dest='command')

    # 수동 처리 명령
    process_parser = subparsers.add_parser('process', help='세션 수동 처리')
    process_parser.add_argument('transcript', help='Transcript 파일 경로')
    process_parser.add_argument('--dry-run', action='store_true', help='실제 파일 생성 없이 미리보기')
    process_parser.add_argument('--format', choices=['md', 'json'], default='md')

    # 검색 명령
    search_parser = subparsers.add_parser('search', help='세션 검색')
    search_parser.add_argument('query', help='검색 쿼리')
    search_parser.add_argument('--from', dest='date_from', help='시작 날짜 (YYYY-MM-DD)')
    search_parser.add_argument('--to', dest='date_to', help='종료 날짜 (YYYY-MM-DD)')

    # 통계 명령
    stats_parser = subparsers.add_parser('stats', help='통계 조회')
    stats_parser.add_argument('--json', action='store_true', help='JSON 형식 출력')

    # 내보내기 명령
    export_parser = subparsers.add_parser('export', help='세션 내보내기')
    export_parser.add_argument('session_id', help='세션 ID')
    export_parser.add_argument('--format', choices=['html', 'pdf'], required=True)
    export_parser.add_argument('--output', '-o', help='출력 파일 경로')

    return parser

def main():
    parser = create_cli()
    args = parser.parse_args()

    if args.command == 'process':
        process_transcript(args.transcript, dry_run=args.dry_run, format=args.format)
    elif args.command == 'search':
        search_sessions(args.query, date_from=args.date_from, date_to=args.date_to)
    elif args.command == 'stats':
        show_stats(json_format=args.json)
    elif args.command == 'export':
        export_session(args.session_id, format=args.format, output=args.output)
    else:
        # 기본 동작: stdin에서 훅 페이로드 읽기
        run_hook()
```

#### 작업 목록
- [ ] argparse 기반 CLI 구현
- [ ] `--dry-run` 모드 추가
- [ ] 하위 명령 구조 (process, search, stats, export)
- [ ] 도움말 및 사용 예시

---

## 6. 구현 로드맵

### 6.1 단기 (1-2주)

| 우선순위 | 작업 | 복잡도 | 영향도 |
|---------|------|--------|--------|
| 🔴 P0 | pathlib 기반 파일 탐색 전환 | 낮음 | 높음 |
| 🔴 P0 | 에러 처리 구조화 (HookResult) | 낮음 | 중간 |
| 🟡 P1 | 재시도 로직 추가 | 낮음 | 중간 |
| 🟡 P1 | 권한 검증 함수 추가 | 낮음 | 중간 |

### 6.2 중기 (2-4주)

| 우선순위 | 작업 | 복잡도 | 영향도 |
|---------|------|--------|--------|
| 🟡 P1 | 비동기 요약 생성 | 중간 | 높음 |
| 🟡 P1 | Graceful shutdown | 중간 | 중간 |
| 🟢 P2 | 체크섬 검증 | 낮음 | 낮음 |
| 🟢 P2 | 통계 수집 | 중간 | 낮음 |

### 6.3 장기 (1-2개월)

| 우선순위 | 작업 | 복잡도 | 영향도 |
|---------|------|--------|--------|
| 🟢 P2 | 검색 인덱스 (SQLite FTS) | 높음 | 높음 |
| 🟢 P2 | HTML/PDF 내보내기 | 중간 | 중간 |
| 🔵 P3 | 커스텀 헤더 템플릿 | 중간 | 낮음 |
| 🔵 P3 | CLI 인터페이스 | 중간 | 낮음 |
| 🔵 P3 | 타임존 지원 | 낮음 | 낮음 |

---

## 7. 기술 부채

### 7.1 현재 기술 부채

| 항목 | 심각도 | 설명 |
|------|--------|------|
| subprocess 의존 | 중간 | find 명령어 대신 pathlib 사용 필요 |
| 동기 처리 | 중간 | 요약 생성의 블로킹 특성 |
| 하드코딩된 값 | 낮음 | 타임아웃, 최대 라인 수 등 상수화 필요 |
| 타입 힌트 불완전 | 낮음 | 일부 함수에 타입 힌트 누락 |

### 7.2 해결 계획

```
Phase 1 완료 시:
  - subprocess 의존 → 해결
  - 동기 처리 → 해결

Phase 2 완료 시:
  - 하드코딩된 값 → 해결 (설정으로 이동)

지속적:
  - 타입 힌트 → 점진적 추가
```

---

## 부록: 테스트 실행 방법

```bash
# 전체 테스트
uv run --with pytest pytest plugins/claude-and-me/tests/ -v

# 특정 테스트
uv run --with pytest pytest plugins/claude-and-me/tests/test_claude_and_me.py::TestNewSession -v

# 커버리지
uv run --with pytest,pytest-cov pytest plugins/claude-and-me/tests/ --cov=plugins/claude-and-me/hooks --cov-report=html

# 벤치마크 (추가 예정)
uv run --with pytest,pytest-benchmark pytest plugins/claude-and-me/tests/ --benchmark-only
```

---

*이 문서는 Claude Code에 의해 자동 생성되었습니다.*
