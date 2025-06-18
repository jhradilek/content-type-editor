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
from asciidoc import content_types, index_files, update_files

def st_data_editor(data, column_order=['file', 'type', 'contents'], disabled=['file', 'prefix', 'contents']):
    return st.data_editor(
        data, #.replace({'file': r'^.*/'}, {'file': ''}, regex=True),
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
            'prefix': st.column_config.Column(
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

#st.set_page_config(layout="wide")
st.title("Content type editor")

if 'df' not in st.session_state:
    with st.spinner("Processing AsciiDoc files...", show_time=True):
        df = index_files(sys.argv[1])
    if df.empty:
        st.error("No AsciiDoc files found.", icon="⚠️")
    else:
        st.session_state.df = df

if 'df' in st.session_state:
    df           = st.session_state['df']
    with_type    = df[df['type'].notna()].copy()
    temp         = df[df['type'].isna()].copy()
    temp['type'] = temp['prefix']
    with_prefix  = temp[temp['type'].notna()]
    other        = temp[temp['type'].isna()]
    new_prefix   = pd.DataFrame()
    new_other    = pd.DataFrame()

    with st.expander("Content type distribution", expanded=True):
        if not with_type.empty:
            st.bar_chart(with_type.groupby(['type']).size().reset_index(name='count'), x='type', y_label='', horizontal=True)

    with st.expander("Files with the content type defined", expanded=False):
        if not with_type.empty:
            st_data_editor(with_type, disabled=['file', 'path', 'type', 'prefix', 'contents'])

    with st.expander("Files with the content type derived from prefix", expanded=True):
        if not with_prefix.empty:
            new_prefix = st_data_editor(with_prefix)

    with st.expander("Files without the content type defined", expanded=True):
        if not other.empty:
            new_other  = st_data_editor(other)

    updated = pd.concat([new_prefix, new_other])
    if not updated.empty:
        updated = updated[updated['type'].notna()]

    if st.button("Update files", type='primary', disabled=updated.empty):
        with st.spinner("Updating AsciiDoc files...", show_time=True):
            count  = update_files(updated)
            expected = len(updated.index)

            if count == expected:
                st.success(f"Successfully updated {count} files.", icon="✅")
            else:
                st.error(f"Unable to update {expected - count}/{expected} AsciiDoc files.", icon="⚠️")
            st.session_state.clear()
