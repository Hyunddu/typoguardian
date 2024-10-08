import json
import os
from clavier import load_qwerty

current_script_path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(current_script_path))
output_file = os.path.join(BASE_DIR, 'typos_clavier.json')
input_file = os.path.join(BASE_DIR, 'typos_DLD.json')


def run_clavier():
    try:
        with open(input_file, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        return
    except json.JSONDecodeError:
        return
    except Exception:
        return

    keyboard = load_qwerty()

    def calculate_keyboard_distance(s1, s2):
        s1 = s1.replace('_', '-')
        s2 = s2.replace('_', '-')
        return sum(keyboard.char_distance(c1, c2) for c1, c2 in zip(s1, s2))

    for pkg, typos_list in data.items():
        processed_typos = []
        for typos, original_score, swapped in typos_list:
            if len(pkg) == len(typos):
                try:
                    keyboard_score = calculate_keyboard_distance(pkg, typos)
                    processed_typos.append([typos, keyboard_score])
                except Exception:
                    continue
        processed_typos.sort(key=lambda x: (x[1] is not None, x[1]))

        data[pkg] = processed_typos

    try:
        with open(output_file, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception:
        pass
