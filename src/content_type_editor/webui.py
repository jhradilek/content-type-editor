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

import sys
import pandas as pd
import streamlit as st
from pathlib import Path
from asciidoc import content_types, index_files, update_files
from content_type_editor import FULL_NAME as NAME

# Define a customized version of the st.data_editor widget:
def st_data_editor(data, column_order=['file', 'type', 'contents'], disabled=['file', 'suggestion', 'contents']):
    return st.data_editor(
        data,
        column_config= {
            'file': st.column_config.Column(
                'File name',
                width='medium'
            ),
            'type': st.column_config.SelectboxColumn(
                'Content type',
                options=content_types,
                width='small',
                required=False
            ),
            'suggestion': st.column_config.Column(
                'Prefix',
                width='small'
            ),
            'contents': st.column_config.Column(
                'Contents',
                width='small'
            )
        },
        column_order=column_order,
        disabled=disabled,
        hide_index=True
    )

# Get the name of the supplied directory; the option parser has already
# verified that it exists and is a directory:
directory = sys.argv[1]

# Determine the base name of the directory:
if directory == '.':
    dirname = Path(directory).resolve().name
else:
    dirname = Path(directory).name

# Configure the web UI:
st.set_page_config(
    page_title = NAME,
    menu_items={
        'Get help': "https://github.com/jhradilek/content-type-editor/",
        'Report a Bug': "https://github.com/jhradilek/content-type-editor/issues"
    }
)

# Display the web UI title:
st.title(NAME)

# Check if this the session has just started or the page was reloaded:
if 'df' not in st.session_state:
    # Display a progress spinner and build the DataFrame with information
    # about each AsciiDoc file:
    with st.spinner(f"Processing AsciiDoc files in {dirname}...", show_time=True):
        df = index_files(directory)
    if df.empty:
        st.error("No AsciiDoc files found.", icon="⚠️")
    else:
        st.session_state.df = df

# Check if the AsciiDoc files have already been indexed:
if 'df' in st.session_state:
    # Process the data and prepare relevant slices:
    df           = st.session_state['df']
    overview     = df.copy()
    overview['type'] = overview['type'].fillna('Undefined')
    with_type    = df[df['type'].notna()].copy()
    temp         = df[df['type'].isna()].copy()
    temp['type'] = temp['suggestion']
    with_suggest = temp[temp['type'].notna()]
    other        = temp[temp['type'].isna()]
    new_suggest  = pd.DataFrame()
    new_other    = pd.DataFrame()

    # Display a bar chart with an overview of known content types:
    with st.expander(f"Distribution of content types in {dirname}", expanded=True):
        if not overview.empty:
            suggestions = len(with_suggest.index)
            col1, col2 = st.columns([0.7, 0.3])
            col1.bar_chart(overview.groupby(['type']).size().reset_index(name='count'), x='type', y_label='', horizontal=True)
            col2.metric("AsciiDoc Files", len(df.index), f"{suggestions} suggestion{'s' if suggestions != 1 else ''}")

    # Display a table with the files that have content type already defined:
    with st.expander("Files with defined content type", expanded=False):
        if not with_type.empty:
            st_data_editor(with_type, disabled=['file', 'path', 'type', 'suggestion', 'contents'])

    # Display a table with the files that have content type identifiable
    # from their prefix or contents:
    with st.expander("Files with suggested content type", expanded=True):
        if not with_suggest.empty:
            new_suggest = st_data_editor(with_suggest)

    # Display a table with the files that need manual update:
    with st.expander("Files without identifiable content type", expanded=True):
        if not other.empty:
            new_other  = st_data_editor(other)

    # Get a list of files that have a new content type:
    updated = pd.concat([new_suggest, new_other])
    if not updated.empty:
        updated = updated[updated['type'].notna()]

    # Display the button to initiate mass update of the files. Make this
    # button inactive if there are no files with changed state:
    if st.button("Update files", type='primary', disabled=updated.empty):
        # Display the progress spinner:
        with st.spinner("Updating AsciiDoc files...", show_time=True):
            # Add the selected content type to the files and get a final
            # count of those that have been successfully updated:
            count  = update_files(updated)

            # Get the number of files that were expected to be updated:
            expected = len(updated.index)

            # Verify that both counts match and display an appropriate message:
            if count == expected:
                st.success(f"Successfully updated {count} file{'s' if count != 1 else ''}.", icon="✅")
            else:
                st.error(f"Failed to update {expected - count} out of {expected} file{'s' if expected != 1 else ''}.", icon="⚠️")
            st.session_state.clear()
