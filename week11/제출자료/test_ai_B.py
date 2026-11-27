"""load_scores 함수의 단위 테스트 (pytest)

실행: pytest -v test_load_scores.py
"""
import pytest

from load_scores import load_scores

HEADER = "name,score\n"


# ---------------------------------------------------------------------------
# 도우미
# ---------------------------------------------------------------------------
@pytest.fixture
def make_csv(tmp_path):
    """본문 문자열로 CSV 파일을 만들고 경로(str)를 돌려준다."""
    def _make(body: str, header: str = HEADER, newline: str = "\n") -> str:
        path = tmp_path / "scores.csv"
        with open(path, "w", encoding="utf-8", newline=newline) as f:
            f.write(header + body)
        return str(path)
    return _make


def raw(line) -> str:
    """원본줄 비교 시 줄끝 문자 포함 여부 차이를 없앤다."""
    return line.rstrip("\r\n")


def assert_skipped(entry, lineno, original):
    """skipped 항목 하나가 (줄번호, 원본줄, 이유) 형식인지 확인한다."""
    assert len(entry) == 3
    got_lineno, got_line, reason = entry
    assert got_lineno == lineno
    assert raw(got_line) == original
    assert isinstance(reason, str) and reason.strip(), "이유는 비어 있지 않은 문자열이어야 함"


# ===========================================================================
# 1. 정상 동작
# ===========================================================================
class TestNormal:
    def test_returns_tuple_of_kept_and_skipped(self, make_csv):
        result = load_scores(make_csv("김철수,90\n"))
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_basic_rows(self, make_csv):
        kept, skipped = load_scores(make_csv("김철수,90\n이영희,85\n박민수,70\n"))
        assert kept == [("김철수", 90), ("이영희", 85), ("박민수", 70)]
        assert skipped == []

    def test_score_is_int(self, make_csv):
        kept, _ = load_scores(make_csv("김철수,90\n"))
        name, score = kept[0]
        assert type(name) is str
        assert type(score) is int

    def test_preserves_file_order(self, make_csv):
        kept, _ = load_scores(make_csv("다,30\n가,10\n나,20\n"))
        assert [n for n, _ in kept] == ["다", "가", "나"]

    def test_quoted_name_with_comma(self, make_csv):
        kept, skipped = load_scores(make_csv('"최,네번",80\n'))
        assert kept == [("최,네번", 80)]
        assert skipped == []

    def test_strips_whitespace_around_name_and_score(self, make_csv):
        kept, skipped = load_scores(make_csv("  김철수  ,  90  \n"))
        assert kept == [("김철수", 90)]
        assert skipped == []

    def test_duplicate_names_are_all_kept(self, make_csv):
        kept, skipped = load_scores(make_csv("김철수,90\n김철수,60\n"))
        assert kept == [("김철수", 90), ("김철수", 60)]
        assert skipped == []

    def test_identical_duplicate_rows_are_all_kept(self, make_csv):
        kept, _ = load_scores(make_csv("김철수,90\n김철수,90\n"))
        assert kept == [("김철수", 90), ("김철수", 90)]

    def test_no_trailing_newline_at_eof(self, make_csv):
        kept, skipped = load_scores(make_csv("김철수,90\n이영희,85"))
        assert kept == [("김철수", 90), ("이영희", 85)]
        assert skipped == []

    def test_crlf_line_endings(self, make_csv):
        path = make_csv("김철수,90\r\n이영희,85\r\n",
                        header="name,score\r\n", newline="")
        kept, skipped = load_scores(path)
        assert kept == [("김철수", 90), ("이영희", 85)]
        assert skipped == []


# ===========================================================================
# 2. 경계값
# ===========================================================================
class TestBoundary:
    @pytest.mark.parametrize("score", [0, 1, 50, 99, 100])
    def test_valid_score_range_inclusive(self, make_csv, score):
        kept, skipped = load_scores(make_csv(f"김철수,{score}\n"))
        assert kept == [("김철수", score)]
        assert skipped == []

    def test_zero_is_valid_not_treated_as_missing(self, make_csv):
        kept, skipped = load_scores(make_csv("김철수,0\n"))
        assert kept == [("김철수", 0)]
        assert skipped == []

    @pytest.mark.parametrize("score", ["-1", "101", "-100", "1000"])
    def test_out_of_range_is_skipped(self, make_csv, score):
        line = f"김철수,{score}"
        kept, skipped = load_scores(make_csv(line + "\n"))
        assert kept == []
        assert len(skipped) == 1
        assert_skipped(skipped[0], 2, line)

    def test_header_only_returns_empty(self, make_csv):
        assert load_scores(make_csv("")) == ([], [])

    def test_header_only_without_newline(self, make_csv):
        assert load_scores(make_csv("", header="name,score")) == ([], [])

    def test_header_line_is_number_one(self, make_csv):
        # 헤더=1, 첫 데이터=2, 두 번째 데이터=3
        _, skipped = load_scores(make_csv("김철수,90\n이영희,abc\n"))
        assert skipped[0][0] == 3

    def test_single_char_name(self, make_csv):
        kept, _ = load_scores(make_csv("김,50\n"))
        assert kept == [("김", 50)]


