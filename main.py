import time
import json

# 십자가 패턴
cross = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]

# X 패턴
x_pattern = [
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 1]
]


# MAC 연산 함수
def mac(pattern, filter_data):
    score = 0

    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            score += pattern[i][j] * filter_data[i][j]

    return score


# MAC 연산 시간 측정 함수
def measure_mac(pattern, filter_data, repeat=10):
    total_time = 0

    for i in range(repeat):
        start = time.perf_counter()

        mac(pattern, filter_data)

        end = time.perf_counter()

        total_time += end - start

    # 초(s)를 밀리초(ms)로 변환
    average_ms = (total_time / repeat) * 1000

    return average_ms


# JSON 파일 로드 및 기본 구조 검증
def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        # 최상위 자료형 확인
        if not isinstance(data, dict):
            print("오류: JSON 최상위 데이터는 객체여야 합니다.")
            return None

        # 필수 키 확인
        if "filters" not in data or "patterns" not in data:
            print("오류: filters 또는 patterns 키가 없습니다.")
            return None

        # 필수 데이터 자료형 확인
        if not isinstance(data["filters"], dict):
            print("오류: filters는 객체여야 합니다.")
            return None

        if not isinstance(data["patterns"], dict):
            print("오류: patterns는 객체여야 합니다.")
            return None

        print("JSON 파일 로드 성공!")
        return data

    except FileNotFoundError:
        print("오류: JSON 파일을 찾을 수 없습니다.")
        return None

    except json.JSONDecodeError:
        print("오류: JSON 파일 형식이 올바르지 않습니다.")
        return None

    except OSError as error:
        print(f"오류: 파일을 읽을 수 없습니다. ({error})")
        return None


# 라벨 정규화 함수
def normalize_label(label):
    label = str(label).strip().lower()

    if label in ["+", "cross"]:
        return "Cross"

    elif label == "x":
        return "X"

    else:
        return "UNKNOWN"


# 배열 크기 및 데이터 검증
def validate_matrix(matrix, size):
    # 배열이 리스트인지 확인
    if not isinstance(matrix, list):
        return False

    # 행 개수 확인
    if len(matrix) != size:
        return False

    for row in matrix:
        # 각 행이 리스트인지 확인
        if not isinstance(row, list):
            return False

        # 열 개수 확인
        if len(row) != size:
            return False

        # 숫자 데이터 확인
        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return False

    return True


# MAC 점수 기반 자동 판정 함수
def classify_pattern(pattern, cross_filter, x_filter):
    score_cross = mac(pattern, cross_filter)
    score_x = mac(pattern, x_filter)

    epsilon = 1e-9

    if abs(score_cross - score_x) < epsilon:
        prediction = "UNDECIDED"

    elif score_cross > score_x:
        prediction = "Cross"

    else:
        prediction = "X"

    return score_cross, score_x, prediction


# 연산 테스트
print("십자가 필터 점수:", mac(cross, cross))
print("X 필터 점수:", mac(cross, x_pattern))



# 3×3 배열 입력 함수
def input_matrix(name):
    matrix = []

    print(f"\n=== {name} 입력 ===")

    for i in range(3):
        while True:
            numbers = input(f"{i + 1}번째 줄 (숫자 3개): ")

            try:
                row = list(map(float, numbers.split()))

                if len(row) != 3:
                    print("입력 형식 오류: 숫자 3개를 입력하세요.")
                    continue

                matrix.append(row)
                break

            except ValueError:
                print("입력 형식 오류: 숫자만 입력하세요.")

    return matrix


# 프로그램 실행
print("\n=== Mini NPU Simulator ===")

print("1. 사용자 입력 (3×3)")
print("2. data.json 분석")

mode = input("모드 선택: ")

if mode == "1":
    filter_a = input_matrix("필터 A")
    filter_b = input_matrix("필터 B")
    pattern = input_matrix("패턴")

    print("\n=== 입력 결과 확인 ===")
    print("필터 A:", filter_a)
    print("필터 B:", filter_b)
    print("패턴:", pattern)


    # MAC 점수 계산
    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)

    # 허용오차 설정
    epsilon = 1e-9

    # 점수 비교 및 판정
    if abs(score_a - score_b) < epsilon:
        result = "UNDECIDED"
    elif score_a > score_b:
        result = "A"
    else:
        result = "B"

    # 결과 출력
    print("\n=== MAC 연산 결과 ===")
    print("필터 A 점수:", score_a)
    print("필터 B 점수:", score_b)
    print("판정 결과:", result)


    # 성능 분석
    average_time = measure_mac(pattern, filter_a)

    print("\n=== 성능 분석 ===")
    print("패턴 크기: 3×3")
    print("연산 횟수:", 3 * 3)
    print("반복 측정: 10회")
    print(f"평균 연산 시간: {average_time:.6f} ms")




