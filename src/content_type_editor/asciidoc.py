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

# Define the mapping of file prefixes to content types:
prefix_map = {
    'assembly': 'Assembly',
    'con': 'Concept',
    'proc': 'Procedure',
    'ref': 'Reference',
    'snip': 'Snippet'
}

# Define the list of supported content types:
content_types = prefix_map.values()

# Define regular expressions for various AsciiDoc markup:
r_add_resources       = re.compile(r"^(?:={2,}\s+|\.{1,2})Additional resources\s*$")
r_comment_block       = re.compile(r"^/{4,}\s*$")
r_comment_line        = re.compile(r"^(?://|//[^/].*)$")
r_content_type        = re.compile(r"^:_(?:mod-docs-content|content|module)-type:\s+(ASSEMBLY|CONCEPT|PROCEDURE|REFERENCE|SNIPPET)")
r_line_ending         = re.compile(r"(\r?\n|\r)")
content_map = {
    'Description list': re.compile(r"^\S.*?(?:;;|:{2,4})(?:\s*|\s+.*)$"),
    'Image':            re.compile(r"^image::(?:\S|\S.*\S)\[.*\]\s*$"),
    'Ordered list':     re.compile(r"^\s*\.+\s+\S.*$"),
    'Procedure':        re.compile(r"^\.{1,2}Procedure\s*$"),
    'Section':          re.compile(r"^={2,}\s\S.*$"),
    'Table':            re.compile(r"^\|={3,}\s*$"),
    'Unordered list':   re.compile(r"^\s*[*-]+\s+\S.*$")
}

# Read an AsciiDoc file and return a dictionary with information about it:
def parse_file(path, filename):
    # Set the default values for the dictionary:
    content_type = None
    suggestion   = None
    contents     = []

    # Set the variable to keep track of block comments:
    in_comment_block = False

    # Determine the content type from the prefix:
    for prefix, value in prefix_map.items():
        if filename.startswith(prefix + '_') or filename.startswith(prefix + '-'):
            suggestion = value
            break

    try:
        # Parse the AsciiDoc file:
        with open(path, 'r') as f:
            for line in f:
                # Ignore content in comment blocks:
                if r_comment_block.search(line):
                    delimiter = line.strip()
                    if not in_comment_block:
                        in_comment_block = delimiter
                    elif in_comment_block == delimiter:
                        in_comment_block = False
                    continue

                # Ignore content in single-line comments:
                if r_comment_line.search(line):
                    continue

                # Ignore content in additional resources:
                if r_add_resources.search(line):
                    break

                # Determine the content type from the attribute:
                if m := r_content_type.search(line):
                    content_type = m.group(1).capitalize()
                    continue

                # Record the presence of certain block elements:
                for block, regex in content_map.items():
                    if regex.search(line) and block not in contents:
                        contents.append(block)

                        # Determine the content type from the contents:
                        if block == 'Procedure' and not suggestion:
                            suggestion = block

    except:
        # Mark the file as unreadable:
        contents = ['File unreadable']

    # Return the result:
    return {
        'file': filename,
        'path': path,
        'type': content_type,
        'suggestion': suggestion,
        'contents': ', '.join(sorted(contents))
    }

# Find all AsciiDoc files in the selected directory and all of its
# subdirectories and return a DataFrame with records about each:
def index_files(path):
    # Create an empty list to collect the records in:
    result = []

    # Find all files recursively:
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            # Exclude files that are not expected to have a content type:
            if name.startswith('_') or name == 'master.adoc':
                continue

            # Process files with a supported extension:
            if name.endswith('.adoc') or name.endswith('.asciidoc'):
                result.append(parse_file(os.path.join(root, name), name))

    # Return the result:
    return pd.DataFrame(result)

# Add the content type attribute to the selected files:
def update_files(df):
    # Initiate the counter:
    count = 0

    # Process each record:
    for i, entry in df.iterrows():
        try:
            # Open the file for updating:
            with open(entry['path'], 'r+', newline='') as f:
                # Read the entire file:
                text = f.read()

                # Use this line to determine the line endings used:
                if m := r_line_ending.search(text):
                    line_ending = m.group(1)
                else:
                    line_ending = "\n"

                # Reset the position of the file handle to the beginning of the
                # file:
                f.seek(0)

                # Write the updated content to the file:
                f.write(
                    f":_mod-docs-content-type: {entry['type'].upper()}" +
                    line_ending + line_ending +
                    text
                )

                # Increment the counter
                count += 1
        except:
            # Do nothing here; the web UI uses the counter to report if
            # some of the files could not be updated:
            pass

    # Return the number of successfully updated files:
    return count
