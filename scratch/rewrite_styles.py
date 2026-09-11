import re

FILES = [
    "static/login.html",
    "static/signup.html"
]

NEW_CSS = """
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

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

    body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }

    /* Remove animated bg orbs */
    .bg-orb { display: none; }

    .logo-title {
      font-family: 'Newsreader', serif; font-style: italic;
      font-size: 32px;
      font-weight: 800;
      color: var(--text);
      background: none;
      -webkit-text-fill-color: var(--text);
      letter-spacing: -0.5px;
    }
    
    .card, .form-card { 
        background: var(--surface); 
        border: 1px solid var(--border); 
        border-radius: 12px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); 
        color: var(--text);
    }

    .form-input, .form-select {
        background: #fff;
        border: 1px solid var(--border);
        color: var(--text);
        padding: 12px 14px;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        outline: none;
        transition: all 0.2s;
    }
    .form-input:focus, .form-select:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px var(--primary-glow);
    }

    .btn-submit {
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(29,111,92,0.2);
        width: 100%; padding: 16px;
        font-size: 15px; font-weight: 700;
        cursor: pointer; transition: all 0.2s;
        display: flex; align-items: center; justify-content: center; gap: 10px;
    }
    .btn-submit:hover {
        background: #145243;
        transform: translateY(-1px);
    }
    
    .mode-btn { color: var(--muted); }
    .mode-btn.active { background: var(--primary); color: white; box-shadow: 0 4px 10px rgba(29,111,92,0.2); }
    .mode-toggle { background: var(--surface); border-color: var(--border); }
    
    .platform-input-wrap, .skill-add-row input, .skill-add-row select, .skill-builder {
        background: #fff; border: 1px solid var(--border); color: var(--text);
    }
    
    .login-link a { color: var(--primary); }
    
    input, select { color: var(--text); background: #fff; border: 1px solid var(--border); }
    input::placeholder { color: var(--muted); }
    
    .cv-dropzone { background: #fff; border-color: var(--border); }
    .cv-dropzone.has-file { background: rgba(46,125,50,0.05); border-color: var(--success); }
    
    .section-title { color: var(--text); border-bottom: 1px solid var(--border); }

    /* Other required components ported from old CSS */
    .page-wrap { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding: 40px 20px; position: relative; z-index: 1; }
    .header { text-align: center; margin-bottom: 32px; }
    .logo-icon { font-size: 40px; display: block; margin-bottom: 12px; }
    .logo-sub { font-size: 13px; color: var(--muted); margin-top: 4px; }
    .mode-toggle { display: flex; border-radius: 16px; padding: 6px; gap: 6px; margin-bottom: 28px; width: 100%; max-width: 480px; }
    .mode-btn { flex: 1; padding: 12px; border: none; font-size: 13px; font-weight: 600; border-radius: 12px; cursor: pointer; transition: all 0.2s; }
    .form-card { padding: 36px; width: 100%; max-width: 700px; margin-bottom: 24px; }
    .section-title { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; padding-bottom: 8px; }
    .form-grid { display: grid; gap: 16px; margin-bottom: 24px; }
    .form-grid.cols-2 { grid-template-columns: 1fr 1fr; }
    .form-grid.cols-3 { grid-template-columns: 1fr 1fr 1fr; }
    .form-group { display: flex; flex-direction: column; gap: 6px; }
    .form-label { font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.7px; }
    .form-hint { font-size: 11px; color: var(--muted); opacity: 0.7; }
    .skill-builder { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; min-height: 44px; padding: 8px; border-radius: 10px; }
    .skill-chip { display: flex; align-items: center; gap: 6px; padding: 4px 10px 4px 12px; background: var(--surface2); border: 1px solid var(--border); border-radius: 20px; font-size: 12px; font-weight: 600; color: var(--text); }
    .skill-chip button { background: none; border: none; color: var(--muted); cursor: pointer; font-size: 14px; line-height: 1; padding: 0; }
    .skill-chip button:hover { color: var(--danger); }
    .skill-add-row { display: flex; gap: 8px; margin-top: 8px; }
    .skill-add-row input { flex: 1; padding: 8px 12px; border-radius: 8px; font-size: 13px; outline: none; }
    .skill-add-row select { padding: 8px 12px; border-radius: 8px; font-size: 13px; outline: none; cursor: pointer; }
    .skill-add-row button { padding: 8px 16px; background: var(--primary); border: none; border-radius: 8px; color: white; font-size: 13px; font-weight: 600; cursor: pointer; }
    .cv-dropzone { border: 2px dashed var(--border); border-radius: 16px; padding: 48px 32px; text-align: center; cursor: pointer; transition: all 0.2s; }
    .cv-dropzone:hover, .cv-dropzone.drag-over { border-color: var(--primary); }
    .cv-icon { font-size: 48px; margin-bottom: 12px; display: block; }
    .cv-title { font-size: 16px; font-weight: 600; margin-bottom: 6px; }
    .cv-sub { font-size: 13px; color: var(--muted); }
    .cv-file-name { font-size: 13px; color: var(--success); font-weight: 600; margin-top: 8px; }
    .platform-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .platform-input-wrap { display: flex; align-items: center; gap: 10px; border-radius: 10px; padding: 10px 14px; }
    .platform-icon { font-size: 20px; flex-shrink: 0; width: 24px; text-align: center; }
    .platform-input-wrap input { background: none; border: none; font-size: 13px; outline: none; flex: 1; }
    .error-box { background: rgba(158,59,51,0.1); border: 1px solid rgba(158,59,51,0.3); border-radius: 10px; padding: 12px 16px; font-size: 13px; color: var(--danger); margin-bottom: 16px; display: none; }
    .success-box { background: rgba(46,125,50,0.1); border: 1px solid rgba(46,125,50,0.3); border-radius: 12px; padding: 20px; font-size: 14px; color: var(--success); margin-bottom: 16px; display: none; text-align: center; }
    .success-box .success-usn { font-size: 28px; font-weight: 800; font-family: monospace; color: var(--primary); margin: 8px 0; }
    .login-link { text-align: center; font-size: 13px; color: var(--muted); }
    .login-link a { text-decoration: none; font-weight: 600; }
    .spinner { width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.7s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .steps { display: flex; gap: 6px; margin-bottom: 28px; }
    .step { flex: 1; height: 4px; border-radius: 2px; background: rgba(0,0,0,0.1); transition: background 0.3s; }
    .step.done { background: var(--success); }
    .step.active { background: var(--primary); }
    .ai-preview { background: var(--surface2); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-top: 16px; display: none; }
    .ai-preview h4 { font-size: 12px; font-weight: 700; color: var(--primary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; }
    .ai-stat { display: flex; justify-content: space-between; font-size: 13px; padding: 6px 0; border-bottom: 1px solid var(--border); }
    .ai-stat:last-child { border: none; }
    .ai-stat strong { color: var(--primary); }
    
    .login-container { position: relative; z-index: 10; width: 100%; max-width: 460px; padding: 20px; }
    .logo-section { text-align: center; margin-bottom: 36px; }
    .logo-subtitle { font-size: 13px; color: var(--muted); letter-spacing: 0.5px; }

    @media (max-width: 600px) {
      .form-grid.cols-2, .form-grid.cols-3, .platform-grid { grid-template-columns: 1fr; }
    }
"""

