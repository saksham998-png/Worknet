import os
import re

backend_dir = r'c:\ethara_website_project\backend'

def fix_imports(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace from models import ...
                content = re.sub(r'from models import', 'from backend.models import', content)
                # Replace from utils. import ...
                content = re.sub(r'from utils\.', 'from backend.utils.', content)
                # Replace from routes. import ...
                content = re.sub(r'from routes\.', 'from backend.routes.', content)
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

fix_imports(backend_dir)
print("Import fix complete.")
