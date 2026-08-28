RIVERTON LAWSUIT DOCUMENT LAB

All cases, people, organizations, events, and records in this package are
fictional. The PDFs are searchable and were generated specifically for Frisket
walkthroughs.

TRY THIS IN FRISKET

1. Upload all six PDF files together as a Files import.
2. Open Document view and inspect a source filing.
3. Run Convert to Markdown on the media column and save it as filing_text.
4. Use Regex extract with RV-CV-\d{4}-\d{5} to create case_number.
5. Extract structured data: plaintiff, defendant, filing date, document type,
   requested relief, deadlines, dollar amounts, and cited contract IDs.
6. Ask a source-grounded question such as "Which allegations are disputed or
   explicitly qualified?"
7. Import court-docket.csv and join on case_number or pdf_filename.

The package intentionally mixes complaints, a petition, and motions. A claim in
a complaint is an allegation, not an established fact; use the source text and
citations when reviewing generated answers.
