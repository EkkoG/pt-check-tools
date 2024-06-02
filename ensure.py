import transmissionrpc
import argparse
from functools import reduce
import os
import shutil

def ensure(tc, paths, rm, interactive):
    all = tc.get_torrents(arguments=['id', 'name', 'status', 'percentDone', 'rateDownload', 'rateUpload', 'eta', 'error', 'errorString', 'files', 'downloadDir'])
    def file_paths(torrent):
        downloadDir = torrent.__getattr__('downloadDir')
        files = torrent.__getattr__('files')
        def save_path(path):
            if '/' in path:
                return path.split('/')[0]
            return path

        return list(map(lambda x: downloadDir + '/' + save_path(x.get('name')), files))
    all_files_in_tr = reduce(lambda x, y: x + y, map(file_paths, all))

    all_file_on_disk = []
    for path in paths:
        all_file_on_disk += list(map(path.__add__, os.listdir(path)))

    system_files = ['.DS_Store', '@eaDir', 'incomplete']
    all_file_on_disk = [f for f in all_file_on_disk if not any([x in f for x in system_files])]

    # 查找磁盘上有但是 Transmission 中没有的文件
    diff = set(all_file_on_disk) - set(all_files_in_tr)
    print("磁盘上有但是 Transmission 中没有的文件:")
    for d in diff:
        print(d)
        if rm:
            if interactive:
                if input('删除？(y/n): ') == 'y':
                    if os.path.isdir(d):
                        shutil.rmtree(d)
                    else:
                        os.remove(d)
            else:
                os.remove(d)

    print()

    # 查找 Transmission 中有但是磁盘上没有的文件
    # 这里可以写一个触发检查的逻辑
    diff = set(all_files_in_tr) - set(all_file_on_disk)
    print("Transmission 中有但是磁盘上没有的文件:")
    for d in diff:
        print(d)


    cache = {}
    for t in all:

        files = t.__getattr__('files')
        _file_paths = set(map(lambda x: t.__getattr__('downloadDir') + '/' + x.get('name'), files))
        # if diff in files
        for f in files:
            p = t.__getattr__('downloadDir') + '/' + f.get('name')
            for d in diff:
                if d in p:
                    print("种子", t.__getattr__('name'), "中的文件", f.get('name'), "不存在")
                    print("触发验证", t.id)
                    if t.id not in cache:
                        tc.verify(t.id)
                        cache[t.id] = True
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=9091)
    parser.add_argument('--user', default='transmission')
    parser.add_argument('--password', default='transmission')
    parser.add_argument('--paths', help='the paths to check', nargs='+', required=True)
    parser.add_argument('--rm', help='删除检测到的种子', action='store_true')
    parser.add_argument('--interactive', help='交互式删除', action='store_true')
    args = parser.parse_args()
    tc = transmissionrpc.Client(args.host, port=args.port, user=args.user, password=args.password)
    ensure(tc, args.paths, args.rm, args.interactive)


