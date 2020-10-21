from rediscluster import RedisCluster


def get_redis_client(startup_nodes=None):
    if startup_nodes is None:
        startup_nodes.append({'host': '127.0.0.1', 'port': '6379'})
    return RedisCluster(
        startup_nodes=startup_nodes,
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3,
    )
