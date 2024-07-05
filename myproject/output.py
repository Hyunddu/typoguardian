import json
import re


def exact_package_match(typo_name, string):
    pattern = rf"^{re.escape(typo_name)}(?:-\d|\.|$)"
    return re.search(pattern, string) is not None


def calculate_score(package_name, typo_name, typo_score):
    score = typo_score
    score_breakdown = [f"typos: {typo_score:.2f}"]

    dog_detected = any(exact_package_match(typo_name, item['location'].split('/')[0])
                       for package in dog_result.get('packages', [])
                       for item in package.get('issues', []))
    yara_detected = any(exact_package_match(typo_name, item['file_path'].split('/')[0])
                        for item in yara_scan_result['malicious'])
    compare_detected = any(typo_name == version_info.get('malicious_package', '')
                           for package_info in comparison_result.values()
                           for version_list in package_info.get('versions', {}).values()
                           for version_info in version_list)
    sbom_detected = any(exact_package_match(typo_name, item['파일명'])
                        and '악성 이유' in item
                        for item in sbom_result['성공한 파일들'])

    if dog_detected:
        score += 3
        score_breakdown.append("dog: +3")
    if yara_detected:
        score += 1
        score_breakdown.append("yara: +1")
    if compare_detected:
        score += 1.5
        score_breakdown.append("compare: +1.5")
    if sbom_detected:
        score += 2
        score_breakdown.append("sbom: +2")
    if yara_detected and dog_detected:
        score += 1
        score_breakdown.append("yara+dog bonus: +1")

    final_score = min(score, 10)
    if final_score < score:
        score_breakdown.append(f"(capped at 10)")

    return final_score, " + ".join(score_breakdown)


def get_danger_level(score):
    if score >= 8.0:
        return "ALERT"
    elif score >= 6.0:
        return "CRIT"
    elif score >= 5.0:
        return "WARNING"
    elif score >= 4.0:
        return "NOTICE"
    else:
        return "INFO"


def get_result_description(typo_name):
    result = []

    # DOG 결과 추가
    for package in dog_result['packages']:
        if package['package'].startswith(typo_name):
            for issue in package['issues']:
                result.append(f"위치: {issue['location']}, 코드: {issue['code']}, 메시지: {issue['message']}")

    return ". ".join(result) if result else "추가 정보 없음"


def run_output():
    
    with open('final_typos.json', 'r') as f:
        final_typos = json.load(f)
    
    with open('dog_result.json', 'r') as f:
        dog_result = json.load(f)
    
    with open('yara_scan_results.json', 'r') as f:
        yara_scan_result = json.load(f)
    
    with open('comparison_results.json', 'r') as f:
        comparison_result = json.load(f)
    
    with open('sbom_results.json', 'r', encoding='utf-8') as file:
        sbom_result = json.load(file)
    typo_result = []
    for package_name, typos in final_typos.items():
        for typo in typos:
            typo_name, typo_score = typo
            if typo_score >= 3.0:
                score, score_breakdown = calculate_score(package_name, typo_name, typo_score)
                danger = get_danger_level(score)
                result = get_result_description(typo_name)
                typo_result.append({
                    "name": typo_name,
                    "score": score,
                    "score_breakdown": score_breakdown,
                    "danger": danger,
                    "result": f"{package_name}의 타이포스쿼팅의심됩니다. 위험도: {score:.2f}점 ({score_breakdown}). {result}"
                })
    typo_result.sort(key=lambda x: x['score'], reverse=True)

    final_result = {
        "typoResult": typo_result,
        "recommand": f"pip install {typo_result[0]['name'].split('-')[0]}" if typo_result else ""
    }

    # print(json.dumps(final_result, ensure_ascii=False))
    with open('results.json', 'w', encoding='utf-8') as json_file:
        json.dump(final_result, json_file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    run_output()
