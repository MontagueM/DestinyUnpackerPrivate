from dataclasses import dataclass, fields, field
import numpy as np
import general_functions as gf
import pkg_db
import os
from PIL import Image
from version import version_str
import binascii
from typing import List
import texture2ddecoder

"""
Images are a two-part system. The first file is the image header, containing all the important info. The second part
has the actual image data which uses the header data to transcribe that data to an actual image.
"""


@dataclass
class ImageHeader:
    EntrySize: np.uint32 = np.uint32(0)  # 0
    TextureFormat: np.uint32 = np.uint32(0)  # 4
    Field8: np.uint32 = np.uint32(0)
    Cafe: np.uint16 = np.uint16(0)  # 0xCAFE
    Width: np.uint16 = np.uint16(0)  # E
    Height: np.uint16 = np.uint16(0)  # 10
    Field12: np.uint16 = np.uint16(0)
    Field14: np.uint32 = np.uint32(0)
    Field18: np.uint32 = np.uint32(0)
    Field1C: np.uint32 = np.uint32(0)
    Field20: np.uint32 = np.uint32(0)
    LargeTextureHash: np.uint32 = np.uint32(0)  # 24
    TextureFormatDefined: str = ''

# This header includes the magic number, DDS header, and DXT10 DDS header
@dataclass
class DDSHeader:
    MagicNumber: np.uint32 = np.uint32(0)
    dwSize: np.uint32 = np.uint32(0)
    dwFlags: np.uint32 = np.uint32(0)
    dwHeight: np.uint32 = np.uint32(0)
    dwWidth: np.uint32 = np.uint32(0)
    dwPitchOrLinearSize: np.uint32 = np.uint32(0)
    dwDepth: np.uint32 = np.uint32(0)
    dwMipMapCount: np.uint32 = np.uint32(0)
    dwReserved1: List[np.uint32] = field(default_factory=list)  # size 11, [11]
    dwPFSize: np.uint32 = np.uint32(0)
    dwPFFlags: np.uint32 = np.uint32(0)
    dwPFFourCC: np.uint32 = np.uint32(0)
    dwPFRGBBitCount: np.uint32 = np.uint32(0)
    dwPFRBitMask: np.uint32 = np.uint32(0)
    dwPFGBitMask: np.uint32 = np.uint32(0)
    dwPFBBitMask: np.uint32 = np.uint32(0)
    dwPFABitMask: np.uint32 = np.uint32(0)
    dwCaps: np.uint32 = np.uint32(0)
    dwCaps2: np.uint32 = np.uint32(0)
    dwCaps3: np.uint32 = np.uint32(0)
    dwCaps4: np.uint32 = np.uint32(0)
    dwReserved2: np.uint32 = np.uint32(0)
    dxgiFormat: np.uint32 = np.uint32(0)
    resourceDimension: np.uint32 = np.uint32(0)
    miscFlag: np.uint32 = np.uint32(0)
    arraySize: np.uint32 = np.uint32(0)
    miscFlags2: np.uint32 = np.uint32(0)


