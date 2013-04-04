import unittest
from couchdbkit_aggregate import IndicatorView, AggregateView, KeyView


class ViewTests(unittest.TestCase):

    def testIndicatorView_default_fn(self):
        view = IndicatorView(MockView(3), MockView(6))
        result = view.get_value("key")
        self.assertEqual(result, 50)

    def testIndicatorView_custom_fn(self):
        view = IndicatorView(MockView(3), MockView(6), lambda x, y: x * y)
        result = view.get_value("key")
        self.assertEqual(result, 18)

    def testAggregateView(self):

        class MyView(AggregateView):
            foo = KeyView('foo')
            bar = KeyView('bar')
            baz = IndicatorView(KeyView('a'), KeyView('b'))
            fake = MockView(5)

        self.assertIsInstance(MyView.key_views.get('foo', 'missing'), KeyView)
        self.assertIsInstance(MyView.key_views.get('bar', 'missing'), KeyView)
        self.assertIsInstance(MyView.key_views.get('baz', 'missing'), IndicatorView)

        self.assertNotIn('fake', MyView.key_views)


class MockView(object):
    def __init__(self, result):
        self.result = result

    def get_value(self, key, startkey=None, endkey=None, couch_view=None,
                  db=None, **kwargs):
        return self.result