import re

FILES = [
    "static/login.html",
    "static/signup.html"
]

NEW_CSS = """
    :root {
      --bg: #f8f5ee;
      --surface: #f4efe4;
      --surface2: #ece6d8;
      --border: #d4cfc4;
      --primary: #1d6f5c;
      --primary-glow: rgba(29,111,92,0.15);
      --accent: #2e7d32;
      --success: #2e7d32;
      --warning: #d97706;
      --danger: #9e3b33;
      --text: #1a1917;
      --muted: #6b665d;
    }

    body { font-family: 'Inter', sans-serif; background: var(--bg) !important; color: var(--text) !important; min-height: 100vh; }

    /* Remove animated bg orbs */
    .bg-orb { display: none !important; }

    .logo-title {
      font-family: 'Newsreader', serif !important; font-style: italic !important;
      font-size: 32px !important;
      font-weight: 800 !important;
      color: var(--text) !important;
      background: none !important;
      -webkit-text-fill-color: var(--text) !important;
      letter-spacing: -0.5px !important;
    }
    
    .card, .form-card { 
        background: var(--surface) !important; 
        border: 1px solid var(--border) !important; 
        border-radius: 12px !important; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important; 
        color: var(--text) !important;
    }

    .form-input, .form-select {
        background: #fff !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }
    .form-input:focus, .form-select:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px var(--primary-glow) !important;
    }

    .btn-submit {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(29,111,92,0.2) !important;
    }
    .btn-submit:hover {
        background: #145243 !important;
        transform: translateY(-1px) !important;
    }
    
    .mode-btn { color: var(--muted) !important; }
    .mode-btn.active { background: var(--primary) !important; color: white !important; box-shadow: 0 4px 10px rgba(29,111,92,0.2) !important; }
    .mode-toggle { background: var(--surface) !important; border-color: var(--border) !important; }
    
    .platform-input-wrap, .skill-add-row input, .skill-add-row select, .skill-builder {
        background: #fff !important; border: 1px solid var(--border) !important; color: var(--text) !important;
    }
    
    .login-link a { color: var(--primary) !important; }
    
    /* Specific overrides for inputs */
    input, select { color: var(--text) !important; background: #fff !important; border: 1px solid var(--border) !important; }
    input::placeholder { color: var(--muted) !important; }
    
    .cv-dropzone { background: #fff !important; border-color: var(--border) !important; }
    .cv-dropzone.has-file { background: rgba(46,125,50,0.05) !important; border-color: var(--success) !important; }
    
    .section-title { color: var(--text) !important; border-bottom: 1px solid var(--border) !important; }
"""

def update_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # 1. Add Newsreader to fonts
    if "Newsreader" not in content:
        content = re.sub(r'href="https://fonts.googleapis.com/css2\?family=Inter', 
                         'href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,400&family=Inter', content)
                         
    # 2. Inject CSS right after <style>
    if "var(--bg): #f8f5ee" not in content:
        content = re.sub(r'<style>', f'<style>\n{NEW_CSS}\n', content)

    # 3. Clean up the old background definitions to avoid overriding
    content = re.sub(r'--bg: #070b14;', '/* removed */', content)
    content = re.sub(r'background: rgba\(13,18,32,0.9\);', '/* removed */', content)
    content = re.sub(r'background: rgba\(15, 20, 35, 0.85\);', '/* removed */', content)
    
    # 4. Nuke all inline blues/gradients
    content = re.sub(r'#6366f1', '#1d6f5c', content)
    content = re.sub(r'#22d3ee', '#2e7d32', content)
    content = re.sub(r'#8b5cf6', '#145243', content)
    content = re.sub(r'#5b5fe0', '#145243', content)
    
    # Replace inline background:rgba(99,102,241,...) which is blue RGB
    content = re.sub(r'rgba\(99,102,241,', 'rgba(29,111,92,', content)
    # Replace inline background:rgba(59,130,246,...) which is blue RGB
    content = re.sub(r'rgba\(59,130,246,', 'rgba(29,111,92,', content)
    content = re.sub(r'#2563eb', '#1d6f5c', content) # Another blue
    content = re.sub(r'#3b82f6', '#1d6f5c', content) # Another blue
    content = re.sub(r'#93c5fd', '#2e7d32', content) # light blue
    content = re.sub(r'#818cf8', '#2e7d32', content) # light blue

    with open(filepath, 'w') as f:
        f.write(content)

for f in FILES:
    update_file(f)
    print(f"Updated {f}")
