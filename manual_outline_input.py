#!/usr/bin/env python3
"""
Manual Outline Input Script
Paste your Document Outline items from the browser, then create the TOC
"""

import re
import json

def get_outline_from_user():
    """
    Get outline items from user input
    """
    print("="*70)
    print("Manual Document Outline Input")
    print("="*70)
    print()
    print("Please follow these steps:")
    print()
    print("1. Open file_c.html in your browser")
    print("2. Look at the 'Karty w dokumencie' (Document Outline) column on the left")
    print("3. Select ALL the text from that column (click and drag, or Ctrl+A)")
    print("4. Copy it (Ctrl+C)")
    print("5. Come back here and paste it")
    print()
    print("After pasting, press Enter, then type 'END' and press Enter again.")
    print()
    print("Paste your outline here (then type END on a new line):")
    print("-" * 70)
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'END':
                break
            lines.append(line)
        except EOFError:
            break
    
    print("-" * 70)
    print()
    
    # Process the lines to extract outline items
    outline_items = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Skip very short lines (likely artifacts)
        if len(line) < 3:
            continue
        
        # Skip lines that are clearly UI elements
        skip_keywords = [
            'karty w dokumencie',
            'document outline',
            'narzędzia',
            'tools',
            'edytuj',
            'edit',
            'zamknij',
            'close'
        ]
        
        if any(keyword in line.lower() for keyword in skip_keywords):
            continue
        
        # Clean up the line
        clean_line = re.sub(r'\s+', ' ', line).strip()
        
        # Add to outline if not already there
        if clean_line and clean_line not in outline_items:
            outline_items.append(clean_line)
    
    return outline_items

def save_outline_to_file(outline_items):
    """
    Save outline items to a JSON file
    """
    output_file = 'manual_outline.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(outline_items, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {len(outline_items)} outline items to {output_file}")
    return output_file

