#!/usr/bin/env python
# -*- coding: utf-8 -*-

import markdown
import StringIO

template = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Java 8 - Lambda / Stream API</title>
<link rel="stylesheet" href="text.css">
</head>
<body>
%s
</body>
</html>
"""

buf = StringIO.StringIO()
try:
    markdown.markdownFromFile('text.md', buf)
    with open('text.html', 'w') as f:
        f.write(template % buf.getvalue())
finally:
    buf.close()
