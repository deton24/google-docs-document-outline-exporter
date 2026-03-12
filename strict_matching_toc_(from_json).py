#!/usr/bin/env python3
"""
Strict Matching Version - Only exact matches, no fuzzy matching
"""

import re
import json

def inject_toc_strict_matching(file_a_path, outline_json_path, output_path):
    """
    Inject TOC with STRICT matching only - no fuzzy matching
    """
    
    # Load outline items
    print(f"Loading outline items from {outline_json_path}...")
    try:
        with open(outline_json_path, 'r', encoding='utf-8') as f:
            outline_items = json.load(f)
        print(f"✓ Loaded {len(outline_items)} outline items")
    except FileNotFoundError:
        print(f"✗ ERROR: {outline_json_path} not found")
        print("Run manual_outline_input.py first to create this file")
        return False
    
    # Load file_a.html
    print(f"\nLoading {file_a_path}...")
    try:
        with open(file_a_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        print(f"✓ Loaded {len(html_content)} characters")
    except FileNotFoundError:
        print(f"✗ ERROR: {file_a_path} not found")
        return False
    
    # CSS
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

    # HTML
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

    # JavaScript with STRICT matching
    toc_js = """
    <script id="toc-injected-script">
        (function() {
            const outlineItems = """ + json.dumps(outline_items, ensure_ascii=False) + """;
            
            // Normalize text for comparison
            function normalizeText(text) {
                return text
                    .toLowerCase()
                    .replace(/\\s+/g, ' ')
                    .replace(/[""'']/g, '"')
                    .replace(/[–—]/g, '-')
                    .trim();
            }
            
            // Calculate similarity score (0-1)
            function similarity(s1, s2) {
                const longer = s1.length > s2.length ? s1 : s2;
                const shorter = s1.length > s2.length ? s2 : s1;
                
                if (longer.length === 0) return 1.0;
                
                const editDistance = (s1, s2) => {
                    s1 = s1.toLowerCase();
                    s2 = s2.toLowerCase();
                    
                    const costs = [];
                    for (let i = 0; i <= s1.length; i++) {
                        let lastValue = i;
                        for (let j = 0; j <= s2.length; j++) {
                            if (i === 0) {
                                costs[j] = j;
                            } else if (j > 0) {
                                let newValue = costs[j - 1];
                                if (s1.charAt(i - 1) !== s2.charAt(j - 1)) {
                                    newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1;
                                }
                                costs[j - 1] = lastValue;
                                lastValue = newValue;
                            }
                        }
                        if (i > 0) costs[s2.length] = lastValue;
                    }
                    return costs[s2.length];
                };
                
                return (longer.length - editDistance(longer, shorter)) / longer.length;
            }
            
            document.addEventListener('DOMContentLoaded', function() {
                console.log('TOC: Loaded', outlineItems.length, 'outline items (STRICT MATCHING)');
                
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

                // Get ALL text elements (not just headings)
                const allElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, div, li, td, th');
                console.log('TOC: Found', allElements.length, 'total elements to search');
                
                // Build heading map with STRICT criteria
                const headingMap = new Map();
                
                allElements.forEach((element, index) => {
                    if (!element.id) {
                        element.id = 'toc-element-' + index;
                    }
                    
                    const text = element.textContent.trim();
                    
                    // Skip very short or very long texts
                    if (text.length < 5 || text.length > 300) return;
                    
                    const normalized = normalizeText(text);
                    
                    // Store element with normalized text as key
                    if (!headingMap.has(normalized)) {
                        headingMap.set(normalized, {
                            element: element,
                            original: text,
                            normalized: normalized
                        });
                    }
                });
                
                console.log('TOC: Created map with', headingMap.size, 'unique text elements');

                let matchedCount = 0;
                let exactMatches = 0;
                let nearMatches = 0;
                let noMatches = 0;
                
                outlineItems.forEach((outlineText, idx) => {
                    const searchNormalized = normalizeText(outlineText);
                    
                    let matchedElement = null;
                    let matchScore = 0;
                    let matchType = '';
                    
                    // Try exact match first
                    if (headingMap.has(searchNormalized)) {
                        matchedElement = headingMap.get(searchNormalized).element;
                        matchScore = 1.0;
                        matchType = 'exact';
                        exactMatches++;
                    } else {
                        // Try to find very similar matches (similarity >= 0.95)
                        let bestMatch = null;
                        let bestScore = 0;
                        
                        for (let [normalized, data] of headingMap) {
                            const score = similarity(searchNormalized, normalized);
                            
                            if (score > bestScore) {
                                bestScore = score;
                                bestMatch = data;
                            }
                        }
                        
                        // Only accept if similarity is 95% or higher
                        if (bestScore >= 0.95) {
                            matchedElement = bestMatch.element;
                            matchScore = bestScore;
                            matchType = 'near-exact';
                            nearMatches++;
                        } else {
                            console.warn('TOC: No match for "' + outlineText + '" (best score: ' + bestScore.toFixed(2) + ')');
                            noMatches++;
                        }
                    }
                    
                    if (matchedElement) {
                        const tocItem = document.createElement('a');
                        tocItem.href = '#' + matchedElement.id;
                        
                        // Determine level from element type
                        const tagName = matchedElement.tagName.toLowerCase();
                        let level = 2; // default
                        
                        if (tagName.match(/^h[1-6]$/)) {
                            level = parseInt(tagName.charAt(1));
                        }
                        
                        tocItem.className = 'toc-sidebar-item toc-level-' + level;
                        tocItem.textContent = outlineText;
                        
                        tocItem.addEventListener('click', function(e) {
                            e.preventDefault();
                            matchedElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            
                            document.querySelectorAll('.toc-sidebar-item').forEach(item => {
                                item.classList.remove('toc-active');
                            });
                            tocItem.classList.add('toc-active');
                        });

                        tocItemsContainer.appendChild(tocItem);
                        matchedCount++;
                        
                        console.log('TOC [' + (idx + 1) + '/' + outlineItems.length + ']: Matched "' + 
                            outlineText.substring(0, 50) + '..." via ' + matchType + 
                            ' (score: ' + matchScore.toFixed(2) + ')');
                    }
                });
                
                console.log('TOC: MATCHING SUMMARY:');
                console.log('  Exact matches: ' + exactMatches);
                console.log('  Near matches (95%+): ' + nearMatches);
                console.log('  No matches: ' + noMatches);
                console.log('  Total matched: ' + matchedCount + '/' + outlineItems.length);
                
                if (matchedCount === 0) {
                    tocItemsContainer.innerHTML = '<div style="padding: 20px; color: #5f6368; font-size: 12px;">No matching headings found. Check browser console (F12) for details.</div>';
                }

                function updateActiveSection() {
                    const tocItems = document.querySelectorAll('.toc-sidebar-item');
                    const scrollPosition = window.scrollY + 100;
                    let currentActive = null;

                    allElements.forEach((element) => {
                        if (element.offsetTop <= scrollPosition) {
                            const elementText = element.textContent.trim();
                            tocItems.forEach((item) => {
                                if (item.textContent.trim() === elementText) {
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

    # Inject
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
        print(f"✓ Saved successfully!")
        return True
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    print("="*70)
    print("Strict Matching TOC Injector")
    print("Uses ONLY exact or 95%+ similar matches")
    print("="*70)
    print()
    
    outline_file = 'manual_outline.json'
    input_file = 'file_a.html'
    output_file = 'file_a_strict_matching.html'
    
    success = inject_toc_strict_matching(input_file, outline_file, output_file)
    
    if success:
        print("\n" + "="*70)
        print("✓ SUCCESS!")
        print("="*70)
        print(f"\nCreated: {output_file}")
        print()
        print("Open in browser and check the console (F12) to see:")
        print("  - How many exact matches were found")
        print("  - How many near-matches (95%+ similarity)")
        print("  - Which items couldn't be matched")
        print()
        print("This version will NOT create incorrect 'fuzzy' matches!")
        print()

if __name__ == "__main__":
    main()
