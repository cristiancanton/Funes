import hashlib
import pathlib
import tarfile
import argparse
import csv

import logging
 
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def checksum_md5(filename):
    md5 = hashlib.md5()
    with open(filename,'rb') as f: 
        for chunk in iter(lambda: f.read(8192), b''): 
            md5.update(chunk)
    return md5.hexdigest()

def get_all_relative_files(root_dir):
    """
    Returns a list of relative paths to all files in the given root directory and its subdirectories.
 
    Args:
        root_dir (str): The path to the root directory to search for files.
 
    Returns:
        list: A list of relative paths to all files found.
    """
    root_dir = pathlib.Path(root_dir)
 
    return [file.relative_to(root_dir) for file in root_dir.rglob("*") if file.is_file() and not file.name.startswith(".")]
 
def tar_and_gzip_files(root_dir, output_file, csv_file):
    """
    Tars and gzips all non-hidden files in the given root directory and its subdirectories.
    Additionally, generates a CSV file with file information.
 
    Args:
        root_dir (str): The path to the root directory to search for files.
        output_file (str): The path to the output tar.gz file.
        csv_file (str): The path to the output CSV file.
    """
    root_dir = pathlib.Path(root_dir)
    files = get_all_relative_files(root_dir)
    with tarfile.open(output_file, "w:gz") as tar, open(csv_file, 'w', newline='') as csvfile:
        fieldnames = ['filename', 'md5', 'filesize', 'action']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
 
        for file in files:
            file_path = root_dir / file
            md5 = checksum_md5(str(file_path))
            filesize = file_path.stat().st_size
            writer.writerow({
                'filename': str(file_path),
                'md5': md5,
                'filesize': filesize,
                'action': 'A'
            })
            logging.info(f"Adding file {file} to tarball")
            tar.add(str(file_path), arcname=str(file))

if __name__ == "__main__":
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description='Funes')
    parser.add_argument('input_dir', type=str, help='Input directory')
    parser.add_argument('output_file', type=str, help='Output file')
    parser.add_argument('output_actions', type=str, help='Output file with performed actions')
    args = parser.parse_args()

    # Check if input directory exists
    if not pathlib.Path(args.input_dir).exists():
        logging.error(f"Input directory '{args.input_dir}' does not exist.")
        exit(1)
 
    # Check if input directory is a directory
    if not pathlib.Path(args.input_dir).is_dir():
        logging.error(f"Input directory '{args.input_dir}' is not a directory.")
        exit(1)
 
    # Create tar and gzip file
    logging.info(f"Creating tar and gzip file: {args.output_file}")
    tar_and_gzip_files(args.input_dir, args.output_file, args.output_actions)
    logging.info(f"Tar and gzip file created successfully: {args.output_file}")
