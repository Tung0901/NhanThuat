with open('index.html', encoding='utf-8') as f: text = f.read()
import re
text = re.sub(r'<h2 class="footer-logo-text">.*?</h2>', '<h2 class="footer-logo-text">LOOPSTACK</h2>', text)
with open('index.html', 'w', encoding='utf-8') as f: f.write(text)

with open('frontend/app.html', encoding='utf-8') as f: text = f.read()
text = re.sub(r'<h2 class="footer-logo-text">.*?</h2>', '<h2 class="footer-logo-text">LOOPSTACK</h2>', text)
with open('frontend/app.html', 'w', encoding='utf-8') as f: f.write(text)
