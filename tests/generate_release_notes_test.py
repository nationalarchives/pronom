import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".github"/"scripts"))
import generate_full_xml_release_notes
from xml.etree.ElementTree import tostring
import tempfile

class MyTestCase(unittest.TestCase):
    def test_date_should_be_formatted_with_ordinal(self):
        self.assertEqual("5th June 2024", generate_full_xml_release_notes.create_ordinal_formatted_date("2024-06-05"))
        self.assertEqual("1st January 2024", generate_full_xml_release_notes.create_ordinal_formatted_date("2024-01-01"))
        self.assertEqual("2nd June 2024", generate_full_xml_release_notes.create_ordinal_formatted_date("2024-06-02"))
        self.assertEqual("11th June 2024", generate_full_xml_release_notes.create_ordinal_formatted_date("2024-06-11"))
        self.assertEqual("21st November 2024", generate_full_xml_release_notes.create_ordinal_formatted_date("2024-11-21"))
        self.assertEqual("22nd August 2024", generate_full_xml_release_notes.create_ordinal_formatted_date("2024-08-22"))
        self.assertEqual("23rd July 2024", generate_full_xml_release_notes.create_ordinal_formatted_date("2024-07-23"))

    def test_get_name_and_summary_should_split_on_colon_to_generate_correct_name_and_summary(self):
        self.assertEqual(("", ""), generate_full_xml_release_notes.create_name_and_summary(""))
        self.assertEqual(("Acrobat PDF/X - Portable Document Format - Exchange 1:2001", "Signature developed through PRONOM Research."),
                         generate_full_xml_release_notes.create_name_and_summary("Acrobat PDF/X - Portable Document Format - Exchange 1:2001: Signature developed through PRONOM Research."))
        self.assertEqual(("Acrobat PDF/X - Portable Document Format - Exchange 1:2001", "Signature developed through PRONOM Research."),
                         generate_full_xml_release_notes.create_name_and_summary("Acrobat PDF/X - Portable Document Format - Exchange 1:2001: Signature developed through PRONOM Research."))
        self.assertEqual(("EndNote Import File", "Amended internal sigs EndNote Import File No.1 and EndNote Import File No.2: Changed wildcard to {5-50}. Amended bytes within sequences from (44|54) to (41|42|43|44|54). Submitted by The National Library of Australia."),
                         generate_full_xml_release_notes.create_name_and_summary("EndNote Import File: Amended internal sigs EndNote Import File No.1 and EndNote Import File No.2: Changed wildcard to {5-50}. Amended bytes within sequences from (44|54) to (41|42|43|44|54). Submitted by The National Library of Australia."))
        self.assertEqual(("Rich Text Format 0", "Removed extraneous whitespace preceeding format name. Error identified by Andy Jackson's file format registry aggregator - http://www.digipres.org/formats/- hosted on the DigiPres Commons website."),
                         generate_full_xml_release_notes.create_name_and_summary("Rich Text Format 0: Removed extraneous whitespace preceeding format name. Error identified by Andy Jackson's file format registry aggregator - http://www.digipres.org/formats/- hosted on the DigiPres Commons website."))
        
    def test_create_format_element_should_create_a_format_element_using_puid_and_summary(self):
        format_elem = generate_full_xml_release_notes.create_format_element("fmt/974", "Notation Interchange File Format: Full entry added.")
        self.assertEqual(b"<format><puid type=\"fmt\">974</puid><name>Notation Interchange File Format</name><summary>Full entry added.</summary></format>", tostring(format_elem, encoding="utf-8"))

        format_elem = generate_full_xml_release_notes.create_format_element("x-fmt/19", "3D Studio: Added variant signature based on samples")
        self.assertEqual(b"<format><puid type=\"x-fmt\">19</puid><name>3D Studio</name><summary>Added variant signature based on samples</summary></format>", tostring(format_elem, encoding="utf-8"))
        
    def test_create_release_outline_element_for_given_outline(self):        
        all_rows = [
            ["New Records", "fmt/974", "Notation Interchange File Format: Full entry added."],
            ["Updated Records", "fmt/6", "Waveform Audio: Simplified signature at suggestion of National Library of New Zealand."],
            ["New Signatures", "fmt/951", "Sonic Foundry WAVE 64: Signature developed through PRONOM Research."]
        ]
        release_outline = generate_full_xml_release_notes.create_release_outline_element("New Records", all_rows)
        self.assertEqual(b"<release_outline name=\"New Records\"><format><puid type=\"fmt\">974</puid><name>Notation Interchange File Format</name><summary>Full entry added.</summary></format></release_outline>", tostring(release_outline, encoding="utf-8"))

        release_outline = generate_full_xml_release_notes.create_release_outline_element("Updated Records", all_rows)
        self.assertEqual(b"<release_outline name=\"Updated Records\"><format><puid type=\"fmt\">6</puid><name>Waveform Audio</name><summary>Simplified signature at suggestion of National Library of New Zealand.</summary></format></release_outline>", tostring(release_outline, encoding="utf-8"))
        
        release_outline = generate_full_xml_release_notes.create_release_outline_element("New Signatures", all_rows)
        self.assertEqual(b"<release_outline name=\"New Signatures\"><format><puid type=\"fmt\">951</puid><name>Sonic Foundry WAVE 64</name><summary>Signature developed through PRONOM Research.</summary></format></release_outline>", tostring(release_outline, encoding="utf-8"))

    def test_create_release_note_from_all_rows(self):
        all_rows = [
            ["New Records", "fmt/974", "Notation Interchange File Format: Full entry added."],
            ["Updated Records", "fmt/6", "Waveform Audio: Simplified signature at suggestion of National Library of New Zealand."],
            ["New Signatures", "fmt/951", "Sonic Foundry WAVE 64: Signature developed through PRONOM Research."]
        ]
        release_note = generate_full_xml_release_notes.create_release_note_element("changelog-v31-2024-06-01.csv", all_rows)
        self.assertEqual(b"<release_note><release_date>1st June 2024</release_date><signature_filename>DROID_SignatureFile_V31.xml</signature_filename><release_outline name=\"New Records\"><format><puid type=\"fmt\">974</puid><name>Notation Interchange File Format</name><summary>Full entry added.</summary></format></release_outline><release_outline name=\"Updated Records\"><format><puid type=\"fmt\">6</puid><name>Waveform Audio</name><summary>Simplified signature at suggestion of National Library of New Zealand.</summary></format></release_outline><release_outline name=\"New Signatures\"><format><puid type=\"fmt\">951</puid><name>Sonic Foundry WAVE 64</name><summary>Signature developed through PRONOM Research.</summary></format></release_outline></release_note>", tostring(release_note, encoding="utf-8"))

    def test_create_release_note_from_all_rows_should_ignore_unsupported_outline_names(self):
        all_rows = [
            ["New Records", "fmt/974", "Notation Interchange File Format: Full entry added."],
            ["Non Updated Records", "fmt/6", "Waveform Audio: Simplified signature at suggestion of National Library of New Zealand."],
            ["Old Signatures", "fmt/951", "Sonic Foundry WAVE 64: Signature developed through PRONOM Research."]
        ]
        release_note = generate_full_xml_release_notes.create_release_note_element("changelog-v31-2024-06-01.csv", all_rows)
        self.assertEqual(b"<release_note><release_date>1st June 2024</release_date><signature_filename>DROID_SignatureFile_V31.xml</signature_filename><release_outline name=\"New Records\"><format><puid type=\"fmt\">974</puid><name>Notation Interchange File Format</name><summary>Full entry added.</summary></format></release_outline></release_note>", tostring(release_note, encoding="utf-8"))

    def test_should_create_release_notes_from_changelog_files_in_given_folder(self):
        with (tempfile.TemporaryDirectory() as tmpdir):
            tmpdir = Path(tmpdir)
            (tmpdir / "changelog-v124-2026-07-03.csv").write_text("New Records,fmt/2094,M4a Audio: Description of M4a audio\nUpdated Records,fmt/596,Apple Lossless Audio Codec: Updated.\nNew Signatures,fmt/2104,Discus Project 4: Signature researched")
            (tmpdir / "changelog-v123-2026-06-09.csv").write_text("New Records,fmt/2096,GGML Universal File (GGUF) 1: Full entry added\nUpdated Records,fmt/875,RDF/XML: Two new internal signatures\nNew Signatures,fmt/720,MBox: New")
            
            release_notes = generate_full_xml_release_notes.create_release_notes_from_changelogs(tmpdir)
            print(tostring(release_notes, encoding="utf-8"))
            self.assertEqual(b"<release_notes><release_note><release_date>3rd July 2026</release_date><signature_filename>DROID_SignatureFile_V124.xml</signature_filename><release_outline name=\"New Records\"><format><puid type=\"fmt\">2094</puid><name>M4a Audio</name><summary>Description of M4a audio</summary></format></release_outline><release_outline name=\"Updated Records\"><format><puid type=\"fmt\">596</puid><name>Apple Lossless Audio Codec</name><summary>Updated.</summary></format></release_outline><release_outline name=\"New Signatures\"><format><puid type=\"fmt\">2104</puid><name>Discus Project 4</name><summary>Signature researched</summary></format></release_outline></release_note><release_note><release_date>9th June 2026</release_date><signature_filename>DROID_SignatureFile_V123.xml</signature_filename><release_outline name=\"New Records\"><format><puid type=\"fmt\">2096</puid><name>GGML Universal File (GGUF) 1</name><summary>Full entry added</summary></format></release_outline><release_outline name=\"Updated Records\"><format><puid type=\"fmt\">875</puid><name>RDF/XML</name><summary>Two new internal signatures</summary></format></release_outline><release_outline name=\"New Signatures\"><format><puid type=\"fmt\">720</puid><name>MBox</name><summary>New</summary></format></release_outline></release_note></release_notes>", tostring(release_notes, encoding="utf-8"))

if __name__ == '__main__':
    unittest.main()
