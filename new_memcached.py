""" 
HINT 1: Run this file first to see how the current implementation of memcache
deals with adding a host.

HINT 2: Browse the python-memcached source code to see how keys are distributed
across multiple servers.

You'll need to setup 8 running memcached instances on the following ports:
11211
11212
11213
11214
11215
11216
11217
11218

Minimum requirements:

apt-get install memcached
python-memcached==1.53
python2.7

You can use any existing python libraries to help you in this task.
"""

import random
import string
import memcache


class MemcacheClient(memcache.Client):
    """ A memcache subclass. It currently allows you to add a new host at run
    time. 

    Sadly, this truely messes with the our keys. I.E. Adding a host at runtime
    effectively wipes our cache all together...Wonder why?
    """
    
    def _get_server(self, key):
        """ Current implementation of Memcache client
        """
        return super(MemcacheClient, self)._get_server(key)

    def add_server(self, server):
        """ Adds a host at runtime to client
        """

        # Create a new host entry
        server = memcache._Host(
            server, self.debug, dead_retry=self.dead_retry,
            socket_timeout=self.socket_timeout,
            flush_on_reconnect=self.flush_on_reconnect
        )
        # Add this to our server choices
        self.servers.append(server)
        # Update our buckets
        self.buckets.append(server)


def random_key(size):
    """ Generates a random key
    """
    return ''.join(random.choice(string.letters) for _ in range(size))


if __name__ == '__main__':
    # We have 7 running memcached servers
    servers = ['127.0.0.1:1121%d' % i for i in range(1,8)]
    # We have 100 keys to split across our servers
    keys = [random_key(10) for i in range(100)]
    # Init our subclass
    client = MemcacheClient(servers=servers, debug=1)
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
