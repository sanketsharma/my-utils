import os
import stat
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def set_permissions(path: Path, permissions: str, owner: str, group: str, dry_run: bool):
    """Set permissions and ownership from the provided data. Only log changes in dry-run mode."""
    try:
        # Log the action first
        action = f"Path: {path}, Permissions: {permissions}, Owner: {owner}, Group: {group}"
        if dry_run:
            logger.info(f"Dry-run: {action}")
        else:
            # Set permissions
            mode = int(permissions, 8)  # Convert octal string to integer
            path.chmod(mode)

            # Set ownership
            if owner and group:
                uid = os.getpwnam(owner).pw_uid
                gid = os.getgrnam(group).gr_gid
                path.chown(uid, gid)

            logger.info(f"Updated {path} with Permissions: {permissions}, Owner: {owner}, Group: {group}")
    except Exception as e:
        logger.error(f"Error setting permissions for {path}: {e}")

def process_permissions_file(input_file: Path, dry_run: bool):
    """Process the file with permissions and apply the changes."""
    with input_file.open("r") as file:
        for line in file:
            if line.startswith("Path:"):
                path_str = line.strip().split(": ")[1]
                permissions = file.readline().strip().split(",")[0].split(": ")[1]
                owner = file.readline().strip().split(",")[1].split(": ")[1]
                group = file.readline().strip().split(",")[2].split(": ")[1]

                path = Path(path_str)
                set_permissions(path, permissions, owner, group, dry_run)

def main():
    parser = argparse.ArgumentParser(description="Set permissions and ownership based on a data file.")
    parser.add_argument("--input-file", type=str, required=True, help="Input file with the permissions data.")
    parser.add_argument("--dry-run", action="store_true", help="If set, will simulate the changes without applying them.")
    args = parser.parse_args()

    input_file = Path(args.input_file).resolve()

    if not input_file.exists() or not input_file.is_file():
        logger.error(f"Error: Input file {input_file} does not exist or is not a file.")
        exit(1)

    logger.info(f"Processing file: {input_file}")
    process_permissions_file(input_file, args.dry_run)
    logger.info("Operation completed.")

if __name__ == "__main__":
    main()
