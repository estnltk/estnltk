class LambdaAttribute:
    __slots__ = ['_lambda_expression', '_lambda_function']

    def __init__(self, lambda_expression: str):
        assert isinstance(lambda_expression, str), type(lambda_expression)
        assert lambda_expression.startswith('lambda '), lambda_expression

        self._lambda_expression = lambda_expression
        self._lambda_function = eval(lambda_expression)

    def __eq__(self, other):
        if isinstance(other, LambdaAttribute):
            return self.lambda_expression == other.lambda_expression

    def __call__(self, annotation):
        return self._lambda_function(annotation)

    @property
    def lambda_expression(self):
        return self._lambda_expression

    def __repr__(self):
        return '{self.__class__.__name__}({self._lambda_expression!r})'.format(self=self)
