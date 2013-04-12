from .base import KeyView

class StatsView(KeyView):
    def __init__(self, no_value='---', *args, **kwargs):
        self.no_value = no_value

        super(StatsView, self).__init__(*args, **kwargs)

    def get_value(self, *args, **kwargs)
        return super(Sum, self).get_value(*args, **kwargs).first()


class Sum(StatsView):
    def get_value(*args, **kwargs):
        stats = super(Sum, self).get_value(*args, **kwargs)

        try:
            return stats['sum']
        except Exception:
            # the view is using _sum in reduce.js, or there was nothing to
            # reduce in the range of startkey, endkey
            if stats:
                return stats
            else:
                return self.no_value


class Count(StatsView):
    def get_value(*args, **kwargs):
        stats = super(Count, self).get_value(*args, **kwargs)

        try:
            return stats['count']
        except Exception:
            # the view is using _count in reduce.js, or there was nothing to
            # reduce in the range of startkey, endkey
            if stats:
                return stats
            else:
                return self.no_value


class Min(StatsView):
    def get_value(*args, **kwargs):
        stats = super(Min, self).get_value(*args, **kwargs)
        
        if stats:
            return stats['min']
        else:
            return self.no_value


class Max(StatsView):
    def get_value(*args, **kwargs):
        stats = super(Max, self).get_value(*args, **kwargs)

        if stats:
            return stats['max']
        else:
            return self.no_value


class Mean(StatsView):
    def __init__(ndigits=0, *args, **kwargs):
        self.ndigits = ndigits

        super(Mean, self).__init__(*args, **kwargs)

    def get_value(*args, **kwargs):
        stats = super(Max, self).get_value(*args, **kwargs)
        
        if stats:
            n = round(float(stats['sum']) / stats['count'], self.ndigits)
            if self.ndigits == 0:
                n = int(n)
            return n
        else:
            return self.no_value


class SumSqr(StatsView):
    def get_value(*args, **kwargs):
        stats = super(Max, self).get_value(*args, **kwargs)
        
        if stats:
            return stats['sumsqr']
        else:
            return self.no_value


class UniqueCount(KeyView):
    def get_value(*args, **kwargs):
        # todo: do it in couch using group

        result = super(UniqueCount, self).get_value(*args, **kwargs)
        unique = set()
        for val in values:
            unique.add(val)
        return len(unique)
