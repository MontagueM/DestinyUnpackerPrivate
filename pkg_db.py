import sqlite3 as sq
import general_functions as gf
from version import version_str
import os

con = None
c = None


def start_db_connection(version=f'D:/D2_Datamining/Package Unpacker/db_test/{version_str}.db'):
    global con
    global c
    print(version)
    con = sq.connect(version)
    c = con.cursor()


def drop_table(pkg_str_to_drop):
    global c
    c.execute(f'DROP TABLE IF EXISTS {pkg_str_to_drop}')


def add_decoded_entries(decoded_entries, pkg_str):
    global con
    global c
    entries = [(int(decoded_entry.ID), gf.get_flipped_hex(gf.get_hash_from_file(decoded_entry.FileName.upper()), 8).upper(), decoded_entry.FileName.upper(),
               "0x" + gf.fill_hex_with_zeros(hex(decoded_entry.RefID)[2:], 4).upper(),
               "0x" + gf.fill_hex_with_zeros(hex(decoded_entry.RefPackageID)[2:], 4).upper(),
               int(decoded_entry.FileSize),
               int(decoded_entry.Type), int(decoded_entry.SubType), decoded_entry.FileType) for decoded_entry in decoded_entries]
    c.execute(f'CREATE TABLE IF NOT EXISTS {pkg_str} (ID INTEGER, Hash TEXT, FileName TEXT, RefID TEXT, RefPKG TEXT, FileSizeB INTEGER, Type INTEGER, SubType INTEGER, FileType TEXT)')
    c.execute(f'CREATE TABLE IF NOT EXISTS Everything (Hash TEXT, FileName TEXT, RefID TEXT, RefPKG TEXT, FileSizeB INTEGER, Type INTEGER, SubType INTEGER, FileType TEXT)')
    c.executemany(f'INSERT INTO {pkg_str} (ID, Hash, FileName, RefID, RefPKG, FileSizeB, Type, SubType, FileType) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);',
              entries)
    c.executemany(f'INSERT INTO Everything (Hash, FileName, RefID, RefPKG, FileSizeB, Type, SubType, FileType) VALUES(?, ?, ?, ?, ?, ?, ?, ?);',
              [x[1:] for x in entries])
    con.commit()
    print(f"Added {len(decoded_entries)} decoded entries to db")


def get_entries_from_table(pkg_str, column_select='*'):
    global c
    c.execute(f"SELECT {column_select} from {pkg_str}")
    rows = c.fetchall()
    return rows


def get_all_tables():
    c.execute("select * from sqlite_master")
    table_list = c.fetchall()
    return table_list


def mass_renaming_tables():
    # Query the SQLite master table

    tableQuery = "select * from sqlite_master"

    c.execute(tableQuery)

    tableList = c.fetchall()

    # Print the updated listed of tables after renaming the stud table

    for table in tableList:
        # Rename the SQLite Table
        all_pkgs = os.listdir(f'{version_str}/output_all/')
        renameTable = "ALTER TABLE stud RENAME TO student"

        c.execute(renameTable)