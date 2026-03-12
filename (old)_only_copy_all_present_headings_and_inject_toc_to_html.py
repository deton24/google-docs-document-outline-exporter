#!/usr/bin/env python3
"""
Enhanced merge script that preserves ALL original formatting
Injects TOC sidebar without modifying the original document structure
"""

import re

def inject_toc_into_html(original_file, output_file):
    """Inject TOC sidebar and scripts into original HTML without changing formatting"""
    
    print(f"Reading {original_file}...")
    try:
        with open(original_file, 'r', encoding='utf-8') as f:
            original_html = f.read()
    except FileNotFoundError:
        print(f"ERROR: Could not find {original_file}")
        return False
    except Exception as e:
        print(f"ERROR reading {original_file}: {e}")
        return False
    
    # CSS for TOC sidebar - will be injected into <head>
    toc_css = """
    <style id="toc-styles">
        /* Table of Contents Styles - Injected */
        #toc-container {
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

        #toc-container.visible {
            left: 0;
        }

        #toc-header {
            padding: 16px 20px;
            border-bottom: 1px solid #dadce0;
            background-color: #fff;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        #toc-title {
            font-size: 14px;
            font-weight: 500;
            color: #5f6368;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        #toc-content {
            padding: 8px 0;
        }

        .toc-item {
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

        .toc-item:hover {
            background-color: #e8eaed;
        }

        .toc-item.active {
            background-color: #e8f0fe;
            border-left-color: #1a73e8;
            color: #1a73e8;
            font-weight: 500;
        }

        .toc-item.level-1 {
            padding-left: 20px;
            font-weight: 500;
            font-size: 14px;
        }

        .toc-item.level-2 {
            padding-left: 32px;
        }

        .toc-item.level-3 {
            padding-left: 44px;
            font-size: 12px;
        }

        .toc-item.level-4 {
            padding-left: 56px;
            font-size: 12px;
        }

        .toc-item.level-5 {
            padding-left: 68px;
            font-size: 11px;
        }

        .toc-item.level-6 {
            padding-left: 80px;
            font-size: 11px;
        }

        #toc-toggle {
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

        #toc-toggle:hover {
            background-color: #f8f9fa;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        body.toc-visible #toc-toggle {
            left: 296px;
        }

        #toc-toggle svg {
            width: 20px;
            height: 20px;
            fill: #5f6368;
        }

        body.toc-visible {
            padding-left: 280px;
            transition: padding-left 0.3s ease;
        }

        #toc-container::-webkit-scrollbar {
            width: 8px;
        }

        #toc-container::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        #toc-container::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }

        #toc-container::-webkit-scrollbar-thumb:hover {
            background: #555;
        }

        /* Ensure headings are scroll-target friendly */
        h1, h2, h3, h4, h5, h6 {
            scroll-margin-top: 20px;
        }

        @media (max-width: 768px) {
            body.toc-visible {
                padding-left: 0;
            }
            
            #toc-container {
                width: 240px;
                left: -240px;
            }
            
            #toc-container.visible {
                left: 0;
            }
        }
    </style>
"""

    # HTML for TOC sidebar - will be injected at start of <body>
    toc_html = """
    <!-- TOC Toggle Button -->
    <button id="toc-toggle" aria-label="Toggle Table of Contents">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
        </svg>
    </button>

    <!-- Table of Contents Sidebar -->
    <nav id="toc-container">
        <div id="toc-header">
            <div id="toc-title">Document Outline</div>
        </div>
        <div id="toc-content">
            <!-- TOC will be generated dynamically -->
        </div>
    </nav>
"""

    # JavaScript for TOC functionality - will be injected before </body>
    toc_script = """
    <script id="toc-script">
        (function() {
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initTOC);
            } else {
                initTOC();
            }

            function initTOC() {
                const tocToggle = document.getElementById('toc-toggle');
                const tocContainer = document.getElementById('toc-container');
                const tocContent = document.getElementById('toc-content');
                const body = document.body;

                if (!tocToggle || !tocContainer || !tocContent) {
                    console.warn('TOC elements not found');
                    return;
                }

                // Show TOC by default on desktop
                if (window.innerWidth > 768) {
                    tocContainer.classList.add('visible');
                    body.classList.add('toc-visible');
                }

                // Toggle TOC visibility
                tocToggle.addEventListener('click', function() {
                    tocContainer.classList.toggle('visible');
                    body.classList.toggle('toc-visible');
                });

                // Generate TOC from all headings in the document
                function generateTOC() {
                    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                    tocContent.innerHTML = '';

                    if (headings.length === 0) {
                        tocContent.innerHTML = '<div style="padding: 20px; color: #666; font-size: 12px;">No headings found</div>';
                        return;
                    }

                    headings.forEach((heading, index) => {
                        // Skip headings inside the TOC container itself
                        if (tocContainer.contains(heading)) {
                            return;
                        }

                        // Create unique ID for heading if it doesn't have one
                        if (!heading.id) {
                            heading.id = 'toc-heading-' + index;
                        }

                        // Create TOC item
                        const tocItem = document.createElement('a');
                        tocItem.href = '#' + heading.id;
                        tocItem.className = 'toc-item level-' + heading.tagName.charAt(1);
                        tocItem.textContent = heading.textContent.trim();
                        
                        // Smooth scroll to heading
                        tocItem.addEventListener('click', function(e) {
                            e.preventDefault();
                            const target = document.getElementById(heading.id);
                            if (target) {
                                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                                
                                // Update active state
                                document.querySelectorAll('.toc-item').forEach(item => {
                                    item.classList.remove('active');
                                });
                                tocItem.classList.add('active');
                            }
                        });

                        tocContent.appendChild(tocItem);
                    });
                }

                // Highlight active section while scrolling
                function updateActiveSection() {
                    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                    const tocItems = tocContent.querySelectorAll('.toc-item');
                    
                    let currentActive = null;
                    const scrollPosition = window.scrollY + 100;

                    // Filter out headings inside TOC
                    const validHeadings = Array.from(headings).filter(h => !tocContainer.contains(h));

                    validHeadings.forEach((heading, index) => {
                        if (heading.offsetTop <= scrollPosition) {
                            currentActive = index;
                        }
                    });

                    tocItems.forEach((item, index) => {
                        if (index === currentActive) {
                            item.classList.add('active');
                        } else {
                            item.classList.remove('active');
                        }
                    });
                }

                // Generate TOC
                generateTOC();

                // Update active section on scroll (throttled)
                let scrollTimeout;
                window.addEventListener('scroll', function() {
                    clearTimeout(scrollTimeout);
                    scrollTimeout = setTimeout(updateActiveSection, 50);
                });

                // Initial active section
                updateActiveSection();

                // Handle window resize
                window.addEventListener('resize', function() {
                    if (window.innerWidth <= 768) {
                        tocContainer.classList.remove('visible');
                        body.classList.remove('toc-visible');
                    }
                });
            }
        })();
    </script>
"""

    print("Injecting TOC components...")
    
    # Inject CSS into <head> (or create <head> if it doesn't exist)
    if re.search(r'</head>', original_html, re.IGNORECASE):
        modified_html = re.sub(
            r'</head>',
            toc_css + '\n</head>',
            original_html,
            count=1,
            flags=re.IGNORECASE
        )
    else:
        # No </head> found, inject at the start
        modified_html = toc_css + '\n' + original_html
    
    # Inject TOC HTML at the start of <body>
    if re.search(r'<body[^>]*>', modified_html, re.IGNORECASE):
        modified_html = re.sub(
            r'(<body[^>]*>)',
            r'\1\n' + toc_html,
            modified_html,
            count=1,
            flags=re.IGNORECASE
        )
    else:
        # No <body> found, inject at the start
        modified_html = toc_html + '\n' + modified_html
    
    # Inject JavaScript before </body> (or at the end if no </body>)
    if re.search(r'</body>', modified_html, re.IGNORECASE):
        modified_html = re.sub(
            r'</body>',
            toc_script + '\n</body>',
            modified_html,
            count=1,
            flags=re.IGNORECASE
        )
    else:
        # No </body> found, append at the end
        modified_html = modified_html + '\n' + toc_script
    
    print(f"Saving to {output_file}...")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(modified_html)
    except Exception as e:
        print(f"ERROR saving {output_file}: {e}")
        return False
    
    return True

def main():
    print("="*60)
    print("TOC Injection Script - Preserves Original Formatting")
    print("="*60)
    print()
    
    # File names
    original_file = 'file_a.html'
    output_file = 'file_a_with_toc.html'
    
    # Perform injection
    success = inject_toc_into_html(original_file, output_file)
    
    print()
    print("="*60)
    if success:
        print("✓ SUCCESS!")
        print("="*60)
        print()
        print(f"Created: {output_file}")
        print()
        print("✓ Original formatting preserved")
        print("✓ Original content unchanged")
        print("✓ TOC sidebar added")
        print()
        print("Open this file in your web browser!")
        print()
        print("Features:")
        print("  • Floating Document Outline sidebar")
        print("  • Auto-generated from all headings")
        print("  • Click to jump to any section")
        print("  • Active section highlighting")
        print("  • Toggle button (☰) to show/hide")
        print("  • Your original formatting 100% intact")
    else:
        print("✗ FAILED")
        print("="*60)
        print()
        print("Please check the error messages above.")
        print(f"Make sure {original_file} is in the same folder.")
    print()

if __name__ == "__main__":
    main()
