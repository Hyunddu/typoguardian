import yara
import zipfile
import json


def compile_yara_rule(rule_file):
    try:
        with open(rule_file, 'r', encoding='utf-8') as f:
            rule = yara.compile(source=f.read())
        print(f"Compiled rule from file: {rule_file}")
        return rule
    except yara.SyntaxError as e:
        print(f"Syntax error compiling {rule_file}: {e}")
    except yara.Error as e:
        print(f"YARA error compiling {rule_file}: {e}")
    except Exception as e:
        print(f"General error compiling {rule_file}: {e}")
    return None


def extract_and_scan_zip(zip_path, rule):
    print(f"Extracting and scanning zip file: {zip_path}")
    results = {'malicious': [], 'clean': [], 'failed': []}
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                if not member.is_dir():
                    with zip_ref.open(member) as extracted_file:
                        file_content = extracted_file.read()
                        try:
                            match = rule.match(data=file_content)
                            if match:
                                print(f"Match found in file: {member.filename}")
                                results['malicious'].append({
                                    'file_path': member.filename,
                                    'match': [str(m) for m in match]
                                })
                            else:
                                results['clean'].append(member.filename)
                        except Exception as e:
                            print(f"Error scanning file {member.filename}: {e}")
                            results['failed'].append(member.filename)
    except Exception as e:
        print(f"Error extracting or scanning zip file {zip_path}: {e}")
        results['failed'].append(zip_path)
    return results


def run_yara_scan():
    rule_file = 'yara_rules/yaramodel1.yara'
    zip_file = 'packages.zip'

    rule = compile_yara_rule(rule_file)
    if rule:
        results = extract_and_scan_zip(zip_file, rule)

        print("\nMalicious files detected:")
        for entry in results['malicious']:
            print(f"File: {entry['file_path']}, Match: {entry['match']}")

        print("\nClean files:")
        for file_path in results['clean']:
            print(f"File: {file_path}")

        print("\nFailed to scan files:")
        for file_path in results['failed']:
            print(f"File: {file_path}")

        print("\nSummary:")
        print(f"Total malicious files: {len(results['malicious'])}")
        print(f"Total clean files: {len(results['clean'])}")

        with open('yara_scan_results.json', 'w') as json_file:
            json.dump(results, json_file, indent=4)
    else:
        print("No valid YARA rule to apply.")


if __name__ == "__main__":
    run_yara_scan()
