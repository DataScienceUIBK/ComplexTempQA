# Dataset

# Reassemble Split ZIP Files

To reassemble the split ZIP files into the original ZIP file, you can use the following commands:

```bash
cat split_archive.z* > reassembled_archive.zip
zip -s 0 reassembled_archive.zip --out final_archive.zip