DXGI_FORMAT = [
  "DXGI_FORMAT_UNKNOWN",
  "DXGI_FORMAT_R32G32B32A32_TYPELESS",
  "DXGI_FORMAT_R32G32B32A32_FLOAT",
  "DXGI_FORMAT_R32G32B32A32_UINT",
  "DXGI_FORMAT_R32G32B32A32_SINT",
  "DXGI_FORMAT_R32G32B32_TYPELESS",
  "DXGI_FORMAT_R32G32B32_FLOAT",
  "DXGI_FORMAT_R32G32B32_UINT",
  "DXGI_FORMAT_R32G32B32_SINT",
  "DXGI_FORMAT_R16G16B16A16_TYPELESS",
  "DXGI_FORMAT_R16G16B16A16_FLOAT",
  "DXGI_FORMAT_R16G16B16A16_UNORM",
  "DXGI_FORMAT_R16G16B16A16_UINT",
  "DXGI_FORMAT_R16G16B16A16_SNORM",
  "DXGI_FORMAT_R16G16B16A16_SINT",
  "DXGI_FORMAT_R32G32_TYPELESS",
  "DXGI_FORMAT_R32G32_FLOAT",
  "DXGI_FORMAT_R32G32_UINT",
  "DXGI_FORMAT_R32G32_SINT",
  "DXGI_FORMAT_R32G8X24_TYPELESS",
  "DXGI_FORMAT_D32_FLOAT_S8X24_UINT",
  "DXGI_FORMAT_R32_FLOAT_X8X24_TYPELESS",
  "DXGI_FORMAT_X32_TYPELESS_G8X24_UINT",
  "DXGI_FORMAT_R10G10B10A2_TYPELESS",
  "DXGI_FORMAT_R10G10B10A2_UNORM",
  "DXGI_FORMAT_R10G10B10A2_UINT",
  "DXGI_FORMAT_R11G11B10_FLOAT",
  "DXGI_FORMAT_R8G8B8A8_TYPELESS",
  "DXGI_FORMAT_R8G8B8A8_UNORM",
  "DXGI_FORMAT_R8G8B8A8_UNORM_SRGB",
  "DXGI_FORMAT_R8G8B8A8_UINT",
  "DXGI_FORMAT_R8G8B8A8_SNORM",
  "DXGI_FORMAT_R8G8B8A8_SINT",
  "DXGI_FORMAT_R16G16_TYPELESS",
  "DXGI_FORMAT_R16G16_FLOAT",
  "DXGI_FORMAT_R16G16_UNORM",
  "DXGI_FORMAT_R16G16_UINT",
  "DXGI_FORMAT_R16G16_SNORM",
  "DXGI_FORMAT_R16G16_SINT",
  "DXGI_FORMAT_R32_TYPELESS",
  "DXGI_FORMAT_D32_FLOAT",
  "DXGI_FORMAT_R32_FLOAT",
  "DXGI_FORMAT_R32_UINT",
  "DXGI_FORMAT_R32_SINT",
  "DXGI_FORMAT_R24G8_TYPELESS",
  "DXGI_FORMAT_D24_UNORM_S8_UINT",
  "DXGI_FORMAT_R24_UNORM_X8_TYPELESS",
  "DXGI_FORMAT_X24_TYPELESS_G8_UINT",
  "DXGI_FORMAT_R8G8_TYPELESS",
  "DXGI_FORMAT_R8G8_UNORM",
  "DXGI_FORMAT_R8G8_UINT",
  "DXGI_FORMAT_R8G8_SNORM",
  "DXGI_FORMAT_R8G8_SINT",
  "DXGI_FORMAT_R16_TYPELESS",
  "DXGI_FORMAT_R16_FLOAT",
  "DXGI_FORMAT_D16_UNORM",
  "DXGI_FORMAT_R16_UNORM",
  "DXGI_FORMAT_R16_UINT",
  "DXGI_FORMAT_R16_SNORM",
  "DXGI_FORMAT_R16_SINT",
  "DXGI_FORMAT_R8_TYPELESS",
  "DXGI_FORMAT_R8_UNORM",
  "DXGI_FORMAT_R8_UINT",
  "DXGI_FORMAT_R8_SNORM",
  "DXGI_FORMAT_R8_SINT",
  "DXGI_FORMAT_A8_UNORM",
  "DXGI_FORMAT_R1_UNORM",
  "DXGI_FORMAT_R9G9B9E5_SHAREDEXP",
  "DXGI_FORMAT_R8G8_B8G8_UNORM",
  "DXGI_FORMAT_G8R8_G8B8_UNORM",
  "DXGI_FORMAT_BC1_TYPELESS",
  "DXGI_FORMAT_BC1_UNORM",
  "DXGI_FORMAT_BC1_UNORM_SRGB",
  "DXGI_FORMAT_BC2_TYPELESS",
  "DXGI_FORMAT_BC2_UNORM",
  "DXGI_FORMAT_BC2_UNORM_SRGB",
  "DXGI_FORMAT_BC3_TYPELESS",
  "DXGI_FORMAT_BC3_UNORM",
  "DXGI_FORMAT_BC3_UNORM_SRGB",
  "DXGI_FORMAT_BC4_TYPELESS",
  "DXGI_FORMAT_BC4_UNORM",
  "DXGI_FORMAT_BC4_SNORM",
  "DXGI_FORMAT_BC5_TYPELESS",
  "DXGI_FORMAT_BC5_UNORM",
  "DXGI_FORMAT_BC5_SNORM",
  "DXGI_FORMAT_B5G6R5_UNORM",
  "DXGI_FORMAT_B5G5R5A1_UNORM",
  "DXGI_FORMAT_B8G8R8A8_UNORM",
  "DXGI_FORMAT_B8G8R8X8_UNORM",
  "DXGI_FORMAT_R10G10B10_XR_BIAS_A2_UNORM",
  "DXGI_FORMAT_B8G8R8A8_TYPELESS",
  "DXGI_FORMAT_B8G8R8A8_UNORM_SRGB",
  "DXGI_FORMAT_B8G8R8X8_TYPELESS",
  "DXGI_FORMAT_B8G8R8X8_UNORM_SRGB",
  "DXGI_FORMAT_BC6H_TYPELESS",
  "DXGI_FORMAT_BC6H_UF16",
  "DXGI_FORMAT_BC6H_SF16",
  "DXGI_FORMAT_BC7_TYPELESS",
  "DXGI_FORMAT_BC7_UNORM",
  "DXGI_FORMAT_BC7_UNORM_SRGB",
  "DXGI_FORMAT_AYUV",
  "DXGI_FORMAT_Y410",
  "DXGI_FORMAT_Y416",
  "DXGI_FORMAT_NV12",
  "DXGI_FORMAT_P010",
  "DXGI_FORMAT_P016",
  "DXGI_FORMAT_420_OPAQUE",
  "DXGI_FORMAT_YUY2",
  "DXGI_FORMAT_Y210",
  "DXGI_FORMAT_Y216",
  "DXGI_FORMAT_NV11",
  "DXGI_FORMAT_AI44",
  "DXGI_FORMAT_IA44",
  "DXGI_FORMAT_P8",
  "DXGI_FORMAT_A8P8",
  "DXGI_FORMAT_B4G4R4A4_UNORM",
  "DXGI_FORMAT_P208",
  "DXGI_FORMAT_V208",
  "DXGI_FORMAT_V408",
  "DXGI_FORMAT_SAMPLER_FEEDBACK_MIN_MIP_OPAQUE",
  "DXGI_FORMAT_SAMPLER_FEEDBACK_MIP_REGION_USED_OPAQUE",
  "DXGI_FORMAT_FORCE_UINT"
]


