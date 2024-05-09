import os
import sys
import argparse
import dbm

cache = {}
db = dbm.open('cache', 'c')

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

def write_cache(f, innode):
    cache[f] = innode
    db[f] = str(innode)

def read_cache(f):
    if f in cache:
        return cache[f]
    return int(db.get(f)) if f in db else None

def main(rm, find_path, dir, check_hard_link):
    all_files = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if is_video_file(file):
                all_files.append(os.path.join(root, file))

    group_by_name = {}
    for f in all_files:
        name = os.path.basename(f)
        name = name[:name.rfind('.')]
        if name not in group_by_name:
            group_by_name[name] = []
        group_by_name[name].append(f)

    # convert to arr
    arr = []
    for name, fs in group_by_name.items():
        arr.append({'name': name, 'files': fs})

    # sort by name
    arr.sort(key=lambda x: x['name'])

    for a in arr:
        if len(a['files']) > 1:
            print(a['name'])
            for f in a['files']:
                print(f)
                # print hard link count
                link_count = os.stat(f).st_nlink
                print("文件", f, "大小", format_size(os.path.getsize(f)), "硬链接数", link_count)
                if link_count == 1:
                    if rm:
                        os.remove(f)
                else:

                    if check_hard_link:
                        innode = os.stat(f).st_ino
                        print("innode", innode)
                        write_cache(f, innode)
                        # find all hard link in path
                        for root, dirs, files in os.walk(find_path):
                            for file in files:
                                path = os.path.join(root, file)
                                t_innode = read_cache(path) or os.stat(path).st_ino
                                write_cache(path, t_innode)
                                if t_innode == innode:
                                    print("硬链接文件", path)

            print()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--rm', help='删除无硬连接文件', action='store_true')
    parser.add_argument('--path', help='文件路径, 用于查找硬连接文件, 当--check-hard-link 为 True 时必须提供', required='--check-hard-link' in sys.argv)
    parser.add_argument('--check-hard-link', help='检查硬连接', action='store_true')
    parser.add_argument('dir', help='文件路径', nargs='?')
    args = parser.parse_args()
    if args.dir is None:
        parser.print_help()
        sys.exit(1)
    main(args.rm, args.path, args.dir, args.check_hard_link)