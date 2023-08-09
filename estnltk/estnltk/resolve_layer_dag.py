#
#   This file is here only for backwards compatibility 
#   ( to enable importing of make_resolver and DEFAULT_RESOLVER 
#     as in previous versions of EstNLTK v1.6 )
#
import warnings

msg = (
    "resolve_layer_dag is deprecated and will be removed in future version. "
    "Use estnltk.default_resolver instead."
)
warnings.warn(msg, DeprecationWarning)

from estnltk_core.taggers_registry import TaggersRegistry
from estnltk_core.layer_resolver import LayerResolver
from estnltk.default_resolver import make_resolver
from estnltk.default_resolver import DEFAULT_RESOLVER