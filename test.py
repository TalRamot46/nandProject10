import os

def rename_xml_files(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.xml') and not file.endswith('2.xml'):
                flag = False
                base_name = file[:-4]
                for file2 in files:
                    if file2 == base_name + '2.xml':
                        flag = True
                if not flag:
                    old_path = os.path.join(root, file)
                    new_path = os.path.join(root, base_name + '2.xml')
                    os.rename(old_path, new_path)
                    print(f"[RENAME] {file} → {base_name + '2.xml'}")

def delete_temp_files(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.jack~') or file.endswith('.cmp'):
                path = os.path.join(root, file)
                os.remove(path)
                print(f"[DELETE] Removed {file}")
import subprocess

def run_and_compare(base_dir):
    for root, dirs, files in os.walk(base_dir):
        jack_files = [f for f in files if f.endswith('.jack')]

        # Run JackAnalyzer on each .jack file
        for jack_file in jack_files:
            jack_path = os.path.join(root, jack_file)
            try:
                subprocess.run(['python', '.\\JackAnalyzer.py', jack_path], check=True)
                print(f"[RUN] JackAnalyzer on {jack_path}")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] JackAnalyzer failed on {jack_path}: {e}")
                continue

        # Compare new .xml with renamed *2.xml
        for jack_file in jack_files:
            base_name = os.path.splitext(jack_file)[0]
            xml_new = os.path.join(root, base_name + '.xml')
            xml_old = os.path.join(root, base_name + '2.xml')

            if not os.path.exists(xml_old):
                print(f"[SKIP] Missing renamed XML: {xml_old}")
                continue
            if not os.path.exists(xml_new):
                print(f"[ERROR] New XML output missing: {xml_new}")
                continue

            with open(xml_old, 'r') as f_old, open(xml_new, 'r') as f_new:
                old_lines = f_old.readlines()
                new_lines = f_new.readlines()

            if old_lines == new_lines:
                print(f"[PASS] {xml_new} matches {xml_old}")
            else:
                print(f"[FAIL] {xml_new} does NOT match {xml_old}")
                for i, (l1, l2) in enumerate(zip(old_lines, new_lines)):
                    if l1 != l2:
                        print(f"   First difference at line {i+1}:\n   OLD: {l1.strip()}\n   NEW: {l2.strip()}")
                        break
# Set your base directory
base_dir = "p10"
# Step 3: Run JackAnalyzer and compare
run_and_compare(base_dir)

