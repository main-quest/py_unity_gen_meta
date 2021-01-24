import os
import sys
import uuid
import posixpath


# Generate .meta files for all files/folders in Unity-style.
# If in terminal, execute as 'import py_unity_gen_meta; print py_unity_gen_meta.unity_gen_meta(<directory>)'
# If @param root_dir is not specified, the current dir is processed
def unity_gen_meta(root_dir="."):
    __rec(root_dir)


# Generate from the command-line param for the dir
def unity_gen_meta_from_cmd_arg():

    my_name = sys.argv[0]
    if len(sys.argv) != 2:
        raise Exception(f"{my_name}: exactly 1 arg is expected")

    root_dir = sys.argv[1]
    if not posixpath.isdir(root_dir):
        raise Exception(f"{my_name}: directory '{root_dir}' doesn't exist")
    unity_gen_meta(root_dir)


# As per https://docs.unity3d.com/2019.3/Documentation/Manual/SpecialFolders.html
def __should_ignore(fs_entry_path, is_dir):

    name = posixpath.basename(fs_entry_path)
    if name.startswith('.') or name.endswith('~'):
        return True

    # Dirs can be named "Name.meta" - dunno why you'd do that, but we need to check nonetheless
    if not is_dir:
        if name.endswith('.meta'):
            return True

    return False


def __write_meta_file_if_needed(fs_entry_path, is_dir):
    if __should_ignore(fs_entry_path, is_dir):
        return

    with_meta_path = f"{fs_entry_path}.meta"
    if is_dir:
        if posixpath.isdir(with_meta_path):
            return
    elif posixpath.isfile(with_meta_path):
            return

    generated_uuid = str(uuid.uuid4()).replace("-", "")
    log_prefix = "Dir" if is_dir else "File"
    print(f"+ {log_prefix} '{fs_entry_path}' --> {generated_uuid}")

    with open(with_meta_path, "w") as fd:
        lines = [
            f"fileFormatVersion: 2",
            f"guid: {generated_uuid}"
        ]
        if is_dir:
            lines.append("folderAsset: yes")
        fd.writelines(lines)


def __rec(root_dir):
    for (dir_path, dir_names, file_names) in os.walk(root_dir):
        dir_path_str = str(dir_path).replace('\\', '/')
        for f_name in file_names:
            f_path = posixpath.join(dir_path_str, f_name)
            __write_meta_file_if_needed(f_path, False)
        for d_name in dir_names:
            d_path = posixpath.join(dir_path_str, d_name)
            __write_meta_file_if_needed(d_path, True)

