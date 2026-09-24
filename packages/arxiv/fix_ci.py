import re

with open("requirements.in", "r") as f:
    req_in = f.read()

# Adding networkx with a more lenient or more updated constraint might be necessary,
# but actually it's pinned to 3.7. networkx 3.7 requires python >= 3.12?
# The logs say:
# ERROR: Could not find a version that satisfies the requirement networkx==3.7
# ERROR: Ignored the following versions that require a different python version: 3.7 Requires-Python >=3.12,!=3.14.1;
#
# This means networkx 3.7 is python 3.12 only!
# So for our CI to work with Python 3.10 and 3.11, we shouldn't pin networkx to 3.7 in requirements.txt.
# Let's run pip-compile and let it resolve networkx on its own, or remove the strict pin in requirements.txt.

with open("requirements.txt", "r") as f:
    content = f.read()

content = re.sub(r"networkx==3\.7", "networkx>=3.0", content)

with open("requirements.txt", "w") as f:
    f.write(content)
