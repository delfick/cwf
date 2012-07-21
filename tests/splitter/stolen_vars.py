from src.splitter.imports import steal
import os

this_dir = os.path.dirname(__file__)
steal('numbers', 'letters'
    , folder=os.path.join(this_dir, 'vars'), globals=globals(), locals=locals()
    )

__ignored = 'ignored'
_hidden = '_hidden'
