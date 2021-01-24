import os
import sys
import uuid
import posixpath


# Generate .meta files for all files/folders in Unity-style.
# If in terminal, execute as py -c 'import py_unity_gen_meta; print py_unity_gen_meta.unity_gen_meta(<directory>)'
# Use double-quotes on Windows
# If @param root_dir is not specified, the current dir is processed
def gen(root_dir="."):
    if not posixpath.isdir(root_dir):
        raise Exception(f"{__file__}: directory '{root_dir}' doesn't exist")
    generator = __Generator()
    generator.rec(root_dir)
    print(f"Done. Generated {generator.dir_count} dirs, {generator.file_count} files.")


# Generate from the command-line param for the dir
def gen_from_cmd_arg():
    if len(sys.argv) != 2:
        raise Exception(f"{__file__}: exactly 1 arg is expected")

    root_dir = sys.argv[1]
    gen(root_dir)


class __Generator(object):

    def __init__(self):
        self.dir_count = 0
        self.file_count = 0

    # As per https://docs.unity3d.com/2019.3/Documentation/Manual/SpecialFolders.html
    @staticmethod
    def __should_ignore(fs_entry_path, is_dir):

        name = posixpath.basename(fs_entry_path)
        if name.startswith('.') or name.endswith('~'):
            return True

        # Dirs can be named "Name.meta" - dunno why you'd do that, but we need to check nonetheless
        if not is_dir:
            if name.endswith('.meta'):
                return True

        return False

    def __write_meta_file_if_needed(self, fs_entry_path, is_dir):
        if self.__should_ignore(fs_entry_path, is_dir):
            return

        with_meta_path = f"{fs_entry_path}.meta"
        if is_dir:
            if posixpath.isfile(with_meta_path):
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

            # writelines doesn't add the nl char: https://stackoverflow.com/a/50223435/7127855
            fd.writelines(s + '\n' for s in lines)

        if is_dir:
            self.dir_count += 1
        else:
            self.file_count += 1

    def rec(self, root_dir):
        for (dir_path, dir_names, file_names) in os.walk(root_dir):
            dir_path_str = str(dir_path).replace('\\', '/')
            for f_name in file_names:
                f_path = posixpath.join(dir_path_str, f_name)
                self.__write_meta_file_if_needed(f_path, False)
            for d_name in dir_names:
                d_path = posixpath.join(dir_path_str, d_name)
                self.__write_meta_file_if_needed(d_path, True)

