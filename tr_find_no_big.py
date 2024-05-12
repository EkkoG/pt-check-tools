import transmissionrpc
import argparse
from tools import format_size


def main(tc: transmissionrpc.Client, max_size: int):
    all_torrent_in_tr = tc.get_torrents(arguments=['addedDate', 'id' ,'trackerList', 'totalSize', 'name', 'status', 'percentDone', 'rateDownload', 'rateUpload', 'eta', 'error', 'errorString', 'files', 'downloadDir'])
    cache = {}
    for t in all_torrent_in_tr:
        files = t.__getattr__('files')
        files_name = ''.join(list(map(lambda x: x['name'], files)))

        key = t.__getattr__('name') + files_name
        if key not in cache:
            cache[key] = []
        cache[key].append(t)

    t_arr = []
    for k, v in cache.items():
        # sort v by addedDate
        t = sorted(v, key=lambda x: x.__getattr__('addedDate'))
        t_arr.append(t[0])

    group_by_name = {}
    for t in t_arr:
        name = t.__getattr__('name')
        if name not in group_by_name:
            group_by_name[name] = []
        group_by_name[name].append(t)

    for name, ts in group_by_name.items():

        if len(ts) > 1:
            t_max_size = max([t.__getattr__('totalSize') for t in ts])
            # all_size_except_max = sum([t.__getattr__('totalSize') for t in ts]) - max_size
            if t_max_size < max_size * 1024 * 1024 * 1024:
                print(name, '疑似没有合集', '最大种子', format_size(t_max_size))
                print()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=9091)
    parser.add_argument('--user', default='transmission')
    parser.add_argument('--password', default='transmission')
    parser.add_argument('--max', default=3)
    args = parser.parse_args()
    tc = transmissionrpc.Client(args.host, port=args.port, user=args.user, password=args.password)
    main(tc, args.max)


