# Getting all files into one db, no versioning

import os
import package_extractor

pkg_dir = 'G:/SteamLibrary/steamapps/common/Destiny 2/packages'

########################################
# Get database files
########################################


def get_version_db():
    seen_pkgs = []
    selected_pkgs = []
    for pkg in os.listdir(pkg_dir):
        if pkg[:-6] not in seen_pkgs:
            seen_pkgs.append(pkg[:-6])
            selected_pkgs.append(pkg)
    for pkg in selected_pkgs:
        p = package_extractor.Package(f'{pkg_dir}/{pkg}')
        p.extract_package(extract=False, largest_patch=True)
        print(f'Written {pkg} to database.')


get_version_db()