def update_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Add Newsreader to fonts
    if "Newsreader" not in content:
        content = re.sub(r'href="https://fonts.googleapis.com/css2\?family=Inter', 
                         'href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,400&family=Inter', content)
                         
    # Replace the whole <style>...</style> block
    style_start = content.find("<style>")
    style_end = content.find("</style>") + len("</style>")
    
    if style_start != -1 and style_end != -1:
        content = content[:style_start] + f"<style>\n{NEW_CSS}\n</style>" + content[style_end:]

    # Remove inline background styling and gradients in the body HTML
    content = re.sub(r'style="background:linear-gradient\([^"]*\)"', 'style="background:var(--primary)"', content)
    content = re.sub(r'background: linear-gradient\([^;]*\);?', 'background: var(--primary);', content)
    content = re.sub(r'background:linear-gradient\([^;]*\);?', 'background: var(--primary);', content)
    
    content = re.sub(r'color:#6366f1;?', 'color:var(--primary);', content)
    content = re.sub(r'color:#818cf8;?', 'color:var(--primary);', content)
    content = re.sub(r'color:#10b981;?', 'color:var(--success);', content)
    content = re.sub(r'color:#ef4444;?', 'color:var(--danger);', content)
    content = re.sub(r'color:#fca5a5;?', 'color:var(--danger);', content)
    content = re.sub(r'color:#6ee7b7;?', 'color:var(--success);', content)
    content = re.sub(r'color:#cbd5e1;?', 'color:var(--text);', content)
    content = re.sub(r'color:#fff;?', 'color:#fff;', content)
    
    content = re.sub(r'background:rgba\(99,102,241,[^)]*\)', 'background:var(--surface2)', content)
    content = re.sub(r'background:rgba\(59,130,246,[^)]*\)', 'background:var(--surface2)', content)
    content = re.sub(r'background:rgba\(16,185,129,[^)]*\)', 'background:var(--surface2)', content)
    content = re.sub(r'background:rgba\(255,255,255,[^)]*\)', 'background:var(--surface2)', content)
    
    content = re.sub(r'border:1px solid rgba\([0-9,.]+\)', 'border:1px solid var(--border)', content)
    
    content = re.sub(r'#2563eb', 'var(--primary)', content)
    content = re.sub(r'rgba\(245,158,11,0.18\)', 'var(--surface2)', content)
    content = re.sub(r'#fbbf24', 'var(--warning)', content)

    with open(filepath, 'w') as f:
        f.write(content)

for f in FILES:
    update_file(f)
    print(f"Updated {f}")
