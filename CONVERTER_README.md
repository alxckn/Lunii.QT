# Plain.PK to V2.PK Converter

## Overview

This script converts Lunii `.plain.pk` archives to `.v2.pk` format that can be imported by STUdio for editing.

## Requirements

The script uses the `xxtea` library which should already be installed if you have Lunii.QT dependencies:

```bash
pip install xxtea
```

Or install all Lunii.QT dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Convert a `.plain.pk` file (output name will be auto-generated based on UUID):

```bash
python plain_to_v2_converter.py story_name.12345678.plain.pk
```

This will create: `00000000000000000000000012345678.v2.pk`

### Specify Output Name

```bash
python plain_to_v2_converter.py input.plain.pk output.v2.pk
```

### Batch Conversion

Convert multiple files:

```bash
for file in *.plain.pk; do
    python plain_to_v2_converter.py "$file"
done
```

## What the Script Does

1. **Reads** the `.plain.pk` archive
2. **Extracts** the UUID from `uuid.bin`
3. **For each file**:
   - `ni`, `nm`: Copied as-is (no encryption)
   - `li.plain`, `ri.plain`, `si.plain`: First 512 bytes encrypted with lunii_generic_key, `.plain` removed
   - `rf/000/*.bmp`: First 512 bytes encrypted, `.bmp` extension removed
   - `sf/000/*.mp3`: First 512 bytes encrypted, `.mp3` extension removed
4. **Restructures** files into `{UUID}/filename` format
5. **Outputs** a `.v2.pk` file compatible with STUdio

## Format Details

### Input Format (.plain.pk)
```
uuid.bin
_metadata.json (optional)
_thumbnail.png (optional)
ni                      (unencrypted)
li.plain                (unencrypted)
ri.plain                (unencrypted)
si.plain                (unencrypted)
rf/000/XXYYXXYY.bmp    (unencrypted)
sf/000/XXYYXXYY.mp3    (unencrypted)
nm                      (optional, for night mode)
```

### Output Format (.v2.pk / .pk)
```
00000000000000000000000012345678/ni              (unencrypted)
00000000000000000000000012345678/li              (first 512 bytes encrypted)
00000000000000000000000012345678/ri              (first 512 bytes encrypted)
00000000000000000000000012345678/si              (first 512 bytes encrypted)
00000000000000000000000012345678/rf/000/XXYYXXYY (first 512 bytes encrypted, no extension)
00000000000000000000000012345678/sf/000/XXYYXXYY (first 512 bytes encrypted, no extension)
00000000000000000000000012345678/nm              (optional, unencrypted)
```

## Importing into STUdio

After conversion:

1. Open STUdio application
2. **Drag and drop** the `.v2.pk` file onto your connected Lunii device in STUdio
3. STUdio will automatically recognize it as a "FS" format (v2.x) pack
4. The story will be imported and you can edit it

Alternatively:
1. In STUdio, select your device
2. Use the **import** or **transfer** function
3. Select the `.v2.pk` file

## Technical Details

### Encryption

- **Algorithm**: XXTEA (eXtended Tiny Encryption Algorithm)
- **Key**: Generic Lunii key (same for all v1/v2 devices)
- **Rounds**: Dynamic, calculated as `1 + 52 / (buffer_length / 4)`
- **Scope**: Only first 512 bytes of each file (except `ni` and `nm`)

### Why Only 512 Bytes?

The Lunii device only decrypts the first 512 bytes of each file in memory. This is sufficient for:
- Index files (`li`, `ri`, `si`): Usually contain only file paths (< 512 bytes)
- Media files: Headers contain format information; rest is standard MP3/BMP data

## Troubleshooting

### "No uuid.bin found in archive"
- Ensure your input is a valid `.plain.pk` file exported from Lunii.QT

### "Input file must be a .plain.pk file"
- The script expects `.plain.pk` extension. Rename if necessary.

### Import fails in STUdio
- Verify the `.v2.pk` file is not corrupted (check file size)
- Try renaming to just `.pk` instead of `.v2.pk`
- Ensure STUdio is updated to the latest version

### File size increased significantly
- This is normal. The generic key encryption adds minimal overhead, but ZIP compression settings may differ.

## Reverse Conversion (v2.pk → plain.pk)

This script only converts **TO** STUdio format. To convert back:
1. Use Lunii.QT's export function (exports as `.plain.pk`)
2. Or use STUdio's export feature with "Archive" format

## License

This script is part of the Lunii.QT project and follows the same license.

## Credits

- Based on reverse engineering work from the Lunii.QT project
- STUdio compatibility based on the "FS" format (v2.x) specification
