import os
import sys
import shutil
import argparse

def format_size(size):
    if size < 1024:
        return "{} B".format(size)
    elif size < 1024 * 1024:
        return "{} KB".format(round(size / 1024, 2))
    elif size < 1024 * 1024 * 1024:
        return "{} MB".format(round(size / 1024 / 1024, 2))
    else:
        return "{} GB".format(round(size / 1024 / 1024 / 1024, 2))

def is_video_file(file):
    return file.endswith(".mp4") or file.endswith(".mkv") or file.endswith(".avi") or file.endswith(".rmvb")

def find_max_hardlink_count(dir):
    # recursively walk through the directory
    # and find the file with the most hardlinks
    max_count = 0
    min_count = 999
    max_file = None
    for root, dirs, files in os.walk(dir):
        for file in files:
            path = os.path.join(root, file)
            count = os.stat(path).st_nlink
            if count < min_count:
                min_count = count
            if count > max_count:
                max_count = count
                max_file = path
    return max_file, max_count, min_count

def check_all_files_have_hardlink(dir):
    all_is_true = True
    all_stand_alone_files = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            path = os.path.join(root, file)
            count = os.stat(path).st_nlink
            if count == 1 and is_video_file(file):
                all_is_true = False
                all_stand_alone_files.append(path)
    all_stand_alone_files.sort()
    return all_is_true, all_stand_alone_files

def main(dir, level, rm, full, interactive, only_file):
    print("dir", dir, "level", level, "rm", rm, "full", full)

    if only_file:
        for file in os.listdir(dir):
            if is_video_file(file):
                path = os.path.join(dir, file)
                link_count = os.stat(path).st_nlink
                print("文件", path, "大小", format_size(os.path.getsize(path)), "硬链接数", link_count)
                if link_count == 1:
                    print("应该移除", path)
                    if rm:
                        if interactive:
                            response = input("移除文件？")
                            if response == "y" or response == "yes":
                                os.remove(path)
                        else:
                            os.remove(path)
        return


    all_dirs = [os.path.join(dir, f) for f in os.listdir(dir)]
    for i in range(level - 1):
        current_dirs = []
        for file in all_dirs:
            if os.path.isdir(file):
                current_dirs += [os.path.join(file, dir) for dir in os.listdir(file)]
        all_dirs = current_dirs
    
    # remove @eaDir
    all_dirs = [dir for dir in all_dirs if not dir.endswith("@eaDir")]
    # remove .DS_Store
    all_dirs = [dir for dir in all_dirs if not dir.endswith(".DS_Store")]

    all_dirs = [dir for dir in all_dirs if not dir.endswith("incomplete")]

    print("all_dirs", all_dirs)

    if full:
        for dir in all_dirs:
            yes, files = check_all_files_have_hardlink(dir)
            if not yes:
                print("应该移除，不是所有文件都有硬链接:", dir)
                for root, dirs, files in os.walk(dir):
                    for file in files:
                        if is_video_file(file):
                            path = os.path.join(root, file)
                            print("文件", path, "大小", format_size(os.path.getsize(path)), "硬链接数", os.stat(path).st_nlink)
                if rm:
                    if interactive:
                        response = input("移除目录？")
                        if response == "y" or response == "yes":
                            shutil.rmtree(dir)
                    else:
                        shutil.rmtree(dir)

    else:
        for full_path in all_dirs:
            try:
                file, count, min_count = find_max_hardlink_count(full_path)
            except:
                print("error", full_path)
                continue

            if count == 1:
                # remove the dir, whether it's empty or not
                if os.path.isdir(full_path):
                    file_size = sum(os.path.getsize(f) for f in os.listdir(full_path) if os.path.isfile(f))
                    print("应该移除", full_path, "文件大小", file_size)
                    for root, dirs, files in os.walk(full_path):
                        for file in files:
                            path = os.path.join(root, file)
                            print("文件", path, "大小", format_size(os.path.getsize(path)), "硬链接数", os.stat(path).st_nlink)
                    if rm:
                        if interactive:
                            response = input("移除目录？")
                            if response == "y" or response == "yes":
                                shutil.rmtree(full_path)
                        else:
                            shutil.rmtree(full_path)

if __name__ == '__main__':
    # file_size = sum(os.path.getsize(f) for f in os.listdir('/var/services/homes/ciel/qBittorent') if os.path.isfile(f))
    # print(file_size)
    parser = argparse.ArgumentParser()
    parser.add_argument("--rm", help="移除无其他硬连接的文件", action="store_true")
    parser.add_argument("--full", help="检测目录下所有视频文件, 默认只要目录下有一个文件存在其他硬连接即认为", action="store_true")
    parser.add_argument("--only-standalone", help="only print standalone files", action="store_true")
    parser.add_argument("--level", help="the level of the directory to check", type=int, default=1)
    parser.add_argument("--interactive", help="interactive delete", action="store_true")
    parser.add_argument("--only-file", help="only check file", action="store_true")
    parser.add_argument("dir", help="the directory to check")
    args = parser.parse_args()
    main(args.dir, args.level, args.rm, args.full, args.interactive, args.only_file)
