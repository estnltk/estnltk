import regex as re
from abc import ABC, abstractmethod




class Rewriter(ABC):
    pass
    # def if_(self, _bool):
    #     if _bool:
    #         return self
    #     else:
    #         return DummyRewriter()

    @abstractmethod
    def rewrite(self, _str):
        raise NotImplementedError('Rewriter should implement rewrite method')

    def rewrite_until_stable(self, _str, limit=10, fail_silently=False):

        res = _str
        prev = res
        if limit is not None:
            breaking = True
        else:
            breaking = False

        c = 0
        while True:
            c += 1
            res = self.rewrite(prev)
            if res == prev:
                break
            prev = res

            if breaking:
                limit -= 1
                if limit <= 0:
                    if fail_silently:
                        break
                    else:
                        raise AssertionError('''Rewrite limit exceeded, ran {c} iterations.
To silence the error and get the result, change the "fail_silently" parameter to True.'''.format(c=c))
        return res


class RegexRewriter(Rewriter):
    def __init__(self, rules, **kwargs):
        self.kwargs = kwargs
        self.rules = rules

    def rewrite(self, _str):
        result = _str
        for (needle, target) in self.rules:
            result = re.sub(needle, target, result)
        return result


# class DummyRewriter(Rewriter):
#     def __init__(self, **kwargs):
#         pass
#
#     def rewrite(self, _str):
#         return _str


class Rewritable:
    __slots__ = []

    def rewrite_attribute(self, attr, rewrite_rules: Rewriter):
        assert isinstance(attr, str), 'attr should be a string, function got {_is}'.format(_is=str(type(attr)))
        assert attr in getattr(self, '__dict__').keys(), '{attr} is not an instance attribute of {self}'.format(attr=attr,
                                                                                                                self=self)
        assert isinstance(rewrite_rules, Rewriter), 'rewrite_rules must be of type Rewriter'

        res = rewrite_rules.rewrite(getattr(self, attr))
        setattr(self, attr, res)
        return res
