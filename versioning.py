import os
from datetime import datetime
import ast
import package_extractor
import version
import pkg_db
import sqlite3

"""
#Function that writes db in db_files folder for the pkgs in the game folder that were changed today/on a specific today
Function that identifies differences between the newest db and all previous db files
Function that picks out the files that have changed (by unpacking and deleting all that are constants)
"""

versions = {
    '2_8_1_0': '2204',
    '2_8_1_1': '2904',
    '2_8_1_2': '1905',
    '2_8_1_3': '2105',
    '2_9_0_0': '0906',
    '2_9_0_1': '1806',
    '2_9_0_2': '2306',
    '2_9_1_0': '0707',
    '2_9_1_1': '1407',
    '2_9_1_2': '0408',
}

pkg_dir = 'G:/SteamLibrary/steamapps/common/Destiny 2/packages'

########################################
# Get database files
########################################


def get_version_db(version):
    date_added = versions[version]
    selected_pkgs = [x for x, y in get_lewis_dates().items() if y == date_added][::-1]
    if version == '2_8_1_0':
        seen_pkgs = []
        selected_pkgs_2 = []
        for pkg in selected_pkgs:
            if pkg[:-6] not in seen_pkgs:
                seen_pkgs.append(pkg[:-6])
                selected_pkgs_2.append(pkg)
        selected_pkgs = selected_pkgs_2
    print(selected_pkgs)
    for pkg in selected_pkgs:
        p = package_extractor.Package(f'{pkg_dir}/{pkg}')
        p.extract_package(extract=False, largest_patch=False)
        print(f'Written {pkg} to database.')


def get_lewis_dates():
    with open('lewis_pkg_dates.txt', 'r') as f:
        contents = f.read()
        dictionary = ast.literal_eval(contents)
    return dictionary


def get_dict_of_dates():
    dic = {}
    for pkg in os.listdir(pkg_dir):
        date_unix = int(os.path.getmtime(f'{pkg_dir}/{pkg}'))
        date_day_month = datetime.utcfromtimestamp(date_unix).strftime('%d%m')
        dic[pkg] = date_day_month
    return dic


########################################
# Find differences in db files
########################################


def find_differences(version_to_check):
    all_versions = [x.split('.')[0] for x in os.listdir('D:/D2_Datamining/Package Unpacker/db')]
    all_versions.remove(version_to_check)
    pkg_db.start_db_connection(f'db/{version_to_check}.db')
    pkgs_to_check = [x[1][:-13] for x in pkg_db.get_all_tables() if 'Decoded' not in x[1]]

    check_files = {}
    check_file_types = {}
    all_pkg_diffs = {}
    for pkg in pkgs_to_check:
        check_file_types[pkg] = {x: y for x, y in pkg_db.get_entries_from_table(pkg, 'FileName, FileType')}
        check_files[pkg] = [x[0] for x in pkg_db.get_entries_from_table(pkg, 'FileName')]
    for v in all_versions:
        pkg_db.start_db_connection(f'db/{v}.db')
        for pkg in list(pkgs_to_check):
            wrote = False
            try:
                v_entries = {x: y for x, y in pkg_db.get_entries_from_table(pkg, 'FileName, FileType')}
                pkg_files = [x[0] for x in pkg_db.get_entries_from_table(pkg, 'FileName')]
                # Actual comparison
                diff = list(set(check_files[pkg]) - set(pkg_files))
                diff.sort()
                all_pkg_diffs[pkg] = diff
                if diff:  # Remove False to actually write
                    with open(f'versioning/{version_to_check}/{pkg}.txt', 'a') as f:
                        wrote = True
                        f.write(f'{v} versus check against {version_to_check} |  {pkg} diff:')
                        for file in diff:
                            try:
                                f.write(f"\n{file} | {v_entries[file]}")
                            except KeyError:
                                f.write(f"\n{file} | {check_file_types[pkg][file]}")
                pkgs_to_check.remove(pkg)
            except sqlite3.OperationalError:
                pass
            if wrote:
                print(f'Wrote to {version_to_check}/{pkg}.txt')
    for pkg in pkgs_to_check:
        print(f'{pkg} is new!')
        with open(f'versioning/{version_to_check}/{pkg}.txt', 'a') as f:
            f.write(f'{pkg} is new!')
    return all_pkg_diffs

########################################
# Export specific database files
########################################


def export_specific_files(old_pkg_name, file_array):
    # The export directory is going to be C:/d2_pkg_temp/
    pkg_name = find_pkg_name(old_pkg_name)
    pkg = package_extractor.Package(f'{pkg_dir}/{pkg_name}')
    # pkg.extract_package(extract=True, largest_patch=True)
    files = os.listdir(f'C:/d2_pkg_temp/{old_pkg_name}')
    for file in list(files):
        a = file.replace('.bin', '')
        if file.replace('.bin', '') not in file_array:
            print(f'Removing {file}')
            os.remove(f'C:/d2_pkg_temp/{old_pkg_name}/{file}')


def find_pkg_name(pkg):
    for pkg_file in os.listdir(pkg_dir):
        if pkg in pkg_file:
            return pkg_file


if __name__ == '__main__':
    # get_version_db(version.version_str)
    diff = find_differences(version_to_check='2_9_1_0')
    pkg_select = 'black_garden_069b'
    export_specific_files(pkg_select, diff[pkg_select])
