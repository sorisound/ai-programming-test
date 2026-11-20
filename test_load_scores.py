# test_load_scores.py
# 설계표(명세서 6칸만 보고 만든 여덟 케이스)를 pytest로 옮긴 것.
#   정상 ①②③ · 예외 ①② · 경계 ①②③(0 · 100 · 101)

import pytest

from load_scores import load_scores


def 쓰기(폴더, 점수):
    """헤더와 한 줄짜리 임시 CSV를 만들고 경로를 돌려준다."""
    경로 = 폴더 / "임시.csv"
    경로.write_text(f"name,score\n홍길동,{점수}\n", encoding="utf-8")
    return 경로


# ── 정상 ──────────────────────────────────────────────

def test_정상_파일을_읽는다():
    kept, skipped = load_scores("scores.csv")
    assert kept == [
        ("김하나", 88),
        ("최,네번", 77),
        ("김하나", 91),   # 동명이인일 수 있으므로 둘 다 남긴다
        ("윤보람", 64),
        ("서한별", 95),
    ]
    assert len(skipped) == 5


def test_빈_줄은_건너뛴다():
    kept, skipped = load_scores("scores.csv")
    # 10행은 빈 줄: 기록 없이 건너뛰고, 그 뒤 줄은 계속 읽는다
    assert 10 not in [줄번호 for 줄번호, _, _ in skipped]
    assert ("윤보람", 64) in kept


def test_이름에_쉼표가_있어도_읽는다():
    kept, skipped = load_scores("scores.csv")
    assert ("최,네번", 77) in kept


# ── 예외 ──────────────────────────────────────────────

def test_없는_파일이면_오류가_난다():
    with pytest.raises(FileNotFoundError):
        load_scores("없는파일.csv")


def test_헤더만_있으면_빈_결과():
    kept, skipped = load_scores("empty.csv")
    assert kept == []
    assert skipped == []


# ── 경계값 ────────────────────────────────────────────

@pytest.mark.parametrize("점수, 유효한가", [
    (-1, False),    # 경계 바로 아래
    (0, True),      # ★ 아래쪽 경계
    (1, True),
    (99, True),
    (100, True),    # ★ 위쪽 경계
    (101, False),   # 경계 바로 위
])
def test_점수_경계값(tmp_path, 점수, 유효한가):
    kept, skipped = load_scores(쓰기(tmp_path, 점수))
    assert (len(kept) == 1) == 유효한가


# ── 커버리지 측정 뒤 추가 (term-missing: 55-56, 77-86) ──────────

def test_이름이_비면_건너뛰고_기록한다():
    # 55-56행: 이름 칸이 빈 줄(",90")이 있어야 지나간다
    kept, skipped = load_scores("weird.csv")
    assert (2, ",90", "이름이 비어 있음") in skipped
    assert all(이름 != "" for 이름, _ in kept)


def test_명령줄로_실행하면_결과를_출력한다(monkeypatch, capsys):
    # 77-86행: python load_scores.py scores.csv 처럼 직접 실행해야 지나간다
    import runpy
    monkeypatch.setattr("sys.argv", ["load_scores.py", "scores.csv"])
    runpy.run_path("load_scores.py", run_name="__main__")
    출력 = capsys.readouterr().out
    assert "읽은 줄 : 5개" in 출력
    assert "건너뛴 줄 : 5개" in 출력
