import os
import signal
from subprocess import check_output, CalledProcessError


def get_pids(name):
    pids = []
    try:
        pids = check_output(["pidof", name]).replace("\n","").split(" ")
    except CalledProcessError:
        return pids

def launch_memcached_instances(count):
    """
    Helper script to launch # of instance of memcached
    :return:
    """
    processes = get_pids("memcached")
    # kill processes
    for pid in processes:
        os.kill(int(pid), signal.SIGKILL)

    for i in range(1, count + 1):
        os.system('memcached -p 1121{} &'.format(i))

if __name__ == '__main__':
    launch_memcached_instances(8)