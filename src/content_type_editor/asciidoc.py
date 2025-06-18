# Copyright (C) 2025 Jaromir Hradilek

# MIT License
#
# Permission  is hereby granted,  free of charge,  to any person  obtaining
# a copy of  this software  and associated documentation files  (the 'Soft-
# ware'),  to deal in the Software  without restriction,  including without
# limitation the rights to use,  copy, modify, merge,  publish, distribute,
# sublicense, and/or sell copies of the Software,  and to permit persons to
# whom the Software is furnished to do so,  subject to the following condi-
# tions:
#
# The above copyright notice  and this permission notice  shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS',  WITHOUT WARRANTY OF ANY KIND,  EXPRESS
# OR IMPLIED,  INCLUDING BUT NOT LIMITED TO  THE WARRANTIES OF MERCHANTABI-
# LITY,  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT
# SHALL THE AUTHORS OR COPYRIGHT HOLDERS  BE LIABLE FOR ANY CLAIM,  DAMAGES
# OR OTHER LIABILITY,  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM,  OUT OF OR IN CONNECTION WITH  THE SOFTWARE  OR  THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import os
import re
import pandas as pd

content_map = {
    'Image':       re.compile(r"^image::(?:\S|\S.*\S)\[.*\]\s*$"),
    'Procedure':   re.compile(r"^\.{1,2}Procedure\s*$"),
    'Section':     re.compile(r"^={2,}\s\S.*$"),
    'Table':       re.compile(r"^\|={3,}\s*$")
}

prefix_map = {
    'assembly': 'Assembly',
    'con': 'Concept',
    'proc': 'Procedure',
    'ref': 'Reference',
    'snip': 'Snippet'
}

content_types = prefix_map.values()

def parse_file(path, filename):
    in_comment_block = False

    content_type = None
    file_prefix  = None
    contents     = []

    r_comment_block  = re.compile(r"^/{4,}\s*$")
    r_comment_line   = re.compile(r"^(?://|//[^/].*)$")
    r_content_type   = re.compile(r"^:_(?:mod-docs-content|content|module)-type:\s+(ASSEMBLY|CONCEPT|PROCEDURE|REFERENCE|SNIPPET)")

    for prefix, value in prefix_map.items():
        if filename.startswith(prefix + '_') or filename.startswith(prefix + '-'):
            file_prefix = value
            break

    with open(path, 'r') as f:
        for line in f:
            if r_comment_block.search(line):
                delimiter = line.strip()
                if not in_comment_block:
                    in_comment_block = delimiter
                elif in_comment_block == delimiter:
                    in_comment_block = False
                continue

            if r_comment_line.search(line):
                continue

            if m := r_content_type.search(line):
                content_type = m.group(1).capitalize()
                continue

            for block, regex in content_map.items():
                if regex.search(line) and block not in contents:
                    contents.append(block)

    return {
        'file': filename,
        'path': path,
        'type': content_type,
        'prefix': file_prefix,
        'contents': ', '.join(sorted(contents))
    }

def index_files(path):
    result = []
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            if name.startswith('_') or name == 'master.adoc':
                continue
            if name.endswith('.adoc') or name.endswith('.asciidoc'):
                result.append(parse_file(os.path.join(root, name), name))
    return pd.DataFrame(result)

def update_files(df):
    count = 0

    r_line_ending    = re.compile(r"([\n\r]+)")

    for i, entry in df.iterrows():
        with open(entry['path'], 'r+') as f:
            line = f.readline()

            if m := r_line_ending.search(line):
                line_ending = m.group(1)
            else:
                line_ending = "\n"

            f.seek(0)
            text = f.read()
            f.seek(0)

            f.write(
                f":_mod-docs-content-type: {entry['type'].upper()}" +
                line_ending + line_ending +
                text
            )

            count += 1

    return count
