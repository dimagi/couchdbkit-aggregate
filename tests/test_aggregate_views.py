from couchdbkit.designer import pushdocs
from ..couchdbkit_aggregate import AggregateView, KeyView, views
from . import CouchdbkitTestCase


class SimpleView(AggregateView):

    foo = views.Sum("foo")
    bar = views.Count("bar")
    baz = views.Min("baz")
    bongo = views.Max("bongo")
    spam1 = views.Mean("spam", ndigits=0)
    spam2 = views.Mean("spam", ndigits=1)
    snork = views.SumSqr("snork")


class ComplexView(AggregateView):
    foo = views.Sum("foo")
    bar = foo


class EmptyResultsView(AggregateView):
    asdf1 = views.Sum("asdf", no_value="no value")
    asdf2 = views.Count("asdf")
    asdf3 = views.Min("asdf")
    asdf4 = views.Max("asdf")
    asdf5 = views.Mean("asdf")
    asdf6 = views.SumSrq("asdf")




class TestAggregateViews(CouchdbkitTestCase):

    def setUp(self):
        super(TestAggregateViews, self).setup()
        
        # insert data, upload designdocs



    def test_simple_aggregate_view(self):

        result = SimpleView.get_result(db=self.db)

        print result