def write_file(header, file_hex):
    with open('bc7_dds.dds', 'wb') as b:
        for f in fields(header):
            if f.type == np.uint32:
                flipped = "".join(gf.get_flipped_hex(gf.fill_hex_with_zeros(hex(np.uint32(getattr(header, f.name)))[2:], 8), 8))
            elif f.type == List[np.uint32]:
                flipped = ''
                for val in getattr(header, f.name):
                    flipped += "".join(
                        gf.get_flipped_hex(gf.fill_hex_with_zeros(hex(np.uint32(val))[2:], 8), 8))
            else:
                print(f'ERROR {f.type}')
                return
            b.write(binascii.unhexlify(flipped))
        b.write(binascii.unhexlify(file_hex))


def get_header(file_hex):
    img_header = ImageHeader()
    for f in fields(img_header):
        if f.type == np.uint32:
            flipped = "".join(gf.get_flipped_hex(file_hex, 8))
            value = np.uint32(int(flipped, 16))
            setattr(img_header, f.name, value)
            file_hex = file_hex[8:]
        elif f.type == np.uint16:
            flipped = "".join(gf.get_flipped_hex(file_hex, 4))
            value = np.uint16(int(flipped, 16))
            setattr(img_header, f.name, value)
            file_hex = file_hex[4:]
    return img_header


