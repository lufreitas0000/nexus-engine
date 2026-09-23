with open('skills/adversarial_check.sh', 'r') as f:
    text = f.read()

text = text.replace('app_spatial_compiler/src app_spatial_compiler/tests', 'semantic_pdf_splitter/src semantic_pdf_splitter/tests')

with open('skills/adversarial_check.sh', 'w') as f:
    f.write(text)
