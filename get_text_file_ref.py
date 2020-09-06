import general_functions as gf
import pkg_db


def get_text_file_ref(f):
    pkg_db.start_db_connection('db/2_9_1_2_all.db')
    pkg_name = gf.get_pkg_name(f)
    entries = {x: y for x, y in pkg_db.get_entries_from_table(pkg_name, 'FileName, FileType')}
    bank_file = None
    for i in range(list(entries.keys()).index(f), len(entries.keys())):
        if entries[list(entries.keys())[i]] == 'Text Header':
            bank_file = list(entries.keys())[i]
            break
    if not bank_file:
        print(f'Could not find text header.')
        return
    print(bank_file)
    print(gf.get_flipped_hex(gf.get_hash_from_file(bank_file), 8).upper())
    pkg_name = gf.get_pkg_name('0913-00001211')
    f_hex = gf.get_hex_data(f'C:/d2_output_2_9_1_0/{pkg_name}/0913-00001211.bin')
    offset = f_hex.find(gf.get_flipped_hex(gf.get_hash_from_file(bank_file), 8).upper())
    if offset == -1:
        print('Not in')
        return
    index = int(offset/8 - 48)
    hex_index = gf.get_flipped_hex(gf.fill_hex_with_zeros(hex(index)[2:], 4), 4)
    print(hex_index.upper())


def get_text_file_from_left_hash(left_hash):
    pkg_name = gf.get_pkg_name('0709-00001CF1')
    f_hex = gf.get_hex_data(f'C:/d2_output_2_9_1_0/{pkg_name}/0709-00001CF1.bin')
    offset = f_hex.find(left_hash.upper())
    if offset == -1:
        print('Not in')
        return
    next_hash = f_hex[offset + 32:offset + 40]
    file = gf.get_file_from_hash(gf.get_flipped_hex(next_hash, 8))
    pkg_name = gf.get_pkg_name(file)
    f_hex = gf.get_hex_data(f'C:/d2_output_2_9_1_0/{pkg_name}/{file}.bin')
    print(file)
    ref = f_hex[132*2:132*2+8]
    # print(ref)
    original_file_from_index(ref)


def original_file_from_index(ref):
    ref_rev = gf.get_flipped_hex(ref, 4)
    offset = (int(ref_rev, 16)*8) +48
    pkg_name = gf.get_pkg_name('0913-00001211')
    f_hex = gf.get_hex_data(f'C:/d2_output_2_9_1_0/{pkg_name}/0913-00001211.bin')
    file = gf.get_file_from_hash(gf.get_flipped_hex(f_hex[offset*2+8:offset*2+16], 8))
    pkg_name = gf.get_pkg_name(file)
    f_hex = gf.get_hex_data(f'C:/d2_output_2_9_1_0/{pkg_name}/{file}.bin')
    print(gf.get_file_from_hash(gf.get_flipped_hex(f_hex[48:48+8], 8)))


if __name__ == '__main__':
    # get_text_file_ref('0913-00000CF1')
    # get_text_file_ref('0913-00000CFF')
    # get_text_file_from_left_hash('FC4B756E')  # Traveler's Chosen
    # get_text_file_from_left_hash('B4679F24')  # Fallen Guillotine
    # get_text_file_from_left_hash('ACC393C8')
    # get_text_file_from_left_hash('08CC2B85')
    # original_file_from_index('A60B')  # Traveler's Chosen
    # original_file_from_index('A80B')  # Fallen G
    # get_text_file_ref('0913-00000CF1')
    # get_text_file_ref('0913-00000DCF')
    get_text_file_from_left_hash('FC4B756E')
    get_text_file_from_left_hash('D680818C')
