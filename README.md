# AsciiDoc Content Type Editor

**content-type-editor** is a web user interface that allows the user to add the `_mod-docs-content-type` attribute to a large number of AsciiDoc files that follow the guidelines for modules as defined in the [Modular Documentation Reference Guide](https://redhat-documentation.github.io/modular-docs/). If the content type can be reliably recognized from the file name or its contents, it provides it as a suggestion which the user can apply. If the content type is ambiguous, it displays analysis of the module content to help the user make the correct choice.

![A demo of the AsciiDoc Content Type Editor workflow](resources/content-type-editor-demo.gif "Example content-type-editor usage")

## Installation

Install the `content-type-editor` Python package:

```console
python3 -m pip install --upgrade content-type-editor
```

## Usage

Navigate to the directory with your AsciiDoc project and run the following command:

```console
content-type-editor
```

Alternatively, you supply the path to the project directory on the command line as follows:

```console
content-type-editor path/to/the/project
```

For a complete list of available command-line options, run `content-type-editor` with the `-h` option:

```console
content-type-editor -h
```

## Copyright

Copyright © 2025 Jaromir Hradilek

This program is free software, released under the terms of the MIT license. It is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
