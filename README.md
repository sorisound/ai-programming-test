# 성적 CSV 읽기 프로그램 (load_scores)

## ① 무엇을 하나요 (What)

성적 CSV(`name,score`)를 읽어 0~100 사이의 정수 점수만 골라 내고, 건너뛴 줄은 줄 번호와 이유를 함께 알려 줍니다.

## ② 왜 만들었나요 (Why)

실제 성적 파일에는 빈 점수 칸, 105점이나 -5점 같은 범위 밖 점수, "결석" 같은 글자, 쉼표가 든 이름, 같은 이름이 두 번 나오는 줄이 섞여 있습니다.
10주차에 AI에게 역할만 주고 받은 코드 네 개는 모두 이런 줄 하나에서 예외가 나 파일 전체를 읽지 못했고, 일부는 105점을 오류 없이 그대로 받아들였습니다.
그래서 잘못된 줄은 버리지도 0점으로 바꾸지도 않고 따로 기록해 두고, 나머지 정상인 줄은 끝까지 읽는 함수가 필요했습니다.

## ③ 어떻게 쓰나요 (How)

Python 3.9 이상이면 프로그램 자체는 추가 설치 없이 돌아갑니다(표준 라이브러리 `csv`만 사용).

```bash
# 설치
git clone https://github.com/<내아이디>/ai-programming-test.git
cd ai-programming-test

# 실행 (파일 이름을 빼면 scores.csv를 읽습니다)
python3 load_scores.py scores.csv
```

실행하면 이렇게 나옵니다.

```
읽은 줄 : 5개
  김하나 88
  최,네번 77
  김하나 91
  윤보람 64
  서한별 95
건너뛴 줄 : 5개
  3행  이두리,105   ← 점수가 0~100 밖
  4행  박세찬,   ← 점수가 비어 있음
  7행  정오름,-5   ← 점수가 0~100 밖
  8행  한겨울,결석   ← 점수가 정수가 아님
  9행  장미르,72,비고없음   ← 열 개수가 2가 아님
```

다른 코드에서 함수로 쓸 때는 다음과 같습니다.

```python
from load_scores import load_scores

kept, skipped = load_scores("scores.csv")
# kept    : [(이름, 점수), ...]
# skipped : [(줄번호, 원본줄, 이유), ...]
```

## ④ 어떻게 테스트하나요

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install pytest pytest-cov

pytest test_load_scores.py -v
pytest test_load_scores.py --cov=load_scores --cov-report=term-missing
```

통과하면 이렇게 나옵니다(13개 통과, 커버리지 100%).

```
collecting ... collected 13 items

test_load_scores.py::test_정상_파일을_읽는다 PASSED                      [  7%]
test_load_scores.py::test_빈_줄은_건너뛴다 PASSED                        [ 15%]
test_load_scores.py::test_이름에_쉼표가_있어도_읽는다 PASSED             [ 23%]
test_load_scores.py::test_없는_파일이면_오류가_난다 PASSED               [ 30%]
test_load_scores.py::test_헤더만_있으면_빈_결과 PASSED                   [ 38%]
test_load_scores.py::test_점수_경계값[-1-False] PASSED                   [ 46%]
test_load_scores.py::test_점수_경계값[0-True] PASSED                     [ 53%]
test_load_scores.py::test_점수_경계값[1-True] PASSED                     [ 61%]
test_load_scores.py::test_점수_경계값[99-True] PASSED                    [ 69%]
test_load_scores.py::test_점수_경계값[100-True] PASSED                   [ 76%]
test_load_scores.py::test_점수_경계값[101-False] PASSED                  [ 84%]
test_load_scores.py::test_이름이_비면_건너뛰고_기록한다 PASSED           [ 92%]
test_load_scores.py::test_명령줄로_실행하면_결과를_출력한다 PASSED       [100%]

============================== 13 passed in 0.02s ==============================

Name             Stmts   Miss  Cover   Missing
----------------------------------------------
load_scores.py      45      0   100%
----------------------------------------------
TOTAL               45      0   100%
```

## ⑤ 파일 구성

| 파일 | 하는 일 |
| --- | --- |
| `load_scores.py` | 성적 CSV를 읽어 (유효한 목록, 건너뛴 줄 기록)을 돌려주는 함수. 직접 실행하면 결과를 출력 |
| `test_load_scores.py` | 정상 3 · 예외 2 · 경계값(-1, 0, 1, 99, 100, 101) · 커버리지 보강 2개 테스트 |
| `scores.csv` | 예시 성적 파일(정상 5줄 + 문제 있는 줄 5줄 + 빈 줄) |
| `empty.csv` | 헤더만 있는 파일(예외 테스트용) |
| `weird.csv` | 빈 이름 · 소수 점수 · 공백 등 이상한 줄 모음(테스트용) |
| `.gitignore` | 가상환경 · pytest · 커버리지 결과 파일 제외 |
| `LICENSE` | MIT License |

## ⑥ 만든 사람 · AI를 어디에 썼는지

- 만든 사람 : 천다민 (학번 2026100234)
- AI를 쓴 곳 : Claude Opus 5.5(Anthropic)로 테스트 코드와 이 README의 초안을 만들었습니다. 비교 실험용으로 같은 모델에게 코드만 준 테스트(A)와 명세만 준 테스트(B)도 받아 돌려 봤습니다(저장소에는 넣지 않음).
- 내가 직접 판단한 것 : 테스트 케이스 여덟 개는 명세서 6칸(코드 위 주석)을 기준으로 정했습니다. 경계값은 0 · 100을 통과, -1 · 101을 실패로 정했습니다. 커버리지에서 빠진 두 곳(빈 이름, 명령줄 실행)에 테스트를 더했습니다. 같은 이름은 동명이인일 수 있으니 지우지 않고 둘 다 남기는 것을 맞는 동작으로 봤습니다.
- 알려진 문제 : 이름에 쉼표가 있는 줄을 건너뛸 때 기록되는 원본 줄에서 큰따옴표가 빠집니다(`"최,네번",abc` → `최,네번,abc`). 명세만 준 AI 테스트(B)가 찾아냈고, 다음 커밋에서 고칠 예정입니다.

## 라이선스

MIT License (LICENSE 파일 참고)
