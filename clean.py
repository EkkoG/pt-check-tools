import transmissionrpc
import argparse

def clean(tc, deleted_torrents, file_missing_torrents, rm):
    all = tc.get_torrents(arguments=['id', 'name', 'status', 'percentDone', 'rateDownload', 'rateUpload', 'eta', 'error', 'errorString'])
    error_torrens = [t for t in all if t.__getattr__('errorString')]
    group_by_error = {}
    for t in error_torrens:
        error = t.__getattr__('errorString')
        if error not in group_by_error:
            group_by_error[error] = []
        group_by_error[error].append(t)

    deleted_torrents_errors = ['err torrent banned', 'torrent not registered with this tracker', '006-种子尚未上传或者已经被删除', 'Torrent not exists']
    file_missing_error = ['No data found!']

    if deleted_torrents:
        for error, ts in group_by_error.items():
            for e in deleted_torrents_errors:
                if e in error:
                    for t in ts:
                        print(f"种子已删除, ID: {t.id}， 种子名： {t.name}")
                        if rm:
                            tc.remove_torrent(t.id, delete_data=False)

    if file_missing_torrents:
        for error, ts in group_by_error.items():
            for e in file_missing_error:
                if e in error:
                    for t in ts:
                        print(f"文件丢失, {t.id} {t.name}")
                        if rm:
                            tc.remove_torrent(t.id, delete_data=False)

    for error, ts in group_by_error.items():
        if error not in deleted_torrents_errors and error not in file_missing_error:
            for t in ts:
                print(error, t.id, t.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=9091)
    parser.add_argument('--user', default='transmission')
    parser.add_argument('--password', default='transmission')
    parser.add_argument('--deleted-torrents', help='检测已删除的种子', action='store_true')
    parser.add_argument('--file-missing-torrents', help='检测文件丢失的种子', action='store_true')
    parser.add_argument('--rm', help='删除检测到的种子', action='store_true')
    args = parser.parse_args()
    tc = transmissionrpc.Client(args.host, port=args.port, user=args.user, password=args.password)
    clean(tc, args.deleted_torrents, args.file_missing_torrents, args.rm)


