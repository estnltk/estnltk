import bisect

from estnltk import Span, Layer, AmbiguousSpan, Annotation


class LambdaAnnotation(Annotation):
    def __getattr__(self, item):
        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError

        attributes = self._attributes
        if item in attributes:
            value = attributes[item]
            if isinstance(value, str) and value.startswith('lambda a: '):
                return eval(value)(self)
            return value

        # item == '__deepcopy__'
        return self.__getattribute__('__class__').__getattribute__(self, item)


class LambdaSpan(Span):
    def add_annotation(self, **attributes) -> LambdaAnnotation:
        # TODO: try and remove if-s
        assert not self._annotations
        annotation = LambdaAnnotation(self)
        if self.layer:
            for attr in self.layer.attributes:
                if attr in attributes:
                    setattr(annotation, attr, attributes[attr])
        else:
            for attr, value in attributes.items():
                if attr == 'text':
                    continue
                setattr(annotation, attr, value)
        self._annotations.append(annotation)
        return annotation


class LambdaLayer(Layer):
    def add_annotation(self, base_span, **attributes):
        if self.parent is not None and self.ambiguous:
            span = self.classes.get(hash(base_span), None)
            if span is None:
                span = AmbiguousSpan(self, base_span)
                bisect.insort(self.span_list.spans, span)
                self.classes[hash(base_span)] = span
            assert isinstance(span, AmbiguousSpan), span
            attributes_pluss_default_values = self.default_values.copy()
            attributes_pluss_default_values.update(attributes)
            return span.add_annotation(**attributes_pluss_default_values)

        if self.parent is None and self.enveloping is None and self.ambiguous:
            span = self.classes.get(hash(base_span), None)
            if span is None:
                span = AmbiguousSpan(self, LambdaSpan(base_span.start, base_span.end, layer=self))
                bisect.insort(self.span_list.spans, span)
                self.classes[hash(span)] = span
            assert isinstance(span, AmbiguousSpan), span
            attributes_pluss_default_values = self.default_values.copy()
            attributes_pluss_default_values.update(attributes)
            return span.add_annotation(**attributes_pluss_default_values)

        if self.parent is None and self.enveloping is None and not self.ambiguous:
            if hash(base_span) in self.classes:
                raise ValueError('the layer is not ambiguous and already contains this span')

            attributes_pluss_default_values = self.default_values.copy()
            attributes_pluss_default_values.update(attributes)
            span = LambdaSpan(base_span.start, base_span.end, layer=self, **attributes_pluss_default_values)
            bisect.insort(self.span_list.spans, span)
            self.classes[hash(span)] = span
            return span.annotations[0]

        # TODO: implement add_annotation
        raise NotImplementedError('add_annotation not yet implemented for this type of layer')
