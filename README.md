Cassandra migrator tools

Usage: `cmig <src_host>:<src_port>/<src_keyspace>/<src_table> <dst_host>:<dst_port>/<dst_keyspace>/<dst_table> <condition>`
Sample: `cmig 10.0.0.4:9042/ks1/users localhost:9042/test/users "group='admin'"`

