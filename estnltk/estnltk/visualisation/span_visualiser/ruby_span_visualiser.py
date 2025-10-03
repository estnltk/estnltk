from estnltk.visualisation.span_visualiser.plain_span_visualiser import PlainSpanVisualiser
import copy
import warnings


class RubySpanVisualiser(PlainSpanVisualiser):

    def __init__(self, text_id, fill_empty_spans=False, styles:'Dict[str, Union[str, Callable[[str, List[Annotation]], str]]]'=None, 
                                                        ruby_text:'Union[str, Callable[[str, List[Annotation]], str]]'=None, 
                                                        ruby_styles:'Dict[str, Union[str, Callable[[str, List[Annotation]], str]]]'=None):
        super().__init__(text_id, fill_empty_spans=fill_empty_spans, styles=styles)
        self.fill_empty_spans = fill_empty_spans
        self.ruby_rt = ruby_text
        self.ruby_rt_styles = ruby_styles

    def __call__(self, segment, spans):
        # Create span formatting
        span_formatting = super().__call__(segment, spans)

        if not self.fill_empty_spans and self.is_pure_text(segment):
            return segment[0]

        if self.span_styles is None:
            return segment[0]

        if self.ruby_rt is not None:
            output = ['<ruby>', span_formatting]
            # copy to make it readable for mappers
            mapping_segment = copy.deepcopy(segment)
            if len(segment[1]) == 1:
                mapping_segment[1] = spans[mapping_segment[1][0]].annotations
            #  Add ruby annotation after the the span
            ruby_rt_style = "font-size:75%"
            if self.ruby_rt_styles is not None:
                # Change ruby's CSS style [Optional]
                ruby_rt_styles = []
                for key, value in self.ruby_rt_styles.items():
                    if callable( value ):
                        ruby_rt_styles.append( key + ":" + value(mapping_segment) + ";" )
                    elif isinstance(value, str):
                        ruby_rt_styles.append( key + ":" + value + ";" )
                    else:
                        raise ValueError(f'(!) Unexpected value {value} in ruby_styles. Expected str or callable.')
                ruby_rt_style = ' '.join( ruby_rt_styles )
            #
            # *) If the browser supports ruby annotations (https://www.w3schools.com/tags/tag_ruby.asp), 
            #    then add ruby annotations ( self.ruby_rt ) on top of the main text (<rt> ... </rt>);
            # *) Otherwise, if the browser does not support ruby annotations, then add ruby annotations 
            #    ( self.ruby_rt ) as a super-script (<rp> ... </rp>).
            #
            output.append(f'<rp><sup style="{ruby_rt_style}"></rp>')
            output.append(f'<rt style="{ruby_rt_style}">')
            if callable( self.ruby_rt ):
                output.append( self.ruby_rt( mapping_segment ) )
            elif isinstance(value, str):
                output.append( self.ruby_rt )
            else:
                raise ValueError(f'(!) Unexpected value {value} for ruby. Expected str or callable.')
            output.append('</rt>')
            output.append('<rp></sup></rp>')
            # Finish ruby annotation
            output.append('</ruby>')
            return "".join(output)
        else:
            return span_formatting