def inject_toc_with_outline(file_a_path, outline_items, output_path):
    """
    Inject TOC into file_a.html using the manual outline items
    """
    print(f"\nReading {file_a_path}...")
    
    try:
        with open(file_a_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"✗ ERROR: {file_a_path} not found")
        return False
    
    print(f"✓ Loaded {len(html_content)} characters")
    
    # CSS for TOC
    toc_css = """
    <style id="toc-injected-styles">
        #toc-sidebar-container {
            position: fixed;
            left: -280px;
            top: 0;
            width: 280px;
            height: 100vh;
            background-color: #f8f9fa;
            border-right: 1px solid #dadce0;
            overflow-y: auto;
            overflow-x: hidden;
            transition: left 0.3s ease;
            z-index: 10000;
            box-shadow: 2px 0 8px rgba(0,0,0,0.1);
            font-family: 'Roboto', Arial, sans-serif;
        }

        #toc-sidebar-container.toc-visible {
            left: 0;
        }

        body.toc-sidebar-open {
            padding-left: 280px;
            transition: padding-left 0.3s ease;
        }

        #toc-sidebar-header {
            padding: 16px 20px;
            border-bottom: 1px solid #dadce0;
            background-color: #fff;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        #toc-sidebar-title {
            font-size: 14px;
            font-weight: 500;
            color: #5f6368;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 0;
        }

        #toc-sidebar-items {
            padding: 8px 0;
        }

        .toc-sidebar-item {
            padding: 6px 20px;
            cursor: pointer;
            transition: background-color 0.2s;
            color: #3c4043;
            text-decoration: none;
            display: block;
            font-size: 13px;
            line-height: 1.4;
            border-left: 3px solid transparent;
        }

        .toc-sidebar-item:hover {
            background-color: #e8eaed;
        }

        .toc-sidebar-item.toc-active {
            background-color: #e8f0fe;
            border-left-color: #1a73e8;
            color: #1a73e8;
            font-weight: 500;
        }

        .toc-sidebar-item.toc-level-1 {
            padding-left: 20px;
            font-weight: 500;
            font-size: 14px;
        }

        .toc-sidebar-item.toc-level-2 {
            padding-left: 32px;
        }

        .toc-sidebar-item.toc-level-3 {
            padding-left: 44px;
            font-size: 12px;
        }

        .toc-sidebar-item.toc-level-4 {
            padding-left: 56px;
            font-size: 12px;
        }

        .toc-sidebar-item.toc-level-5 {
            padding-left: 68px;
            font-size: 11px;
        }

        .toc-sidebar-item.toc-level-6 {
            padding-left: 80px;
            font-size: 11px;
        }

        #toc-sidebar-toggle {
            position: fixed;
            left: 16px;
            top: 16px;
            width: 40px;
            height: 40px;
            background-color: #fff;
            border: 1px solid #dadce0;
            border-radius: 50%;
            cursor: pointer;
            z-index: 10001;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        #toc-sidebar-toggle:hover {
            background-color: #f8f9fa;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        body.toc-sidebar-open #toc-sidebar-toggle {
            left: 296px;
        }

        #toc-sidebar-toggle svg {
            width: 20px;
            height: 20px;
            fill: #5f6368;
        }

        #toc-sidebar-container::-webkit-scrollbar {
            width: 8px;
        }

        #toc-sidebar-container::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        #toc-sidebar-container::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }

        #toc-sidebar-container::-webkit-scrollbar-thumb:hover {
            background: #555;
        }

        h1, h2, h3, h4, h5, h6 {
            scroll-margin-top: 80px;
        }

        @media (max-width: 768px) {
            body.toc-sidebar-open { padding-left: 0; }
            #toc-sidebar-container { width: 240px; left: -240px; }
        }
    </style>
"""

    # TOC HTML
    toc_html = """
    <button id="toc-sidebar-toggle" aria-label="Toggle Table of Contents">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
        </svg>
    </button>

    <nav id="toc-sidebar-container">
        <div id="toc-sidebar-header">
            <h2 id="toc-sidebar-title">Document Outline</h2>
        </div>
        <div id="toc-sidebar-items"></div>
    </nav>
"""

    # JavaScript
    toc_js = """
    <script id="toc-injected-script">
        (function() {
            const outlineItems = """ + json.dumps(outline_items, ensure_ascii=False) + """;
            
            document.addEventListener('DOMContentLoaded', function() {
                console.log('TOC: Loaded', outlineItems.length, 'outline items');
                
                const tocToggle = document.getElementById('toc-sidebar-toggle');
                const tocContainer = document.getElementById('toc-sidebar-container');
                const tocItemsContainer = document.getElementById('toc-sidebar-items');
                const body = document.body;

                if (window.innerWidth > 768) {
                    tocContainer.classList.add('toc-visible');
                    body.classList.add('toc-sidebar-open');
                }

                if (tocToggle) {
                    tocToggle.addEventListener('click', function() {
                        tocContainer.classList.toggle('toc-visible');
                        body.classList.toggle('toc-sidebar-open');
                    });
                }

                const allHeadings = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p[style*="font-size"], span[style*="font-size"], div[style*="font-size"]');
                console.log('TOC: Found', allHeadings.length, 'potential headings');
                
                const headingMap = new Map();
                allHeadings.forEach((heading, index) => {
                    if (!heading.id) {
                        heading.id = 'toc-heading-' + index;
                    }
                    
                    const text = heading.textContent.trim().toLowerCase();
                    const normalized = text.replace(/\\s+/g, ' ').replace(/[^a-z0-9\\s]/gi, '');
                    
                    headingMap.set(normalized, heading);
                    headingMap.set(text, heading);
                });

                let tocItemsCreated = 0;
                
                outlineItems.forEach((outlineText) => {
                    const searchText = outlineText.trim().toLowerCase();
                    const normalizedSearch = searchText.replace(/\\s+/g, ' ').replace(/[^a-z0-9\\s]/gi, '');
                    
                    let matchedHeading = null;
                    let matchMethod = '';
                    
                    // Try exact match
                    if (headingMap.has(normalizedSearch)) {
                        matchedHeading = headingMap.get(normalizedSearch);
                        matchMethod = 'exact';
                    } else if (headingMap.has(searchText)) {
                        matchedHeading = headingMap.get(searchText);
                        matchMethod = 'exact-unnormalized';
                    } else {
                        // Fuzzy match
                        for (let [text, heading] of headingMap) {
                            if (text.includes(normalizedSearch) || normalizedSearch.includes(text)) {
                                matchedHeading = heading;
                                matchMethod = 'fuzzy';
                                break;
                            }
                        }
                        
                        // Even fuzzier - word by word
                        if (!matchedHeading) {
                            const searchWords = normalizedSearch.split(/\\s+/).filter(w => w.length > 3);
                            for (let [text, heading] of headingMap) {
                                const matches = searchWords.filter(word => text.includes(word));
                                if (matches.length >= Math.min(2, searchWords.length)) {
                                    matchedHeading = heading;
                                    matchMethod = 'word-match';
                                    break;
                                }
                            }
                        }
                    }
                    
                    if (matchedHeading) {
                        const tocItem = document.createElement('a');
                        tocItem.href = '#' + matchedHeading.id;
                        const level = matchedHeading.tagName.match(/^H([1-6])$/i);
                        const levelNum = level ? level[1] : '2';
                        tocItem.className = 'toc-sidebar-item toc-level-' + levelNum;
                        tocItem.textContent = outlineText;
                        
                        tocItem.addEventListener('click', function(e) {
                            e.preventDefault();
                            matchedHeading.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            
                            document.querySelectorAll('.toc-sidebar-item').forEach(item => {
                                item.classList.remove('toc-active');
                            });
                            tocItem.classList.add('toc-active');
                        });

                        tocItemsContainer.appendChild(tocItem);
                        tocItemsCreated++;
                        console.log('TOC: Matched "' + outlineText + '" via ' + matchMethod);
                    } else {
                        console.warn('TOC: No match for "' + outlineText + '"');
                    }
                });
                
                console.log('TOC: Created', tocItemsCreated, 'of', outlineItems.length, 'items');
                
                if (tocItemsCreated === 0) {
                    tocItemsContainer.innerHTML = '<div style="padding: 20px; color: #5f6368; font-size: 12px;">Could not match outline items to headings. Check browser console (F12) for details.</div>';
                }

                function updateActiveSection() {
                    const tocItems = document.querySelectorAll('.toc-sidebar-item');
                    const scrollPosition = window.scrollY + 100;
                    let currentActive = null;

                    allHeadings.forEach((heading) => {
                        if (heading.offsetTop <= scrollPosition) {
                            const headingText = heading.textContent.trim();
                            tocItems.forEach((item) => {
                                if (item.textContent.trim() === headingText) {
                                    currentActive = item;
                                }
                            });
                        }
                    });

                    tocItems.forEach((item) => item.classList.remove('toc-active'));
                    if (currentActive) currentActive.classList.add('toc-active');
                }

                let scrollTimeout;
                window.addEventListener('scroll', function() {
                    clearTimeout(scrollTimeout);
                    scrollTimeout = setTimeout(updateActiveSection, 50);
                });

                updateActiveSection();
            });
        })();
    </script>
"""

    # Inject into HTML
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', toc_css + '</head>', 1)
    else:
        html_content = '<head>' + toc_css + '</head>' + html_content
    
    body_match = re.search(r'<body[^>]*>', html_content, re.IGNORECASE)
    if body_match:
        insert_pos = body_match.end()
        html_content = html_content[:insert_pos] + toc_html + html_content[insert_pos:]
    else:
        html_content = toc_html + html_content
    
    if '</body>' in html_content:
        html_content = html_content.replace('</body>', toc_js + '</body>', 1)
    else:
        html_content = html_content + toc_js
    
    # Save
    print(f"\nSaving to {output_path}...")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ Saved!")
        return True
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("STEP 1: Get Outline Items")
    print("="*70)
    
    outline_items = get_outline_from_user()
    
    if not outline_items:
        print("\n✗ No outline items received.")
        print("Please run the script again and paste your outline.")
        return
    
    print(f"\n✓ Received {len(outline_items)} outline items:")
    print()
    for i, item in enumerate(outline_items, 1):
        preview = item if len(item) <= 60 else item[:60] + "..."
        print(f"  {i}. {preview}")
    
    # Save outline
    save_outline_to_file(outline_items)
    
    # Inject into file_a.html
    print("\n" + "="*70)
    print("STEP 2: Inject TOC into file_a.html")
    print("="*70)
    
    success = inject_toc_with_outline('file_a.html', outline_items, 'file_a_with_manual_toc.html')
    
    if success:
        print("\n" + "="*70)
        print("✓ SUCCESS!")
        print("="*70)
        print("\nCreated: file_a_with_manual_toc.html")
        print()
        print("Open this file in your browser and check:")
        print("  1. Does the Document Outline sidebar appear?")
        print("  2. Are your outline items listed?")
        print("  3. Do they link to the correct sections?")
        print()
        print("If items don't link correctly, press F12 in browser")
        print("and check the Console for matching details.")
        print()

if __name__ == "__main__":
    main()
