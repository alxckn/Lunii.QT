#!/usr/bin/env python3
"""
Converter: .plain.pk → .v2.pk (STUdio compatible format)

This script converts Lunii .plain.pk archives to .v2.pk format that can be
imported by STUdio for editing.

Usage:
    python plain_to_v2_converter.py input.plain.pk [output.v2.pk]
"""

import os
import sys
import zipfile
import xxtea
from pathlib import Path
from uuid import UUID


# Generic key used for v1/v2 story encryption (from constants.py)
def vectkey_to_bytes(key_vect):
    joined = [k.to_bytes(4, 'little') for k in key_vect]
    return b''.join(joined)


def lunii_tea_rounds(buffer):
    return int(1 + 52 / (len(buffer) / 4))


raw_key_generic = [0x91BD7A0A, 0xA75440A9, 0xBBD49D6C, 0xE0DCC0E3]
lunii_generic_key = vectkey_to_bytes(raw_key_generic)


def encrypt_first_512_bytes(data, key):
    """
    Encrypt the first 512 bytes of data using XXTEA with lunii_generic_key.
    The rest of the data remains unencrypted.
    """
    if len(data) == 0:
        return data

    # Determine how many bytes to encrypt (max 512)
    encrypt_len = min(512, len(data))

    # Extract the portion to encrypt
    to_encrypt = data[:encrypt_len]
    remainder = data[encrypt_len:]

    # Encrypt using XXTEA
    encrypted = xxtea.encrypt(to_encrypt, key, padding=False, rounds=lunii_tea_rounds(to_encrypt))

    # Combine encrypted header with unencrypted remainder
    return encrypted + remainder


def convert_plain_to_v2(input_path, output_path=None):
    """
    Convert a .plain.pk file to .v2.pk format compatible with STUdio.

    Args:
        input_path: Path to input .plain.pk file
        output_path: Optional path to output .v2.pk file (auto-generated if not provided)

    Returns:
        Path to created .v2.pk file
    """
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not input_path.name.endswith('.plain.pk'):
        raise ValueError(f"Input file must be a .plain.pk file: {input_path}")

    print(f"📦 Opening {input_path.name}...")

    # Open the .plain.pk file
    with zipfile.ZipFile(input_path, 'r') as zip_in:
        file_list = zip_in.namelist()

        # Extract UUID from uuid.bin
        if 'uuid.bin' not in file_list:
            raise ValueError("No uuid.bin found in archive")

        uuid_bytes = zip_in.read('uuid.bin')
        story_uuid = UUID(bytes=uuid_bytes)
        uuid_hex = story_uuid.hex.upper()

        print(f"📋 UUID: {story_uuid}")

        # Determine output path
        if output_path is None:
            output_path = input_path.parent / f"{uuid_hex}.v2.pk"
        else:
            output_path = Path(output_path)

        print(f"🔨 Creating {output_path.name}...")

        # Create the .v2.pk file
        with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_out:
            files_processed = 0

            for file_name in file_list:
                # Skip metadata files (not needed in v2 format)
                if file_name in ['uuid.bin', '_metadata.json', '_thumbnail.png']:
                    continue

                # Read file data
                data = zip_in.read(file_name)

                # Determine output filename and encryption
                if file_name == 'ni' or file_name == 'nm':
                    # ni and nm files: no encryption, no extension change
                    new_name = f"{uuid_hex}/{file_name}"
                    output_data = data

                elif file_name.endswith('.plain'):
                    # li.plain, ri.plain, si.plain → encrypt first 512 bytes, remove .plain
                    base_name = file_name.replace('.plain', '')
                    new_name = f"{uuid_hex}/{base_name}"
                    output_data = encrypt_first_512_bytes(data, lunii_generic_key)

                elif file_name.startswith('rf/') or file_name.startswith('rf\\') or '/rf/' in file_name or '\\rf\\' in file_name:
                    # Image files: encrypt first 512 bytes, remove .bmp extension
                    # rf/000/XXYYXXYY.bmp → UUID/rf/000/XXYYXXYY
                    base_name = file_name.replace('\\', '/')
                    if base_name.endswith('.bmp'):
                        base_name = base_name[:-4]
                    new_name = f"{uuid_hex}/{base_name}"
                    output_data = encrypt_first_512_bytes(data, lunii_generic_key)

                elif file_name.startswith('sf/') or file_name.startswith('sf\\') or '/sf/' in file_name or '\\sf\\' in file_name:
                    # Audio files: encrypt first 512 bytes, remove .mp3 extension
                    # sf/000/XXYYXXYY.mp3 → UUID/sf/000/XXYYXXYY
                    base_name = file_name.replace('\\', '/')
                    if base_name.endswith('.mp3'):
                        base_name = base_name[:-4]
                    new_name = f"{uuid_hex}/{base_name}"
                    output_data = encrypt_first_512_bytes(data, lunii_generic_key)

                else:
                    # Unknown file type, skip
                    print(f"⚠️  Skipping unknown file: {file_name}")
                    continue

                # Write to output archive
                zip_out.writestr(new_name, output_data)
                files_processed += 1

                # Progress indicator
                if files_processed % 10 == 0:
                    print(f"   Processed {files_processed} files...")

            print(f"✅ Processed {files_processed} files total")

    print(f"🎉 Conversion complete: {output_path}")
    print(f"📝 You can now import this file into STUdio")

    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python plain_to_v2_converter.py input.plain.pk [output.v2.pk]")
        print()
        print("Converts a .plain.pk file to .v2.pk format compatible with STUdio")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        convert_plain_to_v2(input_file, output_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
