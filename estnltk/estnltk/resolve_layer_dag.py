#
#   This file is here only for backwards compatibility 
#   ( to enable importing of make_resolver and DEFAULT_RESOLVER 
#     as in previous versions of EstNLTK v1.6 )
#
from estnltk_core.taggers_registry import TaggersRegistry
from estnltk_core.layer_resolver import LayerResolver
from estnltk.default_resolver import make_resolver
from estnltk.default_resolver import DEFAULT_RESOLVER