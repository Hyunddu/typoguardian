import json
import os
import requests
import zipfile


def download_package(package_name, version, save_path):
    url = f"https://pypi.org/pypi/{package_name}/{version}/json"

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch metadata for {package_name}=={version}")
        return False

    data = response.json()
    try:
        download_url = next(
            release['url'] for release in data['urls']
            if release['packagetype'] == 'sdist'
        )
    except StopIteration:
        print(f"No sdist found for {package_name}=={version}")
        return False

    response = requests.get(download_url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as file:
            file.write(response.content)
        # print(f"Downloaded {package_name}=={version} to {save_path}")
        return True
    else:
        print(f"Failed to download {package_name}=={version}")
        return False


def compress_to_zip(base_save_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_save_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, base_save_path)
                zipf.write(file_path, arcname)
    print(f"Compressed {base_save_path} to {zip_path}")


def run_typos_result_download():
    json_file_path = 'final_typos.json'
    base_save_path = 'pypi_zip'
    zip_path = 'packages.zip'

    with open(json_file_path, 'r') as file:
        data = json.load(file)

    for package_group in data.values():
        for package_info in package_group:
            package_name = package_info[0]
            score = package_info[1]

            if score >= 3.0:
                version_url = f"https://pypi.org/pypi/{package_name}/json"
                response = requests.get(version_url)
                if response.status_code != 200:
                    print(f"Failed to fetch version info for {package_name}")
                    continue

                version_data = response.json()
                version = version_data['info']['version']

                save_path = os.path.join(base_save_path, package_name, version, f"{package_name}-{version}.tar.gz")

                download_package(package_name, version, save_path)

    compress_to_zip(base_save_path, zip_path)


if __name__ == '__main__':
    run_typos_result_download()
