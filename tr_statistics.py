import transmissionrpc
import argparse

def main(tc):
    # get session stats
    stats = tc.session_stats()

    def printttt(s):
        print(f"总活动时间: {s['secondsActive'] / 86400:.2f} 天")
        print(f"总上传量: {s['uploadedBytes'] / 1024 / 1024 / 1024:.2f} GB")
        print(f"平均上传速度: {s['uploadedBytes'] / s['secondsActive'] / 1024 / 1024:.2f} MB/s")
        # print(f"平均每天上传: {s['uploadedBytes'] / s['secondsActive'] / 1024 / 1024 / 1024 * 86400:.2f} GB")
        # print(f"预计一月上传: {s['uploadedBytes'] / s['secondsActive'] / 1024 / 1024 / 1024 / 1024 * 86400 * 30:.2f} TB")
        # print(f"预计一年上传: {s['uploadedBytes'] / s['secondsActive'] / 1024 / 1024 / 1024 / 1024 * 86400 * 365:.2f} TB")
        time = s['secondsActive']
        #day
        if time >= 86400:
            print(f"平均每天上传: {s['uploadedBytes'] / 1024 / 1024 / 1024 / time * 86400:.2f} GB")
        else:
            print(f"预计每天上传: {s['uploadedBytes'] / 1024 / 1024 / 1024 / time * 86400:.2f} GB")
        #month
        if time >= 86400 * 30:
            print(f"平均每月上传: {s['uploadedBytes'] / s['secondsActive'] / 1024 / 1024 / 1024 / 1024 * 86400 * 30:.2f} TB")
        else:
            print(f"预计每月上传: {s['uploadedBytes'] / s['secondsActive'] / 1024 / 1024 / 1024 / 1024 * 86400 * 30:.2f} TB")
        #year
        if time >= 86400 * 365:
            print(f"平均每年上传: {s['uploadedBytes'] / s['secondsActive'] / 1024 / 1024 / 1024 / 1024 * 86400 * 365:.2f} TB")
        else:
            print(f"预计每年上传: {s['uploadedBytes'] / s['secondsActive'] / 1024 / 1024 / 1024 / 1024 * 86400 * 365:.2f} TB")


    print("历史数据:")
    printttt(stats.cumulative_stats)
    print("\n最近数据:")
    printttt(stats.current_stats)

def clean(tc):
    for t in tc.get_torrents(arguments=['id', 'name', 'status', 'percentDone', 'rateDownload', 'rateUpload', 'eta', 'error', 'errorString']):
        error = t.__getattr__('errorString')
        if error:
            print(t.name, error)
        # if 'No data found!' in t.__getattr__('errorString'):
        #     print(t.name, t.__getattr__('errorString'))
            # tc.remove_torrent(t.id, delete_data=False)

def frds_size(tc):
    size = 0
    cache = {}
    for t in tc.get_torrents(arguments=['id', 'priorities', 'wanted', 'files', 'name', 'status', 'percentDone', 'rateDownload', 'rateUpload', 'eta', 'error', 'errorString']):
        if t.name in cache:
            continue
        cache[t.name] = True

        if 'FRDS' in t.name:
            for f in t.files().values():
                size += f['size']
    print(f"FRDS 种子大小: {size / 1024 / 1024 / 1024:.2f} GB")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=9091)
    parser.add_argument('--user', default='transmission')
    parser.add_argument('--password', default='transmission')
    args = parser.parse_args()
    tc = transmissionrpc.Client(args.host, port=args.port, user=args.user, password=args.password)
    # frds_size(tc)
    main(tc)


