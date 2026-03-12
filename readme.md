If you open Document outline of your Google document, you cannot export it anywhere else in the exact same form as in your Google document.<br>
While downloading the document as docx, all the headings in the document will be shown in the navigation menu, but with all the ones you've deliberately deleted in your GDoc, now causing a mess in your document outline.<br>
<br>
This script embeeds similarly looking document outline like in the GDoc, into HTML downloaded from GDoc, from a ready list of entries I'll guide you to prepare.
<br><br>
The trick is, I didn't find an automated way to export all the entries in the document outline - you'll need to create the list yourself. I did that by:<br>
1. Opening the GDoc, and this time saving the page as complete HTML site in (...)>Save and share>Save the page as.<br>
2. Then I used GoFullPage addon for Chrome to perform a screenshot of the content 4. Cut it in XnView to show only the outline 5. Then convert it into a text with OCR software, 6. Then corrected the text (you cannot select all the text from such downloaded html file).<br><br>
7. Now the script manual_outline_input.py comes into play. It expects file named "file_a.html" which will be the file downloaded as HTML, but this time from dedicated option in the GDoc.<br>
The script will ask to paste all the entries to embeed for the navigation bar - paste them, then press enter, and input "end" at the end, and press enter - it will write the outline entries into a json file.<br>
Now ignore the output html file, because it will redirect into many incorrect places in the document.<br> 
9. Now the second script called strict_matching_toc_(from_json).py will read all the entries from json you created, and embeed the GDoc-looking document outline into your HTML file (the one downloaded normally with GDoc option - file_a.html). You can edit the json to ensure the script worked correctly, and all the entries are correct.<br>
Be aware that navigation bar in the final file on the left will load around 15 seconds - the detetion of the headings in the second script is more aggresive.
