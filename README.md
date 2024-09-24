# 🛡️ Typoguardian

![GitHub stars](https://img.shields.io/github/stars/Hyunddu/typoguardian?style=social)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)

> Typoguardian은 다양한 알고리즘을 활용하여 타이포스쿼팅 의심 패키지를 식별하는 강력한 Python 모듈입니다.

## 📋 목차
- [🚀 주요 기능](#주요-기능)
- [⚙️ 설치 방법](#설치-방법)
- [🔧 사용 방법](#사용-방법)
- [📁 JSON 파일 설명](#json-파일)

## 🚀 주요 기능

- 레벤슈타인 거리 계산
- 이미지 분석 점수 산출
- 키보드 레이아웃 점수 계산
- Jaro-Winkler 알고리즘 적용
- 다양한 오픈소스 도구를 활용한 악성 패키지 탐지

## ⚙️ 설치 방법

```bash
pip install .
```

## 🔧 사용 방법

### PyPI 패키지 리스트 업데이트

```bash
typoguardian --update
```

이 명령어는 PyPI에 등록된 최신 패키지 리스트를 다운로드합니다.

### 악성 패키지 검사

```bash
typoguardian
```

이 명령어는 다음 작업을 수행합니다:
- PyPI에 등록된 패키지 중 입력한 패키지와 유사한 이름을 가진 패키지를 식별
- 결과를 `final_typos.json` 파일로 저장 (함께 설치되는 패키지 포함)
- yara, guarddog, syft, bomber 오픈소스를 이용하여 악성 패키지 탐지

### 이전 파일 삭제 옵션

```bash
typoguardian --clean
```

검사 진행 전 이전 파일을 삭제합니다 (`pypi_packages.json` 제외).

## 📁 JSON 파일

| 파일명 | 설명 |
|--------|------|
| `pypi_packages.json` | PyPI 패키지 리스트 |
| `typos_DLD.json` | Damerau-Levenshtein 거리 계산 결과 |
| `typos_jaro.json` | Jaro-Winkler 거리 계산 결과 |
| `typos_imgage_numpy.json` | 이미지 분석 점수 계산 결과 |
| `typos_clavier.json` | 키보드 레이아웃 점수 계산 결과 |
| `final_typos.json` | 타이포스쿼팅 의심 패키지 목록 |
| `comparison_results.json` | 정상 패키지 기능 제공 확인 결과 |
| `yara_scan_results.json` | YARA 악성코드 탐지 결과 |
| `sbom_results.json` | SBOM 취약점 탐지 결과 |
| `dog_result.json` | Guarddog 악성코드 탐지 결과 |
| `results.json` | 최종 악성 패키지 점수 계산 결과 |

## 🤝 기여하기

버그를 발견하셨거나 새로운 기능을 제안하고 싶으시다면 이슈를 열어주세요. 풀 리퀘스트도 환영합니다!

## 📞 문의하기

질문이나 피드백이 있으시면 [이슈](https://github.com/Hyunddu/typoguardian/issues)를 통해 연락해주세요.
