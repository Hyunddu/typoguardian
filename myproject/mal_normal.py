import os
import json
import requests

# Constants
SIMILAR_JSON_FILE = "final_typos.json"
PYPI_URL_TEMPLATE = "https://pypi.org/pypi/{package}/json"
SAVE_DIR = "similar_packages"


def load_similar_packages(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        return json.load(file)


def fetch_json(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def download_file(url, save_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


def download_package(package_name):
    package_info_url = PYPI_URL_TEMPLATE.format(package=package_name)
    package_info = fetch_json(package_info_url)
    latest_version = package_info["info"]["version"]
    tarball_url = next((url['url'] for url in package_info["urls"] if url['packagetype'] == 'sdist'), None)
    save_path = os.path.join(SAVE_DIR, package_name, 'normal', latest_version,
                             f'{package_name}-{latest_version}.tar.gz')
    download_file(tarball_url, save_path)


def download_malicious_package(mal_pkg_name, norm_pkg_name):
    package_info_url = PYPI_URL_TEMPLATE.format(package=mal_pkg_name)
    try:
        package_info = fetch_json(package_info_url)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            # print(f"{mal_pkg_name} : pypi 미등록")
            return
        else:
            raise
    latest_version = package_info["info"]["version"]
    tarball_url = next((url['url'] for url in package_info["urls"] if url['packagetype'] == 'sdist'), None)
    if tarball_url is None:
        # print(f"{mal_pkg_name} : tar.gz 미등록")
        return
    save_path = os.path.join(SAVE_DIR, norm_pkg_name, 'malregistry', mal_pkg_name, latest_version,
                             f'{mal_pkg_name}-{latest_version}.tar.gz')
    download_file(tarball_url, save_path)


def run_mal_normal():
    similar_packages = load_similar_packages(SIMILAR_JSON_FILE)
    for norm_pkg_name, mal_pkg_list in similar_packages.items():
        try:
            download_package(norm_pkg_name)
        except:
            print(f"다운로드 실패. {norm_pkg_name}와 관련된 모든 악성 패키지를 건너뜁니다.")
            continue

        for mal_pkg in mal_pkg_list:
            mal_pkg_name, score = mal_pkg
            if score >= 3.0:
                download_malicious_package(mal_pkg_name, norm_pkg_name)


if __name__ == "__main__":
    run_mal_normal()