elif mode == "2":
    print("\n=== JSON 자동 분석 모드 ===")

    data = load_json("data.json")

    if data is not None:
        filters = data["filters"]
        patterns = data["patterns"]

        pass_count = 0
        fail_count = 0
        results = []

        for key, case in patterns.items():

            
            # 패턴 데이터 확인
            pattern = case.get("input")

            if not isinstance(pattern, list):
                print(f"\n[{key}]")
                print("오류: 패턴 데이터가 리스트가 아닙니다.")
                fail_count += 1
                continue

            size = len(pattern)
            size_key = f"size_{size}"

            # 필터 존재 여부 확인
            if size_key not in filters:
                print(f"\n[{key}]")
                print("오류: 해당 크기의 필터가 없습니다.")
                fail_count += 1
                continue

            filter_group = filters[size_key]

            if not isinstance(filter_group, dict) or \
               "cross" not in filter_group or "x" not in filter_group:
                print(f"\n[{key}]")
                print("오류: Cross 또는 X 필터가 없습니다.")
                fail_count += 1
                continue

            # 패턴과 필터 배열 검증           
            if not (
                validate_matrix(pattern, size)
                and validate_matrix(filter_group["cross"], size)
                and validate_matrix(filter_group["x"], size)
            ):
                print(f"\n[{key}]")
                print("오류: 배열 크기 또는 데이터 형식이 올바르지 않습니다.")

                results.append({
                    "name": key,
                    "size": size,
                    "cross": 0.0,
                    "x": 0.0,
                    "expected": str(case.get("expected", "UNKNOWN")),
                    "prediction": "ERROR",
                    "status": "FAIL"
                })

                fail_count += 1
                continue

                print(f"\n[{key}]")
                print("오류: 배열 크기 또는 데이터 형식이 올바르지 않습니다.")
                fail_count += 1
                continue


            # 크기에 맞는 필터 선택
            cross_filter = filters[size_key]["cross"]
            x_filter = filters[size_key]["x"]

            # MAC 점수 및 판정
            score_cross, score_x, prediction = classify_pattern(
                pattern, cross_filter, x_filter
            )

            # 예상 정답 정규화
            expected = normalize_label(case["expected"])

            # PASS / FAIL 확인
            if prediction == expected:
                status = "PASS"
                pass_count += 1
            else:
                status = "FAIL"
                fail_count += 1


            # 분석 결과 저장
            results.append({
                "name": key,
                "size": size,
                "cross": score_cross,
                "x": score_x,
                "expected": expected,
                "prediction": prediction,
                "status": status
            })

            
            # 결과 출력
            print(f"\n[{key}]")
            print(f"크기: {size}×{size}")
            print(f"Cross 점수: {score_cross:.6f}")
            print(f"X 점수: {score_x:.6f}")
            print(f"예상 정답: {expected}")
            print(f"판정 결과: {prediction}")
            print(f"검증 결과: {status}")

        print("\n=== 전체 분석 결과 ===")
        print("총 패턴:", len(patterns))
        print("PASS:", pass_count)
        print("FAIL:", fail_count)


        # 전체 패턴 결과 요약표
        print("\n=== 전체 패턴 결과 요약표 ===")

        print(
            f"{'패턴':<15}"
            f"{'크기':<10}"
            f"{'Cross':<12}"
            f"{'X':<12}"
            f"{'예상':<12}"
            f"{'판정':<12}"
            f"{'결과':<8}"
        )

        print("-" * 85)

        for result in results:
            print(
                f"{result['name']:<15}"
                f"{str(result['size']) + 'x' + str(result['size']):<10}"
                f"{result['cross']:<12.4f}"
                f"{result['x']:<12.4f}"
                f"{result['expected']:<12}"
                f"{result['prediction']:<12}"
                f"{result['status']:<8}"
            )


        # 크기별 MAC 연산 성능 측정
        print("\n=== 크기별 MAC 연산 성능 측정 ===")

        for size in [3, 5, 13, 25]:
            # 측정용 정사각형 배열 생성
            test_pattern = [[1] * size for _ in range(size)]
            test_filter = [[1] * size for _ in range(size)]

            # 10회 반복 측정
            average_ms = measure_mac(test_pattern, test_filter, repeat=10)

            print(f"{size}x{size}: {average_ms:.6f} ms")


else:
    print("올바른 모드를 선택하세요.")


