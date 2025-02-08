import os
import argparse
import logging
import shutil  # Use shutil.chown for ownership fixing

# Constants for permissions
FILE_PERMISSIONS = 0o644
DIR_PERMISSIONS = 0o755

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def is_invalid_base_dir(base_dir):
    base_dir = os.path.abspath(base_dir)
    home_dir = os.path.expanduser("~")
    system_dirs = ["/bin", "/usr", "/lib", "/sbin", "/etc", "/boot", "/opt", "/var"]

    # Allow subdirectories of $HOME
    if os.path.samefile(base_dir, home_dir):
        return True  # Prevent running on $HOME directly

    if any(os.path.samefile(os.path.commonpath([base_dir, sys_dir]), sys_dir) for sys_dir in system_dirs):
        return True  # Prevent running on system directories

    return False  # Otherwise, it's valid


def fix_permissions(base_dir, dry_run):
    # Fix base directory permissions first
    fix_dir_permissions(base_dir, dry_run)

    for root, dirs, files in os.walk(base_dir):
        logging.info(f"Processing directory: {root}")

        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            fix_dir_permissions(dir_path, dry_run)

        for file_name in files:
            file_path = os.path.join(root, file_name)
            fix_file_permissions(file_path, dry_run)

def fix_file_permissions(file_path, dry_run):
    if not os.path.islink(file_path):
        if dry_run:
            logging.info(f"Would set file permissions to {oct(FILE_PERMISSIONS)} for {file_path}")
        else:
            os.chmod(file_path, FILE_PERMISSIONS)
            logging.info(f"Set file permissions to {oct(FILE_PERMISSIONS)} for {file_path}")

def fix_dir_permissions(dir_path, dry_run):
    if dry_run:
        logging.info(f"Would set directory permissions to {oct(DIR_PERMISSIONS)} for {dir_path}")
    else:
        os.chmod(dir_path, DIR_PERMISSIONS)
        logging.info(f"Set directory permissions to {oct(DIR_PERMISSIONS)} for {dir_path}")

def fix_ownership(base_dir, user, group, dry_run):
    for root, dirs, files in os.walk(base_dir):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            change_ownership(dir_path, user, group, dry_run)

        for file_name in files:
            file_path = os.path.join(root, file_name)
            change_ownership(file_path, user, group, dry_run)

    change_ownership(base_dir, user, group, dry_run)

def change_ownership(path, user, group, dry_run):
    if dry_run:
        logging.info(f"Would change ownership to {user}:{group} for {path}")
    else:
        shutil.chown(path, user, group)  # Use shutil instead of os.chown()
        logging.info(f"Changed ownership to {user}:{group} for {path}")

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

    user = os.getuid()
    group = os.getgid()

    logging.info(f"Starting permission and ownership fixes for {base_dir}...")
    fix_permissions(base_dir, args.dry_run)
    fix_ownership(base_dir, user, group, args.dry_run)
    logging.info("Finished.")

if __name__ == "__main__":
    main()