def define_texture_format(texture_format):
    if DXGI_FORMAT[texture_format] == 'DXGI_FORMAT_BC1_UNORM':
        return 'BC1'
    elif DXGI_FORMAT[texture_format] == 'DXGI_FORMAT_BC1_UNORM_SRGB':
        return 'BC1_SRGB'
    elif DXGI_FORMAT[texture_format] == 'DXGI_FORMAT_BC7_UNORM':
        return 'BC7'
    elif DXGI_FORMAT[texture_format] == 'DXGI_FORMAT_BC7_UNORM_SRGB':
        return 'BC7_SRGB'
    elif DXGI_FORMAT[texture_format] == 'DXGI_FORMAT_R8G8B8A8_UNORM':
        return 'RGBA'
    elif DXGI_FORMAT[texture_format] == 'DXGI_FORMAT_R8G8B8A8_UNORM_SRGB':
        return 'RGBA_SRGB'
    elif DXGI_FORMAT[texture_format] == 'DXGI_FORMAT_BC3_UNORM_SRGB':
        return 'BC3_SRGB'
    elif DXGI_FORMAT[texture_format] == 'DXGI_FORMAT_BC4_UNORM':
        return 'BC4'
    elif DXGI_FORMAT[texture_format] == 'DXGI_FORMAT_BC5_UNORM':
        return 'BC5'
    else:
        return DXGI_FORMAT[texture_format]
    # DXGI_FORMAT_BC6H_UF16 is HDR, don't think I'm able to extract easily
    # Some other unsupported formats: DXGI_FORMAT_R8_UNORM, DXGI_FORMAT_R16G16B16A16_FLOAT, DXGI_FORMAT_BC5_UNORM


def get_image_from_file(file_path):
    pkg_db.start_db_connection()
    file_name = file_path.split('/')[-1].split('.')[0]
    file_pkg = file_path.split('/')[-2]
    # To get the actual image data we need to pull this specific file's data from the database as it references its file
    # in its RefID.
    entries = pkg_db.get_entries_from_table(file_pkg, 'FileName, RefID, RefPKG, FileType')
    this_entry = [x for x in entries if x[0] == file_name][0]
    ref_file_name = f'{this_entry[2][2:]}-{gf.fill_hex_with_zeros(this_entry[1][2:], 8)}'
    if this_entry[-1] == 'Texture Header':
        header_hex = gf.get_hex_data(file_path)
        data_hex = gf.get_hex_data(f'{"/".join(file_path.split("/")[:-1])}/{ref_file_name}.bin')
    elif this_entry[-1] == 'Texture Data':
        print('Only pass through header please, cba to fix this.')
        return
    else:
        print(f"File given is not texture data or header of type {this_entry[-1]}")
        return

    header = get_header(header_hex)
    dimensions = [header.Width, header.Height]
    header.TextureFormatDefined = define_texture_format(header.TextureFormat)
    # large_file = gf.get_file_from_hash(gf.get_flipped_hex(header.LargeTextureHash, 8))
    # pkg_name = gf.get_pkg_name(large_file)
    # data_hex = gf.get_hex_data(f'C:/d2_output/{pkg_name}/{large_file}.bin')
    img = get_image_from_data(header, dimensions, data_hex)
    if img:
        img.save(f'C:/d2_output_2_9_2_0_images/{file_pkg}/{file_name}.png')
        img.show()


