import pytest
from find_max import find_max


# =========================================================
# 1. 정상 케이스 (Normal)
# =========================================================
class TestNormal:
    def test_max_in_middle(self):
        assert find_max([3, 9, 4]) == 9

    def test_max_at_first(self):
        assert find_max([10, 2, 5, 7]) == 10

    def test_max_at_last(self):
        # 원본 코드에서 실패: 마지막 원소를 검사하지 않음
        assert find_max([1, 2, 3, 99]) == 99

    def test_unsorted_list(self):
        assert find_max([55, 72, 18, 90, 64]) == 90

    def test_float_values(self):
        assert find_max([88.5, 92.3, 79.1]) == pytest.approx(92.3)

    def test_mixed_int_and_float(self):
        assert find_max([80, 85.5, 85]) == 85.5

    def test_all_negative(self):
        assert find_max([-10, -3, -7]) == -3

    def test_negative_and_positive(self):
        assert find_max([-5, 0, 5, -1]) == 5

    def test_tuple_input(self):
        # 인덱싱과 len()이 가능한 시퀀스이므로 동작해야 함
        assert find_max((4, 8, 2)) == 8

    def test_input_not_modified(self):
        scores = [3, 1, 2]
        find_max(scores)
        assert scores == [3, 1, 2]

    @pytest.mark.parametrize(
        "scores, expected",
        [
            ([1, 2, 3, 4, 5], 5),    # 오름차순, 원본 코드에서 실패
            ([5, 4, 3, 2, 1], 5),    # 내림차순
            ([2, 8, 3, 8, 1], 8),    # 최댓값 중복
            ([0, 0, 1], 1),          # 원본 코드에서 실패
        ],
    )
    def test_various_lists(self, scores, expected):
        assert find_max(scores) == expected

    @pytest.mark.parametrize("scores", [
        [1, 5, 3, 8, 2],
        [100, -100, 50, 0],
        [7, 7, 7, 8],
        list(range(1000)),
    ])
    def test_matches_builtin_max(self, scores):
        # 내장 함수 max()와 결과 비교
        assert find_max(scores) == max(scores)


# =========================================================
# 2. 경계값 케이스 (Boundary)
# =========================================================
class TestBoundary:
    def test_single_element(self):
        assert find_max([42]) == 42

    def test_two_elements_max_first(self):
        assert find_max([9, 1]) == 9

    def test_two_elements_max_last(self):
        # 원본 코드에서 실패: range(1, 1)이 빈 범위라 반복문이 돌지 않음
        assert find_max([1, 9]) == 9

    def test_three_elements_max_last(self):
        assert find_max([1, 2, 3]) == 3

    def test_all_same_values(self):
        assert find_max([5, 5, 5, 5]) == 5

    def test_zero_values(self):
        assert find_max([0, 0, 0]) == 0

    def test_score_range_bounds(self):
        # 점수 범위가 0~100이라고 가정했을 때의 양 끝값
        assert find_max([0, 100]) == 100
        assert find_max([100, 0]) == 100

    def test_very_large_and_small_numbers(self):
        assert find_max([-10**18, 10**18]) == 10**18

    def test_float_infinity(self):
        assert find_max([1.0, float("inf"), 2.0]) == float("inf")
        assert find_max([float("-inf"), -1e308]) == -1e308

    def test_large_list_max_at_end(self):
        data = list(range(100_000))
        assert find_max(data) == 99_999


# =========================================================
# 3. 예외 케이스 (Exception)
# =========================================================
class TestException:
    def test_empty_list_raises(self):
        with pytest.raises(IndexError):
            find_max([])

    def test_empty_tuple_raises(self):
        with pytest.raises(IndexError):
            find_max(())

    def test_none_raises(self):
        with pytest.raises(TypeError):
            find_max(None)

    def test_integer_input_raises(self):
        with pytest.raises(TypeError):
            find_max(123)

    def test_mixed_incomparable_types_raises(self):
        with pytest.raises(TypeError):
            find_max([1, "a", 3])

    def test_none_inside_list_raises(self):
        with pytest.raises(TypeError):
            find_max([1, None, 3])

    def test_set_input_raises(self):
        # set은 인덱싱을 지원하지 않음
        with pytest.raises(TypeError):
            find_max({1, 2, 3})
