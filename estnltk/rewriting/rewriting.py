class ReverseRewriter():
    #this is an example of the api
    #it reverses every value it is given

    def rewrite(self, record):
        #record is a dict (non-ambiguous layer)
        #            list - of - dicts (ambiguous layer)
        #            list - of - list - of dicts (enveloping layer)
        #   ... (and so on, as enveloping layers can be infinitely nested)
        # in practice, you should only implement "rewrite" for the case you are interested in

        #in this case, it is a simple dict


        result = {}
        for k, v in record.items():
            if k in ('start', 'end'):
                result[k] = v
            else:
                result[k] = v[::-1]

        return result

