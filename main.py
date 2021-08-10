#!/usr/bin/env python3
# calls all 3 main functions of app for scheduled download and deletion
from delete_local import *
from delete_cloud import *
from daily_download import *

def main():
    # delete any locally saved mp4 file over 1 year old
    delete_old_local()
    # delete any cloud stored recording over 1 week old
    delete_old_cloud()
    # download mp4s from todays meetings
    daily_download()


if __name__ == '__main__':
    main()