def get_images_from_pkg(pkg_path):
    pkg_db.start_db_connection()
    all_files = os.listdir(pkg_path)
    file_pkg = pkg_path.split('/')[-2]
    entries = pkg_db.get_entries_from_table(file_pkg, 'FileName, RefID, RefPKG, FileType')
    for file in all_files[::-1]:
        file_name = file.split('.')[0]
        file_path = pkg_path + file
        # To get the actual image data we need to pull this specific file's data from the database as it references its
        #  file in its RefID.
        try:
            this_entry = [x for x in entries if x[0] == file_name][0]
        except IndexError:
            continue
        ref_file_name = f'{this_entry[2][2:]}-{gf.fill_hex_with_zeros(this_entry[1][2:], 4)}'
        if this_entry[-1] == 'Texture Header':
            header_hex = gf.get_hex_data(file_path)
            try:
                direc = [x for x in os.listdir(f'C:/d2_output/') if this_entry[2].lower()[2:] in x][0]
            except IndexError:
                continue
            data_hex = gf.get_hex_data(f'C:/d2_output/{direc}/{ref_file_name}.bin')
        else:
            # print("File given is not texture data or header.")
            continue

        try:
            os.mkdir(f'C:/d2_output_2_9_2_0_images/')
            os.mkdir(f'C:/d2_output_2_9_2_0_images/{file_pkg}/')
        except FileExistsError:
            try:
                os.mkdir(f'C:/d2_output_2_9_2_0_images/{file_pkg}/')
            except FileExistsError:
                pass
        header = get_header(header_hex)
        # print(f'Getting image data for file {this_entry[0]}')
        dimensions = [int(header.Width), int(header.Height)]

        header.TextureFormatDefined = define_texture_format(header.TextureFormat)
        # print(file_name, header.TextureFormat)
        large_tex_hash = hex(header.LargeTextureHash)[2:].upper()
        # print(large_tex_hash)
        if large_tex_hash != 'FFFFFFFF':
            large_file = gf.get_file_from_hash(large_tex_hash)
            pkg_name = gf.get_pkg_name(large_file)
            data_hex = gf.get_hex_data(f'C:/d2_output/{pkg_name}/{large_file}.bin')
        img = get_image_from_data(header, dimensions, data_hex)
        if img and img != 'Invalid':
            img.save(f'C:/d2_output_2_9_2_0_images/{file_pkg}/{file_name}.png')
            print(f'Saved {file_name}')
        elif img and img == 'Invalid':
            print(f'{file_name} {header.TextureFormatDefined} not saved')


def get_image_from_data(header, dimensions, data_hex):
    img = None
    if 'RGBA' in header.TextureFormatDefined:
        try:
            img = Image.frombytes('RGBA', dimensions, bytes.fromhex(data_hex))
        except ValueError:
            return 'Invalid'
    elif 'BC1' in header.TextureFormatDefined:
        try:
            img = Image.frombytes('RGBA', dimensions, bytes.fromhex(data_hex), 'bcn', (1,))
        except ValueError:
            # bc1_decomp(header, data_hex)
            try:
                dec = texture2ddecoder.decode_bc1(bytes.fromhex(data_hex), header.Width, header.Height)
                img = Image.frombytes('RGBA', dimensions, dec, 'raw', ("BGRA"))
            except ValueError:
                return 'Invalid'
    elif 'BC3' in header.TextureFormatDefined:
        try:
            img = Image.frombytes('RGBA', dimensions, bytes.fromhex(data_hex), 'bcn', (3,))
        except ValueError:
            try:
                dec = texture2ddecoder.decode_bc3(bytes.fromhex(data_hex), header.Width, header.Height)
                img = Image.frombytes('RGBA', dimensions, dec, 'raw', ("BGRA"))
            except ValueError:
                return 'Invalid'
    elif 'BC4' in header.TextureFormatDefined:
        try:
            img = Image.frombytes('RGBA', dimensions, bytes.fromhex(data_hex), 'bcn', (4,))
        except ValueError:
            try:
                dec = texture2ddecoder.decode_bc4(bytes.fromhex(data_hex), header.Width, header.Height)
                img = Image.frombytes('RGBA', dimensions, dec, 'raw', ("BGRA"))
            except ValueError:
                return 'Invalid'
    elif 'BC5' in header.TextureFormatDefined:
        try:
            img = Image.frombytes('RGBA', dimensions, bytes.fromhex(data_hex), 'bcn', (5,))
        except ValueError:
            try:
                dec = texture2ddecoder.decode_bc5(bytes.fromhex(data_hex), header.Width, header.Height)
                img = Image.frombytes('RGBA', dimensions, dec, 'raw', ("BGRA"))
            except ValueError:
                return 'Invalid'
    elif 'BC6' in header.TextureFormatDefined:
        # bc6h_decomp(header, data_hex)
        try:
            img = Image.frombytes('RGBA', dimensions, bytes.fromhex(data_hex), 'bcn', (6,))
        except ValueError:
            try:
                dec = texture2ddecoder.decode_bc6(bytes.fromhex(data_hex), header.Width, header.Height)
                img = Image.frombytes('RGBA', dimensions, dec, 'raw', ("BGRA"))
            except ValueError:
                return 'Invalid'
    elif 'BC7' in header.TextureFormatDefined:
        # print('Size', int(len(data_hex)/2), '|', header.TextureFormatDefined, dimensions)
        try:
            img = Image.frombytes('RGBA', dimensions, bytes.fromhex(data_hex), 'bcn', (7,))
        except ValueError:
            # bc7_decomp(header, data_hex)
            try:
                dec = texture2ddecoder.decode_bc7(bytes.fromhex(data_hex), header.Width, header.Height)
                img = Image.frombytes('RGBA', dimensions, dec, 'raw', ("BGRA"))
            except ValueError:
                return 'Invalid'
    else:
        print(f'Image not supported type {header.TextureFormatDefined}')
    return img

