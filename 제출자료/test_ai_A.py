# test_load_scores.py
# ---------------------------------------------------------------------------
# load_scores(path) 단위 테스트
#   1. 정상 동작
#   2. 예외 / 건너뛰기 (명세 ①, ③~⑥)
#   3. 경계값 (명세 ②, 점수 0·100, 빈 파일 등)
#   4. 명세에 없는 현재 동작 고정 (characterization)
# ---------------------------------------------------------------------------

import pytest

from load_scores import load_scores, MIN_SCORE, MAX_SCORE

HEADER = "이름,점수\n"

# 이유 문자열은 한곳에 모아 둡니다 (오타 하나로 테스트가 깨지지 않도록)
열개수 = "열 개수가 2가 아님"
이름없음 = "이름이 비어 있음"
점수없음 = "점수가 비어 있음"
정수아님 = "점수가 정수가 아님"
범위밖 = "점수가 0~100 밖"


@pytest.fixture
def make_csv(tmp_path):
    """본문 문자열로 임시 CSV 파일을 만들어 경로를 돌려준다.

    write_text 대신 바이트로 써서 OS별 줄바꿈 변환이 끼어들지 않게 한다.
    """
    def _make(body="", header=HEADER, encoding="utf-8"):
        p = tmp_path / "scores.csv"
        p.write_bytes((header + body).encode(encoding))
        return p
    return _make


# ===========================================================================
# 1. 정상 동작
# ===========================================================================

def test_정상_여러_줄을_순서대로_읽는다(make_csv):
    path = make_csv("김철수,85\n이영희,92\n박민수,70\n")

    kept, skipped = load_scores(path)

    assert kept == [("김철수", 85), ("이영희", 92), ("박민수", 70)]
    assert skipped == []


def test_반환값은_리스트_두_개의_튜플이다(make_csv):
    result = load_scores(make_csv("김철수,85\n"))

    assert isinstance(result, tuple) and len(result) == 2
    kept, skipped = result
    assert isinstance(kept, list) and isinstance(skipped, list)
    assert isinstance(kept[0][1], int)          # 점수는 문자열이 아니라 int


def test_이름과_점수의_앞뒤_공백을_제거한다(make_csv):
    kept, skipped = load_scores(make_csv("  김철수  ,  85  \n"))

    assert kept == [("김철수", 85)]
    assert skipped == []


def test_동명이인은_둘_다_남긴다(make_csv):
    """v5 재검토 결정: 같은 이름이어도 지우지 않는다."""
    kept, skipped = load_scores(make_csv("김철수,85\n이영희,90\n김철수,70\n"))

    assert kept == [("김철수", 85), ("이영희", 90), ("김철수", 70)]
    assert skipped == []


def test_BOM이_있는_파일도_읽는다(make_csv):
    """엑셀에서 저장한 UTF-8 CSV는 맨 앞에 BOM이 붙는다."""
    path = make_csv("김철수,85\n", encoding="utf-8-sig")

    kept, skipped = load_scores(path)

    assert kept == [("김철수", 85)]
    assert skipped == []


def test_윈도우_줄바꿈_CRLF도_읽는다(make_csv):
    path = make_csv("김철수,85\r\n이영희,92\r\n", header="이름,점수\r\n")

    kept, skipped = load_scores(path)

    assert kept == [("김철수", 85), ("이영희", 92)]
    assert skipped == []


def test_마지막_줄에_줄바꿈이_없어도_읽는다(make_csv):
    kept, _ = load_scores(make_csv("김철수,85\n이영희,92"))

    assert kept == [("김철수", 85), ("이영희", 92)]


def test_따옴표로_감싼_쉼표는_이름의_일부다(make_csv):
    kept, skipped = load_scores(make_csv('"김,철수",85\n'))

    assert kept == [("김,철수", 85)]
    assert skipped == []


# ===========================================================================
# 2. 예외 / 건너뛰기
# ===========================================================================

def test_명세1_파일이_없으면_FileNotFoundError(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "없는파일.csv")


@pytest.mark.parametrize(
    "line, reason",
    [
        # ③ 열 개수
        ("김철수",            열개수),
        ("김철수,85,A",       열개수),
        ("김철수,85,",        열개수),   # 끝에 쉼표 하나 → 열이 3개
        ("   ",               열개수),   # 공백만 있는 줄은 '빈 줄'이 아니다
        # ⑥ 이름
        (",85",               이름없음),
        ("   ,85",            이름없음),
        (",",                 이름없음),  # 이름·점수 둘 다 없으면 이름 검사가 먼저
        # ④ 점수 비어 있음
        ("김철수,",           점수없음),
        ("김철수,   ",        점수없음),
        # ④ 정수가 아님
        ("김철수,abc",        정수아님),
        ("김철수,85.5",       정수아님),
        ("김철수,85점",       정수아님),
        ("김철수,8 5",        정수아님),
        ("김철수,1e2",        정수아님),
        # ⑤ 범위 밖
        ("김철수,-1",         범위밖),
        ("김철수,101",        범위밖),
        ("김철수,-100",       범위밖),
        ("김철수,1000",       범위밖),
    ],
)
def test_잘못된_줄은_건너뛰고_기록한다(make_csv, line, reason):
    kept, skipped = load_scores(make_csv(line + "\n"))

    assert kept == []
    assert skipped == [(2, line, reason)]       # 헤더가 1행이므로 데이터는 2행


