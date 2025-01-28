import os
import argparse
import logging

# Constants for permissions
FILE_PERMISSIONS = 0o644
DIR_PERMISSIONS = 0o755

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Function to check if the base directory is valid
def is_invalid_base_dir(base_dir):
    base_dir = os.path.abspath(base_dir)
    home_dir = os.path.expanduser("~")
    system_dirs = ["/bin", "/usr", "/lib", "/sbin", "/etc", "/boot", "/opt", "/var"]
    if base_dir == home_dir:
        return True
    if base_dir in system_dirs:
        return True
    if os.path.commonpath([base_dir, home_dir]) == home_dir:
        return False
    return any(os.path.commonpath([base_dir, sys_dir]) == sys_dir for sys_dir in system_dirs)

# Function to fix permissions
def fix_permissions(base_dir, dry_run):
    for root, dirs, files in os.walk(base_dir):
        # Fix directory permissions
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            fix_dir_permissions(dir_path, dry_run)

        # Fix file permissions
        for file_name in files:
            file_path = os.path.join(root, file_name)
            fix_file_permissions(file_path, dry_run)

    # Fix base directory permissions
    fix_dir_permissions(base_dir, dry_run)

# Function to fix file permissions
def fix_file_permissions(file_path, dry_run):
    if not os.path.islink(file_path):  # Do not change permissions of symlink targets
        if dry_run:
            logging.info(f"Would set file permissions to {oct(FILE_PERMISSIONS)} for {file_path}")
        else:
            os.chmod(file_path, FILE_PERMISSIONS)
            logging.info(f"Set file permissions to {oct(FILE_PERMISSIONS)} for {file_path}")

# Function to fix directory permissions
def fix_dir_permissions(dir_path, dry_run):
    if dry_run:
        logging.info(f"Would set directory permissions to {oct(DIR_PERMISSIONS)} for {dir_path}")
    else:
        os.chmod(dir_path, DIR_PERMISSIONS)
        logging.info(f"Set directory permissions to {oct(DIR_PERMISSIONS)} for {dir_path}")

# Function to fix ownership
def fix_ownership(base_dir, user, group, dry_run):
    for root, dirs, files in os.walk(base_dir):
        # Fix directory ownership
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            change_ownership(dir_path, user, group, dry_run)

        # Fix file ownership
        for file_name in files:
            file_path = os.path.join(root, file_name)
            change_ownership(file_path, user, group, dry_run)

    # Fix base directory ownership
    change_ownership(base_dir, user, group, dry_run)

# Function to change ownership
def change_ownership(path, user, group, dry_run):
    if dry_run:
        logging.info(f"Would change ownership to {user}:{group} for {path}")
    else:
        os.chown(path, user, group)
        logging.info(f"Changed ownership to {user}:{group} for {path}")

# Main function
def main():
    parser = argparse.ArgumentParser(description="Fix permissions and ownership.")
    parser.add_argument("--base-dir", required=True, help="Base directory to start fixing.")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run.")
    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_dir)

    if not os.path.exists(base_dir):
        logging.error(f"Base directory {base_dir} does not exist.")
        return

    if is_invalid_base_dir(base_dir):
        logging.error("Invalid base directory. Cannot be $HOME or a system directory.")
        return

    user = os.getuid()  # Get current user ID
    group = os.getgid()  # Get current group ID

    logging.info(f"Starting permission and ownership fixes for {base_dir}...")
    fix_permissions(base_dir, args.dry_run)
    fix_ownership(base_dir, user, group, args.dry_run)
    logging.info("Finished.")

if __name__ == "__main__":
    main()