# https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide describes everything for dw_pitch


# def bc1_decomp(header, data_hex):
#     """
#     8 bytes per 4x4 pixel block
#     dwFourCC "DXT1"
#     dwFlags DDS_FOURCC
#     """
#     width_hex = gf.get_flipped_hex(gf.fill_hex_with_zeros(hex(header.Width)[2:], 8), 8).upper()
#     height_hex = gf.get_flipped_hex(gf.fill_hex_with_zeros(hex(header.Height)[2:], 8), 8).upper()
#     block_size = 16
#     dw_pitch_or_linear_size = np.uint32(max(1, ((header.Width+3) / 4) * block_size))
#     dw_hex = gf.get_flipped_hex(gf.fill_hex_with_zeros(hex(int(dw_pitch_or_linear_size))[2:], 8), 8).upper()
#     ######
#     data_size = int(len(data_hex)/2)
#     c_data_size = int(data_size/2)  # c_ is since its BC7 compressed, it is stored with half the size for normal
#
#
#     bc1_header = DDSHeader()
#     bc1_header.MagicNumber = int('20534444', 16)
#     bc1_header.dwSize = 124
#     bc1_header.dwFlags = (0x1 + 0x2 + 0x4 + 0x1000) + 0x80000
#     bc1_header.dwHeight = header.Height
#     bc1_header.dwWidth = header.Width
#     bc1_header.dwPitchOrLinearSize = max(1, (bc1_header.dwWidth+3)/4)*block_size
#     bc1_header.dwDepth = 0
#     bc1_header.dwMipMapCount = 0
#     bc1_header.dwReserved1 = [0]*11
#     bc1_header.dwPFSize = 32
#     bc1_header.dwPFFlags = 0x1 + 0x4
#     bc1_header.dwPFFourCC = int('30315844', 16)
#     bc1_header.dwPFRGBBitCount = 0
#     bc1_header.dwPFRBitMask = 0  # All of these are 0 as it is compressed data
#     bc1_header.dwPFGBitMask = 0
#     bc1_header.dwPFBBitMask = 0
#     bc1_header.dwPFABitMask = 0
#     bc1_header.dwCaps = 0x1000 + 0x8
#     bc1_header.dwCaps2 = 0x200 + 0x400 + 0x800 + 0x1000 + 0x2000 + 0x4000 + 0x8000  # All faces for cubemap
#     bc1_header.dwCaps3 = 0
#     bc1_header.dwCaps4 = 0
#     bc1_header.dwReserved2 = 0
#     bc1_header.dxgiFormat = header.TextureFormat
#     bc1_header.resourceDimension = 3  # DDS_DIMENSION_TEXTURE2D
#     bc1_header.miscFlag = 0 + 0x4
#     # int(((int(bc1_header.dwWidth) * int(bc1_header.dwHeight)) + 320) / c_data_size)
#     bc1_header.arraySize = 1
#     bc1_header.miscFlags2 = 0x1 #?
#     print(f'Array size {bc1_header.arraySize}')
#     write_file(bc1_header, data_hex)


