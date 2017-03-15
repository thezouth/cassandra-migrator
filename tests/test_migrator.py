import unittest

import time
import uuid

import docker
import migrator

CASSANDRA_IMAGE='cassandra:3.9'

class TestMigrator(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cli = docker.from_env()
        cls.cas1 = cli.containers.run(image=CASSANDRA_IMAGE, detach=True, ports={'9042/tcp': None})
        cls.cas2 = cli.containers.run(image=CASSANDRA_IMAGE, detach=True, ports={'9042/tcp': None})
        time.sleep(90)
        cls.cas1_port = cli.api.port(cls.cas1.id,'9042/tcp')[0]['HostPort']
        cls.cas2_port = cli.api.port(cls.cas2.id,'9042/tcp')[0]['HostPort']

    @classmethod
    def teardown_class(cls):
        cls.cas1.remove(force=True)
        cls.cas2.remove(force=True)

    def test_make_keyspace(self):
        keyspace = 'ks_' + uuid.uuid4().hex
        cas = migrator.Cassandra('localhost', int(self.cas1_port), keyspace, 'table_name')
        assert keyspace not in cas.cluster.metadata.keyspaces
        cas.make_keyspace()
        assert keyspace in cas.cluster.metadata.keyspaces

    def test_copy_data(self):
        src_keyspace = 'ks_' + uuid.uuid4().hex
        dst_keyspace = 'ks_' + uuid.uuid4().hex
        src_table = 'tb_' + uuid.uuid4().hex
        dst_table = 'tb_' + uuid.uuid4().hex
        src = migrator.Cassandra('localhost', int(self.cas1_port), src_keyspace, src_table)
        dst = migrator.Cassandra('localhost', int(self.cas2_port), dst_keyspace, dst_table)
        _prepare_data(src.session, src_keyspace, src_table)

        dst.make_keyspace()
        condition = "symbol='a'"
        migrator.copy_table_structure(src, dst)
        migrator.copy_table_data(src, dst, condition)

        src_rs = src.session.execute('select * from {}.{} where {}'.format(src_keyspace, src_table, condition))
        dst_rs = dst.session.execute('select * from {}.{}'.format(dst_keyspace, dst_table))
        assert list(src_rs) == list(dst_rs)


    def test_parse(self):
        host, port, keyspace, table = migrator.parse('localhost:9042/tests/users')
        assert 'localhost' == host
        assert 9042 == port
        assert 'tests' == keyspace
        assert 'users' == table


def _prepare_data(session, keyspace, table):
    session.execute("""
    CREATE KEYSPACE IF NOT EXISTS {}
    WITH replication = {{
        'class': 'SimpleStrategy',
        'replication_factor': '1'
    }}""".format(keyspace))

    session.execute('''
    CREATE TABLE {}.{} (
        symbol text, date date, time time, row_no int, mark int, price decimal, volume bigint,
        PRIMARY KEY (symbol, date, time, row_no))
    WITH CLUSTERING ORDER BY (date DESC, time DESC, row_no DESC)'''.format(keyspace, table))

    session.execute('''
    INSERT INTO {}.{} (symbol, date, time, row_no, mark, price, volume)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''.format(keyspace, table), ('a', '2017-03-14', '10:00:00', 123456, 1, 10.1, 1000))

    session.execute('''
    INSERT INTO {}.{} (symbol, date, time, row_no, mark, price, volume)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''.format(keyspace, table), ('b', '2017-03-14', '10:00:01', 123457, 1, 999999, 0))

    session.execute('''
    INSERT INTO {}.{} (symbol, date, time, row_no, mark, price, volume)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''.format(keyspace, table), ('a', '2017-03-14', '10:00:02', 123458, -1, 10.2, 2000))


