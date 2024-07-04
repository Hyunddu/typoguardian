import os
import json
import zipfile
import subprocess
from tempfile import TemporaryDirectory
from tqdm import tqdm

def analyze_package(package_path):
    cmd = f"guarddog pypi scan {package_path} --output-format=json"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        if "TarSafeException" in e.stderr:
            print(f"Skipping package due to unsafe symlink: {package_path}")
        else:
            print(f"Error running guarddog: {e.stderr}")
        return None
    except json.JSONDecodeError:
        print("Failed to decode JSON response from guarddog")
        return None

def is_valid_tar_gz(file_path):
    if not os.path.isfile(file_path):
        return False
    try:
        with open(file_path, 'rb') as f:
            return f.read(2) == b'\x1f\x8b'
    except IOError:
        return False

def process_zip_file(zip_file_path, output_file):
    all_packages = []
    malicious_count = 0

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        with TemporaryDirectory() as temp_dir:
            zip_ref.extractall(temp_dir)
            package_files = [os.path.join(root, file)
                             for root, _, files in os.walk(temp_dir)
                             for file in files if file.endswith('.tar.gz')]

            for package_file in tqdm(package_files, desc="Analyzing packages"):
                if not is_valid_tar_gz(package_file):
                    print(f"Skipping invalid tar.gz file: {package_file}")
                    continue
                
                analysis_result = analyze_package(package_file)
                
                if analysis_result is None:
                    continue
                
                package_name = os.path.basename(package_file)
                is_malicious = analysis_result['issues'] > 0
                if is_malicious:
                    malicious_count += 1

                package_info = {
                    "package": package_name,
                    "issues": []
                }

                for issue_type, issues in analysis_result['results'].items():
                    for issue in issues:
                        package_info["issues"].append({
                            "location": issue.get("location", ""),
                            "code": issue.get("code", ""),
                            "message": issue.get("message", "")
                        })

                all_packages.append(package_info)

    summary = {
        "total_packages": len(all_packages),
        "malicious_packages": malicious_count
    }

    final_result = {
        "summary": summary,
        "packages": all_packages
    }

    with open(output_file, 'w') as f:
        json.dump(final_result, f, indent=2)

    print(f"Saved {output_file}")

def run_guarddog_analysis():
    process_zip_file('packages.zip', 'dog_result.json')

if __name__ == "__main__":
    run_guarddog_analysis()
