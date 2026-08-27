for filename in ['index.html', 'frontend/app.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    text = text.replace('<h2 class="footer-logo-text">LOOPSTACK</h2>', '<h2 class="footer-logo-text">HUMAN ART</h2>')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)
