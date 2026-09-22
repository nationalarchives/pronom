"""
Generate the full Release Notes XML from the changelog. The structure of the release notes is as follows:
    <?xml version="1.0" encoding="utf-8"?>
    <?xml-stylesheet type="text/xsl" href="release-note.xsl"?>
    <release_notes>
    <release_note>
       <release_date>2nd September 2026</release_date>
       <signature_filename>DROID_SignatureFile_V125.xml</signature_filename>
       <release_outline name="New Records">f
          <format>
             <puid type="fmt">2105</puid>
             <name>ForTheRecord TRM Audio</name>
             <summary>Full entry added. Submitted by Preservica.</summary>
          </format>
          .
          .
          .
       </release_outline>   
       <release_outline name="Updated Records">f
          <format>
             <puid type="fmt">45</puid>
             <name>Rich Text Format</name>
             <summary>Updated signature to allow for whitespace as per specification. Submitted by Archives nationales de France.</summary>
          </format>
          .
          .
          .
       </release_outline>   
       <release_outline name="New Signatures">
          <format>
             <puid type="fmt">2105</puid>
             <name>ForTheRecord TRM Audio</name>
             <summary>Signature researched and samples provided by Preservica.</summary>
          </format>      
       </release_outline>
    </release_note>
    </release_notes>   

The file is written in such a way that the release_note elements are arranged in descending order of date, i.e. the newest
 release_note appears at the beginning of the file  
 
 Expected name for each changelog file: changelog-vNNN-NNNN-NN-NN.csv, e.g. changelog-v88-2016-09-27.csv. Elements from the 
 filename are used to populate release_date and signature_filename
 
Expected data in each changelog file is a 3 column CSV as shown below: 
New Records,fmt/974,Notation Interchange File Format: Full entry added.
Updated Records,fmt/6,Waveform Audio: Simplified signature at suggestion of National Library of New Zealand.
New Signatures,fmt/951,Sonic Foundry WAVE 64: Signature developed through PRONOM Research.
 
Data from each row is used to populate name attribute of the release_outline as well as the puid, name and summary elements
inside the format element  
"""
import os
import re
import csv
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree

def get_ordinal_formatted_date(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    day = date.day
    ordinal_suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{ordinal_suffix} {date.strftime('%B %Y')}"

def get_name_and_summary(summary):
    # A ':' can appear more than once, splitting on ': ' works best based on analysing existing data
    summary_parts = summary.split(": ", 1)
    return summary_parts[0], summary_parts[1] if len(summary_parts) > 1 else ""

def create_format_element(puid, summary):
    format_elem = Element('format')
    puid_type, puid_value = puid.split("/", 1)
    SubElement(format_elem, "puid", type=puid_type).text = puid_value
    name, summary = get_name_and_summary(summary)
    SubElement(format_elem, 'name').text = name  # Extract name before colon
    SubElement(format_elem, 'summary').text = summary   # Extract summary after colon
    return format_elem

def create_release_outline_element(outline_name, all_rows):
    release_outline = Element('release_outline', name=outline_name)
    for row in all_rows:
        if row[0].strip() == outline_name:
            outline_name, puid, summary = row
            release_outline.append(create_format_element(puid, summary))
    return release_outline

def create_release_note_element(changelog_file_name, all_rows):
    release_note = Element('release_note')
    
    version = changelog_file_name.split("-", 2)[1][1:]
    date_str = changelog_file_name.split("-", 2)[2].removesuffix(".csv")
    release_date = get_ordinal_formatted_date(date_str)
    droid_signature_file = f'DROID_SignatureFile_V{version}.xml'

    SubElement(release_note, 'release_date').text = release_date
    SubElement(release_note, 'signature_filename').text = droid_signature_file

    for outline_name in ["New Records", "Updated Records", "Signatures", "New Signatures"]:
        if any(row[0].strip() == outline_name for row in all_rows):
            release_note.append(create_release_outline_element(outline_name, all_rows))

    return release_note

def create_release_notes_from_changelogs(path_to_changelog_files):
    release_notes = Element('release_notes')
    changelog_files = [
        f for f in os.listdir(path_to_changelog_files)
        if re.match(r'^changelog-v\d+-\d{4}-\d{2}-\d{2}\.csv$', f)
    ]

    # Sort files in descending order based on the date in the filename
    changelog_files.sort(key=lambda f: int(f.split("-")[1].removeprefix("v")), reverse=True)
    for changelog_file in changelog_files:
        with open(f'{path_to_changelog_files}/{changelog_file}', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            all_rows = [
                row for row in reader
                if len(row) == 3
            ]
            release_notes.append(create_release_note_element(changelog_file, all_rows))

    return release_notes

def run():
    # Create the root element
    release_notes = create_release_notes_from_changelogs('./../../changelogs')

    # Write the XML to a file
    tree = ElementTree(release_notes)
    with open('release_notes.xml', 'wb') as xmlfile:
        xmlfile.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
        xmlfile.write(b'<?xml-stylesheet type="text/xsl" href="release-note.xsl"?>\n')
        tree.write(xmlfile, encoding='utf-8', xml_declaration=False)

# Example usage
if __name__ == "__main__":
    run()