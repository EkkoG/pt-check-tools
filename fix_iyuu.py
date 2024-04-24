import transmissionrpc
import argparse
from functools import reduce
import os

def ensure_same_files(t, another):
    # 检查两个种子的文件是否一致
    # 1. 检查文件数量是否一致
    # 2. 检查文件名是否一致
    # 3. 检查文件大小是否一致
    files = t.__getattr__('files')
    another_files = another.__getattr__('files')
    if len(files) != len(another_files):
        print('文件数量不一致')
        return False
    # 检查文件名是否一致
    for f, af in zip(files, another_files):
        print(f.get('name'), af.get('name'))
        if f.get('name').split('/')[-1] != af.get('name').split('/')[-1]:
            print('文件名不一致')
            return False

    # 检查文件大小是否一致
    for f, af in zip(files, another_files):
        if f.get('length') != af.get('length'):
            print('文件大小不一致')
            return False
    return True

    
     
def fix_torrent(t, all_torrent_in_tr):
    print('未下载完成', t.name)
    files = t.__getattr__('files')
    print(files)

    exts = ['mp4', 'mkv', 'avi', 'rmvb', 'wmv', 'flv', 'mov', 'ts', 'webm']
    video_files = [f for f in files if any([f.get('name').endswith(ext) for ext in exts])]
    video_files = [f.get('name').split('/')[-1] for f in video_files]
    # find a torrent that contains video files in all_torrent_in_tr
    for tt in all_torrent_in_tr:
        if tt == t:
            continue
        files = tt.__getattr__('files')
        if all([any([f.get('name').split('/')[-1] == vf for vf in video_files]) for f in files]) and tt.__getattr__('percentDone') == 1:
            print('找到了一个包含相同视频文件的种子')
            if ensure_same_files(t, tt):
                print('文件信息一致')
                print(tt.name)
                print(files)
                print('删除')

def ensure(tc):
    all_torrent_in_tr = tc.get_torrents(arguments=['id', 'name', 'status', 'percentDone', 'rateDownload', 'rateUpload', 'eta', 'error', 'errorString', 'files', 'downloadDir'])
    for t in all_torrent_in_tr:
        percentDone = t.__getattr__('percentDone')
        if percentDone == 0:
            fix_torrent(t, all_torrent_in_tr)
            print()


            
    



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=9091)
    parser.add_argument('--user', default='transmission')
    parser.add_argument('--password', default='transmission')
    args = parser.parse_args()
    tc = transmissionrpc.Client(args.host, port=args.port, user=args.user, password=args.password)
    ensure(tc)


