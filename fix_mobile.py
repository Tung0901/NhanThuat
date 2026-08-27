css_fix = '''
        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.2rem !important;
                margin-bottom: 1.5rem !important;
            }
            .footer-container {
                top: 55vh !important;
                transform: translateY(-40%) !important;
            }
            .footer-logo-text {
                font-size: 14vw !important;
            }
            .hero-content {
                padding-top: 4vh !important;
            }
            .glass-cursor-card {
                display: none !important;
            }
        }
'''

for filename in ['index.html', 'frontend/app.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    
    if 'hero-title { font-size: 2.2rem !important;' not in text:
        text = text.replace('</style>', css_fix + '\n    </style>', 1)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
