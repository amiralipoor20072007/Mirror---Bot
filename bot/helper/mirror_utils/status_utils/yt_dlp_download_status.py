#!/usr/bin/env python3
from bot import DOWNLOAD_DIR
from bot.helper.ext_utils.bot_utils import MirrorStatus, get_readable_file_size, get_readable_time, async_to_sync
from bot.helper.ext_utils.fs_utils import get_path_size

class YtDlpDownloadStatus:
    def __init__(self, obj, listener, gid):
        self.__obj = obj
        self.__uid = listener.uid
        self.__gid = gid
        self.message = listener.message
        self.__listener = listener

    def listener(self):
        return self.__listener

    def gid(self):
        return self.__gid

    def processed_bytes(self):
        if self.__obj.downloaded_bytes != 0:
          return self.__obj.downloaded_bytes
        else:
          return async_to_sync(get_path_size, f"{DOWNLOAD_DIR}{self.__uid}")

    def size_raw(self):
        return self.__obj.size

    def size(self):
        return get_readable_file_size(self.size_raw())

    def status(self):
        return MirrorStatus.STATUS_DOWNLOADING

    def name(self):
        return self.__obj.name

    def progress_raw(self):
        return self.__obj.progress

    def progress(self):
        return f'{round(self.progress_raw(), 2)}%'

    def speed_raw(self):
        """
        :return: Download speed in Bytes/Seconds
        """
        return self.__obj.download_speed

    def speed(self):
        return f'{get_readable_file_size(self.speed_raw())}/s'

    def eta(self):
        if self.__obj.eta != '-':
            return f'{get_readable_time(self.__obj.eta)}'
        try:
            seconds = (self.size_raw() - self.processed_bytes()) / self.speed_raw()
            return f'{get_readable_time(seconds)}'
        except:
            return '-'

    def download(self):
        return self.__obj