# ===========================================================================
# 3. 잘못된 줄 → 건너뛰고 기록
# ===========================================================================
class TestInvalidRows:
    @pytest.mark.parametrize(
        "line",
        [
            "김철수",            # 열 1개
            "김철수,90,추가",     # 열 3개
            "김철수,90,",         # 열 3개(마지막 빈 열)
            "최,네번,80",         # 따옴표 없는 쉼표 → 열 3개
        ],
        ids=["1열", "3열", "3열-빈열", "따옴표없는쉼표"],
    )
    def test_wrong_column_count(self, make_csv, line):
        kept, skipped = load_scores(make_csv(line + "\n"))
        assert kept == []
        assert len(skipped) == 1
        assert_skipped(skipped[0], 2, line)

    @pytest.mark.parametrize("line", [",90", "   ,90", '"",90'],
                             ids=["빈이름", "공백이름", "따옴표빈이름"])
    def test_empty_name(self, make_csv, line):
        kept, skipped = load_scores(make_csv(line + "\n"))
        assert kept == []
        assert len(skipped) == 1
        assert_skipped(skipped[0], 2, line)

    @pytest.mark.parametrize("line", ["김철수,", "김철수,   "],
                             ids=["빈점수", "공백점수"])
    def test_empty_score(self, make_csv, line):
        kept, skipped = load_scores(make_csv(line + "\n"))
        assert kept == []
        assert len(skipped) == 1
        assert_skipped(skipped[0], 2, line)

    @pytest.mark.parametrize(
        "score",
        ["abc", "90.5", "90.0", "9 0", "구십", "1e2", "NaN"],
    )
    def test_non_integer_score(self, make_csv, score):
        line = f"김철수,{score}"
        kept, skipped = load_scores(make_csv(line + "\n"))
        assert kept == []
        assert len(skipped) == 1
        assert_skipped(skipped[0], 2, line)

    def test_invalid_row_not_converted_to_zero(self, make_csv):
        kept, _ = load_scores(make_csv("김철수,abc\n이영희,\n"))
        assert ("김철수", 0) not in kept
        assert ("이영희", 0) not in kept
        assert kept == []

    def test_invalid_rows_are_not_silently_dropped(self, make_csv):
        """잘못된 줄 수 == skipped 길이 (조용히 사라지는 줄이 없어야 함)"""
        body = "김철수\n,90\n이영희,\n박민수,abc\n최지우,101\n"
        kept, skipped = load_scores(make_csv(body))
        assert kept == []
        assert [s[0] for s in skipped] == [2, 3, 4, 5, 6]

    def test_one_bad_row_does_not_stop_processing(self, make_csv):
        body = "김철수,90\n이영희,abc\n박민수,70\n"
        kept, skipped = load_scores(make_csv(body))
        assert kept == [("김철수", 90), ("박민수", 70)]
        assert len(skipped) == 1
        assert_skipped(skipped[0], 3, "이영희,abc")

    def test_mixed_file(self, make_csv):
        body = (
            "김철수,90\n"        # 2 OK
            "이영희\n"           # 3 열 개수
            '"최,네번",80\n'     # 4 OK
            ",50\n"              # 5 이름 없음
            "박민수,\n"          # 6 점수 없음
            "정다은,12.5\n"      # 7 정수 아님
            "한지민,-1\n"        # 8 범위 밖
            "김철수,100\n"       # 9 OK (동명이인)
            "오세훈,0\n"         # 10 OK
        )
        kept, skipped = load_scores(make_csv(body))
        assert kept == [("김철수", 90), ("최,네번", 80),
                        ("김철수", 100), ("오세훈", 0)]
        assert [s[0] for s in skipped] == [3, 5, 6, 7, 8]
        assert [raw(s[1]) for s in skipped] == [
            "이영희", ",50", "박민수,", "정다은,12.5", "한지민,-1",
        ]

    def test_reason_differs_by_error_kind(self, make_csv):
        """서로 다른 종류의 오류는 서로 다른 이유를 가져야 한다."""
        body = "이영희\n,50\n박민수,abc\n한지민,101\n"
        _, skipped = load_scores(make_csv(body))
        reasons = [s[2] for s in skipped]
        assert len(set(reasons)) == 4


# ===========================================================================
# 4. 빈 줄 → 기록 없이 건너뜀
# ===========================================================================
class TestBlankLines:
    def test_blank_line_skipped_without_record(self, make_csv):
        kept, skipped = load_scores(make_csv("김철수,90\n\n이영희,85\n"))
        assert kept == [("김철수", 90), ("이영희", 85)]
        assert skipped == []

    def test_multiple_and_trailing_blank_lines(self, make_csv):
        kept, skipped = load_scores(make_csv("\n\n김철수,90\n\n\n"))
        assert kept == [("김철수", 90)]
        assert skipped == []

    def test_only_blank_lines_after_header(self, make_csv):
        assert load_scores(make_csv("\n\n\n")) == ([], [])

    def test_blank_lines_still_count_toward_line_number(self, make_csv):
        # 1:헤더  2:빈줄  3:김철수,90  4:빈줄  5:이영희,abc
        _, skipped = load_scores(make_csv("\n김철수,90\n\n이영희,abc\n"))
        assert len(skipped) == 1
        assert_skipped(skipped[0], 5, "이영희,abc")


# ===========================================================================
# 5. 파일 예외
# ===========================================================================
class TestFileErrors:
    def test_missing_file_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_scores(str(tmp_path / "없는파일.csv"))

    def test_missing_file_error_not_swallowed(self, tmp_path):
        """빈 결과 ([], [])로 숨기지 않고 반드시 예외를 올려야 한다."""
        missing = tmp_path / "nope.csv"
        with pytest.raises(FileNotFoundError):
            result = load_scores(str(missing))
            pytest.fail(f"예외 대신 값을 반환함: {result!r}")