# def bc7_decomp(header, data_hex):
#     """
#     In BC7 we're working with only compressed data. This means:
#     - need DDSD_LINEARSIZE for dwFlags
#     - dwPitchOrLinearSize is "total number of bytes in the top level texture for a compressed texture"
#     - block_size = 16
#
#     We also need to be able to identify cubemaps since this changes:
#     - dwCaps DDSCAPS_COMPLEX
#     - all of dwCaps2 info
#     - DDS_RESOURCE_MISC_TEXTURECUBE
#     - "Starting with DirectX 8, a cube map is stored with all faces defined." so 6 faces immediately.
#     """
#     width_hex = gf.get_flipped_hex(gf.fill_hex_with_zeros(hex(header.Width)[2:], 8), 8).upper()
#     height_hex = gf.get_flipped_hex(gf.fill_hex_with_zeros(hex(header.Height)[2:], 8), 8).upper()
#     block_size = 16
#     dw_pitch_or_linear_size = np.uint32(max(1, ((header.Width+3) / 4) * block_size))
#     dw_hex = gf.get_flipped_hex(gf.fill_hex_with_zeros(hex(int(dw_pitch_or_linear_size))[2:], 8), 8).upper()
#     ######
#     data_size = int(len(data_hex)/2)
#     c_data_size = int(data_size/2)  # c_ is since its BC7 compressed, it is stored with half the size for normal
#
#
#     bc7_header = DDSHeader()
#     bc7_header.MagicNumber = int('20534444', 16)
#     bc7_header.dwSize = 124
#     bc7_header.dwFlags = (0x1 + 0x2 + 0x4 + 0x1000) + 0x80000
#     bc7_header.dwHeight = header.Height
#     bc7_header.dwWidth = header.Width
#     bc7_header.dwPitchOrLinearSize = max(1, (bc7_header.dwWidth+3)/4)*block_size
#     bc7_header.dwDepth = 0
#     bc7_header.dwMipMapCount = 0
#     bc7_header.dwReserved1 = [0]*11
#     bc7_header.dwPFSize = 32
#     bc7_header.dwPFFlags = 0x1 + 0x4
#     bc7_header.dwPFFourCC = int('30315844', 16)
#     bc7_header.dwPFRGBBitCount = 0
#     bc7_header.dwPFRBitMask = 0  # All of these are 0 as it is compressed data
#     bc7_header.dwPFGBitMask = 0
#     bc7_header.dwPFBBitMask = 0
#     bc7_header.dwPFABitMask = 0
#     bc7_header.dwCaps = 0x1000 + 0x8
#     bc7_header.dwCaps2 = 0x200 + 0x400 + 0x800 + 0x1000 + 0x2000 + 0x4000 + 0x8000  # All faces for cubemap
#     bc7_header.dwCaps3 = 0
#     bc7_header.dwCaps4 = 0
#     bc7_header.dwReserved2 = 0
#     bc7_header.dxgiFormat = header.TextureFormat
#     bc7_header.resourceDimension = 3  # DDS_DIMENSION_TEXTURE2D
#     bc7_header.miscFlag = 0 + 0x4
#     # int(((int(bc7_header.dwWidth) * int(bc7_header.dwHeight)) + 320) / c_data_size)
#     bc7_header.arraySize = 1
#     bc7_header.miscFlags2 = 0x1 #?
#     print(f'Array size {bc7_header.arraySize}')
#     write_file(bc7_header, data_hex)
#     return True


