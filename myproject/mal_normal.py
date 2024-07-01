import os
import json
import re
import requests

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


def get_github_url(package_info):
    project_urls = package_info["info"]["project_urls"]
    if project_urls:
        return next((url for url in project_urls.values() if "github.com" in url), None)
    return None


def get_github_release_url(github_url):
    match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
    if not match:
        return None
    owner, repo = match.groups()
    releases_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    headers = {
        # 'Authorization': 'Github token',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(releases_url, headers=headers)
        response.raise_for_status()
        release_info = response.json()
        tag_name = release_info['tag_name']
        return f"https://github.com/{owner}/{repo}/archive/refs/tags/{tag_name}.tar.gz"
    except requests.exceptions.RequestException:
        return None


def download_package(package_name, package_type='normal'):
    try:
        package_info = fetch_json(PYPI_URL_TEMPLATE.format(package=package_name))
        latest_version = package_info["info"]["version"]
        tarball_url = next((url['url'] for url in package_info["urls"] if url['packagetype'] == 'sdist'), None)
        if tarball_url is None:
            github_url = get_github_url(package_info)
            if github_url:
                tarball_url = get_github_release_url(github_url)
        if tarball_url is None:
            print(f"{package_name}: 패키지 파일을 찾을 수 없습니다.")
            return
        if package_type == 'normal':
            save_path = os.path.join(SAVE_DIR, package_name, 'normal', latest_version, f'{package_name}-{latest_version}.tar.gz')
        else:
            save_path = os.path.join(SAVE_DIR, package_type, 'malregistry', package_name, latest_version, f'{package_name}-{latest_version}.tar.gz')
        download_file(tarball_url, save_path)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            if "pypi.org" in str(e):
                print(f"{package_name}: 존재하지 않는 패키지입니다.")
            elif "api.github.com" in str(e):
                print(f"{package_name}: 패키지 파일을 찾을 수 없습니다.")
    except requests.exceptions.RequestException:
        print(f"{package_name}: 다운로드 실패")


def run_mal_normal():
    similar_packages = load_similar_packages(SIMILAR_JSON_FILE)
    for norm_pkg_name, mal_pkg_list in similar_packages.items():
        download_package(norm_pkg_name)
        for mal_pkg in mal_pkg_list:
            mal_pkg_name, score = mal_pkg
            if score >= 3.0:
                download_package(mal_pkg_name, package_type=norm_pkg_name)


if __name__ == "__main__":
    run_mal_normal()
