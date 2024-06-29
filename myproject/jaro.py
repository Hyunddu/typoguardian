import json
import jarowinkler


def calculate_jaro_winkler_similarity(results):
    jaro_results = {}
    for package, similar_packages in results.items():
        jaro_scores = []
        for similar_package, dld_score in similar_packages:
            score = jarowinkler.jarowinkler_similarity(package, similar_package)
            jaro_scores.append((similar_package, score))
        jaro_scores.sort(key=lambda x: x[1], reverse=True)
        jaro_results[package] = jaro_scores
    return jaro_results


def run_jaro():
    try:
        with open("typos_DLD.json", "r") as file:
            results = json.load(file)
    except FileNotFoundError:
        print("typos_DLD.json not found.")
        return

    jaro_results = calculate_jaro_winkler_similarity(results)

    with open("typos_jaro.json", "w") as file:
        json.dump(jaro_results, file, indent=4)

