#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'andyguo'

import os
import sys
import multiprocessing as mp
from functools import partial
from itertools import izip
import time

# buffer size default is 4M
BLOCKSIZE = 4096 * 1024


def worker(conn, back, num, lock):
    current_proc_name = mp.current_process().name
    time.sleep(1)
    local_number = 0
    get_lock = False
    while True:
        src, dst = conn.get()
        # print u'[{}]:\t{}'.format(current_proc_name, src)

        if src is None:
            print u'[{}]:\tterminated'.format(current_proc_name)
            back.put((current_proc_name, None))
            break

        if os.path.exists(dst):
            # print u'[{}]:\tskip\t{}'.format(current_proc_name, dst)
            temp_size = os.path.getsize(src)
            lock.acquire()
            num.value += temp_size
            lock.release()
            continue

        with open(src, 'r') as src_file:
            try:
                os.makedirs(os.path.dirname(dst))
            except:
                pass

            with open(dst, 'w') as dst_file:
                local_number = 0
                get_lock = False
                for buf_data in iter((lambda: src_file.read(BLOCKSIZE)), ''):
                    dst_file.write(buf_data)
                    local_number += BLOCKSIZE
                    get_lock = lock.acquire(block=False)
                    if get_lock:
                        num.value += local_number
                        local_number = 0.0
                        # print num.value
                        lock.release()

        lock.acquire()
        num.value += local_number
        lock.release()


class MULTI_COPY(object):
    def __init__(self, num_process=4):
        self.file_size = mp.Value('d', 0.0)
        self.total_size = 0
        self.percent = 0.0
        self.lock = mp.Lock()
        self.pool_size = num_process
        self.queue = mp.Queue()
        self.queue2 = mp.Queue()
        self.done = False

    def run(self, from_files, to_files, file_size=None):
        self.done = False
        workers = [mp.Process(target=worker, args=(self.queue, self.queue2, self.file_size, self.lock))
                   for x in range(self.pool_size)]
        [x.start() for x in workers]

        for file_pair in izip(from_files, to_files):
            # print file_pair
            if not os.path.isfile(file_pair[0]):
                continue

            self.total_size += os.path.getsize(file_pair[0])
            self.queue.put(file_pair)

        for x in range(self.pool_size):
            self.queue.put((None, None))

        print '========== distrubution done! =========='

        finish = 0
        while finish < self.pool_size:
            # print 'update!!!!!!! {}'.format(finish)
            self.percent = self.file_size.value / self.total_size * 100.0
            try:
                self.queue2.get(timeout=1)
                finish += 1
            except:
                pass

        [x.join() for x in workers]

        print '========== all done! =========='
        self.done = True
        print self.total_size, self.file_size.value, self.percent


if __name__ == '__main__':
    test = MULTI_COPY(4)
    from unipath import Path
    import threading as mt
    import time

    src = list(Path('/Users/guoxiaoao/Desktop/TEMP/Footage').walk())
    dst = [x.replace('/Users/guoxiaoao/Desktop/TEMP/Footage', '/Volumes/ORACLE/Temp/other/guoxiaoao/2') for x in src]

    sub_process = mt.Thread(target=test.run, args=(src, dst))
    sub_process.start()

    while not test.done:
        print test.percent
        time.sleep(1)

    sub_process.join()

    # test.run(src, dst)
