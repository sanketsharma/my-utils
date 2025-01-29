import os
import argparse
import stat
import pwd
import grp
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_permissions_and_owner(path):
    stat_info = os.lstat(path)
    permissions = oct(stat_info.st_mode & 0o777)[2:]
    owner = pwd.getpwuid(stat_info.st_uid).pw_name
    group = grp.getgrgid(stat_info.st_gid).gr_name
    return permissions, owner, group

def collect_permissions(base_dir, output_file):
    base_dir = os.path.abspath(base_dir)  # Ensure absolute path
    logging.info(f"Starting to collect permissions for {base_dir}")
    
    with open(output_file, 'w') as f:
        for root, dirs, files in os.walk(base_dir):
            for entry in dirs + files:
                path = os.path.join(root, entry)
                rel_path = os.path.relpath(path, base_dir)  # Store relative path
                try:
                    permissions, owner, group = get_permissions_and_owner(path)
                    f.write(f"{rel_path} {permissions} {owner} {group}\n")
                    logging.info(f"Collected: {rel_path} {permissions} {owner} {group}")
                except Exception as e:
                    logging.error(f"Failed to get permissions for {path}: {e}")

def restore_permissions(base_dir, input_file, dry_run=False):
    base_dir = os.path.abspath(base_dir)  # Ensure absolute path
    logging.info(f"Restoring permissions in {base_dir} from {input_file}")
    
    with open(input_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 4:
                logging.warning(f"Skipping malformed line: {line.strip()}")
                continue
            
            rel_path, permissions, owner, group = parts
            abs_path = os.path.join(base_dir, rel_path)  # Reconstruct absolute path
            
            if not os.path.exists(abs_path):
                logging.warning(f"Skipping missing file: {abs_path}")
                continue
            
            try:
                if not dry_run:
                    os.chmod(abs_path, int(permissions, 8))
                    os.chown(abs_path, pwd.getpwnam(owner).pw_uid, grp.getgrnam(group).gr_gid)
                logging.info(f"Restored: {abs_path} {permissions} {owner} {group}")
            except Exception as e:
                logging.error(f"Failed to set permissions for {abs_path}: {e}")

if __name__ == "__main__":
    setup_logging()
    parser = argparse.ArgumentParser(description="Collect and restore file permissions.")
    parser.add_argument("--mode", choices=['collect', 'restore'], required=True, help="Mode: collect or restore")
    parser.add_argument("--base-dir", required=True, help="Base directory")
    parser.add_argument("--file", required=True, help="Permissions file")
    parser.add_argument("--dry-run", action='store_true', help="Perform a dry run (for restore mode)")
    
    args = parser.parse_args()
    
    if args.mode == "collect":
        collect_permissions(args.base_dir, args.file)
    elif args.mode == "restore":
        restore_permissions(args.base_dir, args.file, args.dry_run)
