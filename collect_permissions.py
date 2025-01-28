import os
import stat
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_permissions_and_owner(path: Path):
    """Get permissions, owner, and group of a file."""
    stat_info = path.stat()
    permissions = oct(stat_info.st_mode)[-4:]
    owner = os.getpwuid(stat_info.st_uid).pw_name
    group = os.getgrgid(stat_info.st_gid).gr_name
    return permissions, owner, group

def collect_permissions(base_dir: Path, dry_run: bool, output_file: str):
    """Collect permissions and ownership info for all files and directories."""
    with open(output_file, 'w') as f:
        for root, dirs, files in os.walk(base_dir):
            path = Path(root)
            permissions, owner, group = get_permissions_and_owner(path)
            line = f"{path} {permissions} {owner} {group}\n"
            if dry_run:
                logger.info(f"Dry-run: {line.strip()}")
            else:
                f.write(line)
                logger.info(f"Collected: {line.strip()}")

            # Handle files and directories
            for file_name in files:
                path = Path(root) / file_name
                permissions, owner, group = get_permissions_and_owner(path)
                line = f"{path} {permissions} {owner} {group}\n"
                if dry_run:
                    logger.info(f"Dry-run: {line.strip()}")
                else:
                    f.write(line)
                    logger.info(f"Collected: {line.strip()}")

            for dir_name in dirs:
                path = Path(root) / dir_name
                permissions, owner, group = get_permissions_and_owner(path)
                line = f"{path} {permissions} {owner} {group}\n"
                if dry_run:
                    logger.info(f"Dry-run: {line.strip()}")
                else:
                    f.write(line)
                    logger.info(f"Collected: {line.strip()}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Collect file permissions and ownership information.")
    parser.add_argument("--base-dir", type=str, required=True, help="Base directory to start collecting permissions.")
    parser.add_argument("--output-file", type=str, required=True, help="File to save the collected permission data.")
    parser.add_argument("--dry-run", action="store_true", help="If set, will simulate the collection without writing to the output file.")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).expanduser()

    if not base_dir.exists() or not base_dir.is_dir():
        logger.error(f"Error: {base_dir} is not a valid directory.")
        exit(1)

    logger.info(f"Starting to collect permissions for {base_dir}")
    collect_permissions(base_dir, args.dry_run, args.output_file)
    logger.info(f"Permission collection completed. Data saved to {args.output_file}.")

if __name__ == "__main__":
    main()

