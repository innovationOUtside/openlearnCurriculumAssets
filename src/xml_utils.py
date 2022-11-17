import unicodedata
from lxml import etree
import pandas as pd
import hashlib
import re

def context_path(xpath):
    """Simplify an xpath to give a cleaner context path."""
    # The xpath can be retrieved from an element by:
    # tree = etree.ElementTree(root)
    # tree.getpath(el)
    xpath = re.sub(r'\[\d+\]', '', xpath)
    xpath = re.sub(r'(/Item|/Unit|/Session|/Section|/SubSection|/InternalSection)', '', xpath)
    return xpath

def create_id(records, id_field="id", fields=["code", "name"]):
    """Create a key from the specified fields."""
    fields = [fields] if isinstance(fields, str) else fields
    if isinstance(records, list):
        for record in records:
            key = "-".join([record[k] for k in fields ])
            # We could check there is no collision on the id key
            record[id_field] = hashlib.sha1(key.encode(encoding='UTF-8')).hexdigest()
    elif isinstance(records, dict):
        key = "-".join([record[k] for k in fields ])
        # We could check there is no collision on the id key
        record[id_field] = hashlib.sha1(key.encode(encoding='UTF-8')).hexdigest()
    elif isinstance(records, tuple):
        key = "-".join([k for k in records])
        # We could check there is no collision on the id key
        return hashlib.sha1(key.encode(encoding='UTF-8')).hexdigest()
      
    # The records list or dict is mutable and is updated directly
    # Consequently, we do not need a return value

def unpack(x):
    return etree.tostring(x)

# via http://stackoverflow.com/questions/5757201/help-or-advice-me-get-started-with-lxml/5899005#5899005
def flatten(el):
    """Utility function for flattening XML tags."""
    def _flatten(el):
        if el is None:
            return ""  # Originally returned None; any side effects of move to ''?
        result = [(el.text or "")]
        for sel in el:
            result.append(_flatten(sel))
            result.append(sel.tail or "")
        return unicodedata.normalize("NFKD", "".join(result)) or " "
    return _flatten(el).strip()

def fts(db, base_tbl, q):
    """Run a simple full-text search query 
       over a table with an FTS virtual table."""
    _q = f"""SELECT * FROM {base_tbl}_fts 
             WHERE {base_tbl}_fts MATCH {db.quote(q)} ;"""
    return pd.read_sql(_q, con=db.conn)