def test_좋은_줄과_나쁜_줄이_섞여_있어도_서로_영향이_없다(make_csv):
    body = (
        "김철수,85\n"      # 2행  O
        "이영희\n"         # 3행  X 열 개수
        "\n"               # 4행  빈 줄 (기록 없음)
        "박민수,101\n"     # 5행  X 범위
        "최지우,0\n"       # 6행  O
    )
    kept, skipped = load_scores(make_csv(body))

    assert kept == [("김철수", 85), ("최지우", 0)]
    assert skipped == [
        (3, "이영희", 열개수),
        (5, "박민수,101", 범위밖),
    ]


def test_빈_줄은_기록하지_않지만_줄번호는_센다(make_csv):
    kept, skipped = load_scores(make_csv("김철수,85\n\n\n이영희,abc\n"))

    assert kept == [("김철수", 85)]
    assert skipped == [(5, "이영희,abc", 정수아님)]


def test_skipped_원소는_줄번호_원본_이유의_3튜플이다(make_csv):
    _, skipped = load_scores(make_csv("김철수,abc\n"))

    line_no, 원본, 이유 = skipped[0]
    assert isinstance(line_no, int)
    assert isinstance(원본, str)
    assert isinstance(이유, str)


def test_원본에는_공백을_제거하지_않은_줄이_남는다(make_csv):
    _, skipped = load_scores(make_csv("  김철수  ,  abc  \n"))

    assert skipped == [(2, "  김철수  ,  abc  ", 정수아님)]


# ===========================================================================
# 3. 경계값
# ===========================================================================

@pytest.mark.parametrize(
    "raw, expected",
    [
        (str(MIN_SCORE),     MIN_SCORE),       # 0   (하한)
        (str(MIN_SCORE + 1), MIN_SCORE + 1),   # 1
        (str(MAX_SCORE - 1), MAX_SCORE - 1),   # 99
        (str(MAX_SCORE),     MAX_SCORE),       # 100 (상한)
    ],
)
def test_경계값_안쪽은_남긴다(make_csv, raw, expected):
    kept, skipped = load_scores(make_csv(f"김철수,{raw}\n"))

    assert kept == [("김철수", expected)]
    assert skipped == []


@pytest.mark.parametrize("score", [MIN_SCORE - 1, MAX_SCORE + 1])
def test_경계값_바로_바깥은_건너뛴다(make_csv, score):
    line = f"김철수,{score}"
    kept, skipped = load_scores(make_csv(line + "\n"))

    assert kept == []
    assert skipped == [(2, line, 범위밖)]


def test_명세2_헤더만_있으면_빈_결과(make_csv):
    assert load_scores(make_csv("")) == ([], [])


def test_헤더만_있고_줄바꿈도_없으면_빈_결과(make_csv):
    assert load_scores(make_csv("", header="이름,점수")) == ([], [])


def test_완전히_빈_파일이면_빈_결과(make_csv):
    assert load_scores(make_csv("", header="")) == ([], [])


def test_헤더와_빈_줄만_있으면_빈_결과(make_csv):
    assert load_scores(make_csv("\n\n\n")) == ([], [])


def test_데이터가_한_줄뿐이어도_읽는다(make_csv):
    assert load_scores(make_csv("김철수,85\n")) == ([("김철수", 85)], [])


def test_한_글자_이름도_이름이다(make_csv):
    kept, _ = load_scores(make_csv("김,85\n"))

    assert kept == [("김", 85)]


# ===========================================================================
# 4. 명세에 적혀 있지 않은 현재 동작 (characterization test)
#    - "지금 이렇게 동작한다"를 고정해 둔 테스트입니다.
#    - 원하는 동작이 아니라면 명세를 먼저 정하고, 테스트와 코드를 함께 고치세요.
# ===========================================================================

def test_현재동작_첫_줄은_내용과_상관없이_헤더로_버린다(make_csv):
    path = make_csv("이영희,92\n", header="김철수,85\n")

    kept, skipped = load_scores(path)

    assert kept == [("이영희", 92)]         # 김철수는 기록도 없이 사라진다
    assert skipped == []


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("+50",  50),    # 부호 붙은 수
        ("-0",   0),
        ("007",  7),     # 앞자리 0
        ("1_00", 100),   # 파이썬 숫자 구분자 _
        ("５０", 50),    # 전각 숫자
    ],
)
def test_현재동작_int가_받아들이는_표기는_모두_통과한다(make_csv, raw, expected):
    kept, skipped = load_scores(make_csv(f"김철수,{raw}\n"))

    assert kept == [("김철수", expected)]
    assert skipped == []


def test_현재동작_원본은_따옴표가_빠진_채_기록된다(make_csv):
    _, skipped = load_scores(make_csv('"김,철수",abc\n'))

    # 파일에는 "김,철수",abc 였지만 기록에는 따옴표가 없다
    assert skipped == [(2, "김,철수,abc", 정수아님)]
