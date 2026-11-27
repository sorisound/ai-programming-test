import pandas as pd

from analysis import 정제, 반별평균

# 파일을 맨 위에서 한 번만 읽는다
원본_df = pd.read_csv("scores_2026.csv", encoding="utf-8", dtype={"학번": str})
mini_df = pd.read_csv("mini.csv", encoding="utf-8", dtype={"학번": str})

# 읽은 데이터를 한 번만 정제해 두고 모든 테스트에서 함께 쓴다
깨끗한_df = 정제(원본_df)
깨끗한_mini = 정제(mini_df)


# ① 정제하면 100행이 남는지 확인한다
def test_정제_후_행_수():
    assert len(깨끗한_df) == 100


# ② 정제 후 반 값이 '1반'과 '2반' 두 가지뿐인지 확인한다
def test_반_값_종류():
    assert set(깨끗한_df["반"].unique()) == {"1반", "2반"}


# ③ 반별 점수 합계를 모두 더한 값이 전체 점수 합계와 같은지 확인한다
def test_반별_합계의_합():
    반별_합계 = 깨끗한_df.groupby("반")["점수"].sum()
    assert 반별_합계.sum() == 깨끗한_df["점수"].sum()


# ④ mini.csv를 정제한 뒤 1반 평균이 80.0인지 확인한다
def test_mini_1반_평균():
    평균 = 반별평균(깨끗한_mini)
    assert 평균["1반"] == 80.0
