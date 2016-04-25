import memcache
from consistent_hash.consistent_hash import ConsistentHash


class KetamaMemcacheClient(memcache.Client):
    """ A memcache subclass. This implementation allows you to add a new host at run
    time. It uses consistent hash library (libketama). All server are initilized with
    weight 1, that should uniformly distribute the keys, you can assign different weights
    that is more reflective of your memcached setup. It takes

    By default all servers have a weight of 1.
        { '192.168.0.101:11212': 1, '192.168.0.102:11212': 2, '192.168.0.103:11212': 1 }
        would generate a 25/50/25 distribution of the keys.


    @see https://github.com/yummybian/consistent-hash
    """

    def __init__(self, *args, **kwargs):
        super(KetamaMemcacheClient, self).__init__(*args, **kwargs)
        if self.servers:
            # ConsistentHash expects dictionary of servers and associated weights
            s = {str(server).split(":", 1)[1]: server.weight for server in self.servers}
            self.consistent_hash = ConsistentHash(s)

    def _get_server(self, key):
        """ Returns the most likely server to hold the key
        """
        server_ip_address = self.consistent_hash.get_node(key)
        # find the server object
        if server_ip_address:
            server = next((x for x in self.servers if server_ip_address in str(x)), None)
            if server and server.connect():
                return server, key
        return (None, None)

    def add_server(self, server):
        """ Adds a host at runtime to client
        """
        server_tmp = server
        # Create a new host entry
        server = memcache._Host(
            server, self.debug, dead_retry=self.dead_retry,
            socket_timeout=self.socket_timeout,
            flush_on_reconnect=self.flush_on_reconnect
        )
        # Add this to our server choices
        self.servers.append(server)
        self.buckets.append(server)
        # Adds this node to the circle
        self.consistent_hash.add_nodes([server_tmp])