# def bc6h_decomp(header, data_hex):
#     width_hex = gf.get_flipped_hex(gf.fill_hex_with_zeros(hex(header.Width)[2:], 8), 8)
#     height_hex = gf.get_flipped_hex(gf.fill_hex_with_zeros(hex(header.Height)[2:], 8), 8)
#     tex_form_hex = '5F00'
#     block_size = 16
#     dw_pitch_or_linear_size = max(1, ((header.Width) / 4) * block_size)
#     # dw_pitch_or_linear_size = '001E'
#     dw_hex = gf.get_flipped_hex(gf.fill_hex_with_zeros(hex(int(dw_pitch_or_linear_size))[2:], 8), 8).upper()
#     bc6h_header = f'444453207C00000006000000{height_hex}{width_hex}{dw_hex}0000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000040000004458313000000000000000000000000000000000000000000010000000000000000000000000000000000000{tex_form_hex}000003000000000000000100000000000000'
#     bc6h_hex = bc6h_header + data_hex
#     with open(f'test_dds_out/bc6h.dds', 'wb') as f:
#         f.write(binascii.unhexlify(bc6h_hex))
#     print()
#     return True


def get_images_in_pkgs():
    for pkg in os.listdir(f'C:/d2_output/')[::-1]:
        if 'commando' in pkg:
            print(f'Getting from pkg {pkg}')
            get_images_from_pkg(f'C:/d2_output/{pkg}/')


def compare_images_hash():
    import imagehash
    cutoff = 5
    old_versions = ['2_9_0_1', '2_9_0_2']
    old_images_dir = f'{old_version_str}/images_all/'
    new_images_dir = f'{version_str}/images_all/'

    for folder in os.listdir(new_images_dir):
        for img in os.listdir(new_images_dir + folder):
            original = Image.open(new_images_dir + folder + '/' + img)
            hash0 = imagehash.average_hash(original)
            diff = Image.open(old_images_dir + folder + '/' + img)
            hash1 = imagehash.average_hash(diff)
            if hash0 - hash1 < cutoff:
                # print(f'{img} images are similar')
                pass
            else:
                print(f'{img} images are not similar')
        print(list(set(os.listdir(new_images_dir + folder)) - set(os.listdir(old_images_dir + folder))))


def compare_images_names():
    old_versions = ['2_9_0_1']
    new_pkgs = os.listdir(f'{version_str}/images_all/')
    compared_pkgs = []
    print(new_pkgs)
    for old_version_str in old_versions[::-1]:
        old_pkgs = os.listdir(f'{old_version_str}/images_all/')
        for pkg in new_pkgs:
            if pkg in old_pkgs and pkg not in compared_pkgs:
                compared_pkgs.append(pkg)  # Don't want to version multiple times, just most recent
                images_old = os.listdir(f'{old_version_str}/images_all/{pkg}')
                images_new = os.listdir(f'{version_str}/images_all/{pkg}')
                new_images = list(set(images_new) - set(images_old))
                print(f'New images for {pkg}: {new_images}')


if __name__ == '__main__':
    # get_image_from_file('2_9_0_1/output_all/ui_01a3/01A3-000003CF.bin')
    # environments_0957
    # get_images_from_pkg(f'{version_str}/output_all/sandbox_0696/')
    # c = 0
    # for pkg in os.listdir('D:/D2_Datamining/Package Unpacker/2_9_0_1/output_all'):
    #     if 'activities' in pkg:
    #         print(pkg, c)
    #         c += 1
    #         # if c <= 19:
    #         #     continue
    #         print('Getting images for', pkg)
    #         get_images_from_pkg(f'{version_str}/output_all/{pkg}/')
    get_images_in_pkgs()
    # compare_images()
    # get_images_from_pkg(f'{version_str}/output_all/cayde_6_feet_under_0368/')
    # fix issues with some images needing try except
    # compare_images_names()
