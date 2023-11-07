"""
BackupManager tests.
"""

import os
from lute.db.setup.main import BackupManager


def test_do_backup(tmp_path):
    """
    Running backup should:
    - create a gz backup file with the timestamp added to the name.
    - delete the oldest files in the backup dir matching the basename pattern.
    - leave any other files alone.
    """
    file_to_backup = tmp_path / "sample.txt"
    backup_dir = tmp_path / "backup"

    # Create the backup directory and a sample file
    os.makedirs(backup_dir)
    with open(file_to_backup, "w", encoding="utf-8") as f:
        f.write("Sample file content")

    backup_count = 3
    bm = BackupManager(file_to_backup, backup_dir, backup_count)

    # Perform initial backups.
    bm.do_backup("2000")
    bm.do_backup("2001")
    bm.do_backup("2002")

    # Next one knocks out the first one.
    bm.do_backup("2003")

    # Check if the number of backups is within the specified limit
    backup_files = list(backup_dir.glob("sample.txt.*.gz"))
    assert len(backup_files) == backup_count

    filenames = [os.path.basename(p) for p in backup_files]
    filenames.sort()
    assert filenames == [
        "sample.txt.2001.gz",
        "sample.txt.2002.gz",
        "sample.txt.2003.gz",
    ]
