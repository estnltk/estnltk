from docutils.examples import internals
from lxml import etree
import os

def get_doc(text):
    return etree.fromstring(internals(text)[0].asdom().toxml())

def get_filename(path):
    return os.path.basename(path).split('.')[-2]


def get_toctree_from_index(text, maxdepth=2):
    tree = get_doc(text)
    template = '''
.. toctree::
   :maxdepth: {maxdepth}

   {docs}
    '''.format(
        docs = '\n   '.join([
                
                '{name} <{filename}>'.format(
                    
                    filename=get_filename(r.get('refuri')), 
                    name=r.get('name')
                
                
                ) for r in tree.xpath('//list_item/paragraph/reference')]
                           
                           ),
        maxdepth = maxdepth
        
        
    )
    return template

if __name__ == '__main__':
    import sys
    fromfile = sys.argv[1]
    title = sys.argv[2]
    print('=' * len(title))
    print(title)
    print('=' * len(title))
    print()

    print(get_toctree_from_index(open(fromfile).read(), maxdepth=1))