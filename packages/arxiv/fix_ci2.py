import re

with open("requirements.txt", "r") as f:
    content = f.read()

content = re.sub(r"numpy==2\.5\.3", "numpy>=1.26.0", content)
content = re.sub(r"scipy==1\.18\.1", "scipy>=1.11.0", content)

with open("requirements.txt", "w") as f:
    f.write(content)
