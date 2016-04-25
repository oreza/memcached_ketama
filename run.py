import random
import string
from memcached_ketama import KetamaMemcacheClient

if __name__ == '__main__':

    def random_key(size):
        """ Generates a random key
        """
        return ''.join(random.choice(string.letters) for _ in range(size))

    # We have 7 running memcached servers
    servers = ['127.0.0.1:1121%d' % i for i in range(1,8)]
    # We have 100 keys to split across our servers
    keys = [random_key(10) for i in range(100)]
    # Init our subclass
    client = KetamaMemcacheClient(servers=servers, debug=1)
    # Distribute the keys on our servers
    for key in keys:
        client.set(key, 1)

    # Check how many keys come back
    valid_keys = client.get_multi(keys)
    print '%s percent of keys matched' % ((len(valid_keys)/float(len(keys))) * 100)

    # We add another server...and pow!
    client.add_server('127.0.0.1:11218')
    print 'Added new server'

    valid_keys = client.get_multi(keys)
    print '%s percent of keys stil matched' % ((len(valid_keys)/float(len(keys))) * 100)