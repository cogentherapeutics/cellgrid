import pandas as pd
from pandas.util.testing import assert_index_equal, assert_series_equal
from cellgrid.ensemble.node import *
from cellgrid.ensemble import Schema


class TestNode:
    def setup_method(self):
        self.node = ModelNode('test', ['a', 'b'])

    def test_set_xtrain(self):
        self.node.x_train = 'x_train'
        assert self.node.x_train == 'x_train'

    def test_set_ytrain(self):
        self.node.y_train = 'y_train'
        assert self.node.y_train == 'y_train'


class TestNodeManager:
    def test_add(self):
        nm = NodeManager()
        nm.add('test', None, 'model_class', 'markers')
        node = nm.get_node('test')
        assert isinstance(node, ModelNode)
        assert node.name == 'test'

        nm.add('test2', 'test', 'model_class', 'markers')
        node2 = nm.get_node('test2')
        assert node2.name == 'test2'

    def test_walk(self):
        nm = NodeManager()
        nm.add('test', None, 'model_class', 'markers')
        nm.add('test2', 'test', 'model_class', 'markers')
        nm.add('test3', 'test', 'model_class', 'markers')
        nm.add('test4', 'test3', 'model_class', 'markers')

        r = [i.name for i in nm.walk()]
        assert r == ['test', 'test2', 'test3', 'test4']


class TestNodeTrainer:
    def test_create_new_blocks(self):
        y_train = pd.Series([1, 2, 1])
        parent = 'parent'
        blocks = NodesTrainer.create_new_block(y_train, parent)

        assert blocks[0]['name'] == 1
        assert blocks[0]['parent'] == parent
        assert_index_equal(blocks[0]['index'], pd.Index([0, 2]))

        assert blocks[1]['name'] == 2
        assert blocks[1]['parent'] == parent
        assert_index_equal(blocks[1]['index'], pd.Index([1]))

    def test_update_node_data(self):
        schema_data = [
            {
                'name': 'all-events',
                'parent': None,
                'model_class': 'xgb',
                'markers': ['a', 'b']
            },
            {
                'name': 'n1',
                'parent': 'all-events',
                'model_class': 'xgb',
                'markers': ['a', 'b']
            }
        ]
        schema = Schema(schema_data)
        nt = NodesTrainer(schema)
        nt.schema_to_nodes()

        x_train = pd.DataFrame([[1, 2], [3, 4], [5, 6], [7, 8]],
                               columns=list('ab'))
        y_train = pd.DataFrame([['n1', 'n11'], ['n2', ''], ['n2', ''], ['n1', 'n12']], columns=['x1', 'x2'])
        nt.update_node_data(x_train, y_train)

        nodes = list(nt.nm.walk())
        assert_series_equal(nodes[0].y_train,
                            pd.Series(['n1', 'n2', 'n2', 'n1'], name='x1'))
        assert_series_equal(nodes[1].y_train,
                            pd.Series(['n11', 'n12'], name='x2', index=[0, 3])
                            )