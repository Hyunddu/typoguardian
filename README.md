# MyProject
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)


MyProject는 레벤슈타인 거리, 이미지 분석 점수 및 키보드 레이아웃 점수, jarowinkler 알고리즘을 활용하여 타이포스쿼팅 의심패키지를 확인하는 Python 모듈입니다.

## 목차
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)

## 설치 방법
```bash
python -m pip install -r .\requirements.txt
```
## 사용 방법

### PyPI 패키지 리스트 업데이트
```bash
myproject --update
```
이 명령어는 PyPI에 등록된 최신 패키지 리스트를 다운로드합니다.

### 타이포스쿼팅 의심 패키지 불러오기
```bash
myproject {패키지 이름}
```
pypi에 등록된 패키지 중 입력한 패키지와 유사한 패키지 이름을 json파일로 저장합니다. 함께 설치되는 패키지도 포함됩니다.

### 정상 기능 제공 확인
```bash
myproject --compare
```
설치된 패키지와 타이포스쿼팅 의심패키지 파일을 비교하여 기존 기능을 제공하는지 확인합니다.

## json 파일
- pypi 패키지 리스트 (output => pypi_packages.json)
- damerau_levenshtein_distance (output => typos_DLD.json)
- Jaro–Winkler_distance (output => typos_jaro.json)
- 이미지 분석 점수 계산 (output => typos_imgage_numpy.json) 
- 키보드 레이아웃 점수 계산 (output => typos_clavier.json)
- 타이포스쿼팅 의심 패키지 (output => final_typos.json)
- 정상패키지 기능제공 확인 (output => comparison_results.json)
