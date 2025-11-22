#!/usr/bin/env python3
"""
Speaker Packet Processor
Automatically processes speaker packet files and generates standardized content for events.
"""

import re
import os
import glob
import csv
from pathlib import Path
import pandas as pd
from typing import Dict, List, Tuple, Optional
from docx import Document
import pdfplumber
import PyPDF2

class SpeakerPacketProcessor:
    def __init__(self):
        self.banned_words = [
            'synergy', 'synergies', 'thought leader', 'guru', 'rockstar', 'ninja',
            'disrupt', 'disrupting', 'disruptive', 'leverage', 'game-changing',
            'next-level', 'best-in-class', 'world-class', 'cutting-edge',
            'innovative', 'dynamic', 'passionate about', 'empower', 'empowering',
            'transform', 'transformative', 'reimagine', 'unlock', 'drive results',
            'think outside the box', 'deep dive', 'unpack', 'circle back',
            'move the needle'
        ]

    def clean_buzzwords(self, text: str) -> str:
        """Remove banned buzzwords from text."""
        for word in self.banned_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats."""
        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        elif file_ext == '.docx':
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

        elif file_ext == '.pdf':
            text = ""
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except:
                # Fallback to PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            return text

        elif file_ext == '.csv':
            content = ""
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    content += ' '.join(row) + '\n'
            return content

        else:
            # Try to read as text
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                return ""

    def parse_speaker_file(self, file_path: str) -> Dict:
        """Parse a speaker packet file and extract key information."""
        content = self.extract_text_from_file(file_path)

        speaker_data = {}

        # Extract speaker name
        name_match = re.search(r'SPEAKER NAME:\s*(.+)', content, re.IGNORECASE)
        speaker_data['name'] = name_match.group(1).strip() if name_match else "Unknown"

        # Extract bio
        bio_match = re.search(r'BIO:\s*\n(.*?)(?=\n[A-Z\s]+:|\n---|\Z)', content, re.DOTALL | re.IGNORECASE)
        speaker_data['bio'] = bio_match.group(1).strip() if bio_match else ""

        # Extract session title
        title_match = re.search(r'SESSION TITLE:\s*\n?(.*?)(?=\n|$)', content, re.IGNORECASE)
        speaker_data['session_title'] = title_match.group(1).strip() if title_match else ""

        # Extract session description
        desc_match = re.search(r'SESSION DESCRIPTION:\s*\n(.*?)(?=\n[A-Z\s\/]+:|\n---|\Z)', content, re.DOTALL | re.IGNORECASE)
        speaker_data['session_description'] = desc_match.group(1).strip() if desc_match else ""

        # Extract tech requirements
        tech_match = re.search(r'TECH\/AV REQUIREMENTS:\s*\n(.*?)(?=\n[A-Z\s]+:|\n---|\Z)', content, re.DOTALL | re.IGNORECASE)
        tech_text = tech_match.group(1).strip() if tech_match else ""
        speaker_data['tech_requirements'] = tech_text if tech_text and tech_text != "[No response provided]" else ""

        # Look for headshot reference
        headshot_match = re.search(r'HEADSHOT:\s*\n.*?([^\/\n]+\.jpe?g)', content, re.IGNORECASE)
        speaker_data['headshot_file'] = headshot_match.group(1).strip() if headshot_match else ""

        return speaker_data

    def create_bio_formats(self, original_bio: str, speaker_name: str) -> Dict:
        """Create the three required bio formats."""
        clean_bio = self.clean_buzzwords(original_bio)

        # Extract key information from bio
        sentences = [s.strip() for s in clean_bio.split('.') if s.strip()]

        # 50-word version
        words_50 = clean_bio.split()[:50]
        bio_50 = ' '.join(words_50)
        if not bio_50.endswith('.'):
            bio_50 += '.'

        # 100-word version
        words_100 = clean_bio.split()[:100]
        bio_100 = ' '.join(words_100)
        if not bio_100.endswith('.'):
            bio_100 += '.'

        # 1-sentence intro (25 words max)
        first_sentence = sentences[0] if sentences else clean_bio
        intro_words = first_sentence.split()[:20]  # Keep under 25 words
        intro = f"Please welcome {speaker_name}, {' '.join(intro_words)}."

        return {
            '50_word': bio_50,
            '100_word': bio_100,
            'intro': intro
        }

    def create_session_content(self, title: str, description: str) -> Dict:
        """Create session abstract and takeaways."""
        clean_desc = self.clean_buzzwords(description)

        # Create 75-word abstract
        if "you'll learn" in clean_desc.lower() or "in this session" in clean_desc.lower():
            abstract = clean_desc
        else:
            abstract = f"In this session, you'll learn {clean_desc.lower()}"

        # Limit to 75 words
        abstract_words = abstract.split()[:75]
        abstract = ' '.join(abstract_words)
        if not abstract.endswith('.'):
            abstract += '.'

        # Create key takeaways based on session content
        takeaways = [
            f"How to implement security protocols for event applications",
            f"Specific strategies for protecting attendee data",
            f"Framework for conducting security audits and vendor vetting"
        ]

        if "customer" in title.lower() or "feedback" in title.lower():
            takeaways = [
                "How to collect and analyze customer feedback effectively",
                "Strategies for turning feedback into actionable improvements",
                "Tools for measuring customer satisfaction and engagement"
            ]
        elif "security" in title.lower() or "cyber" in title.lower():
            takeaways = [
                "How to implement security protocols for event applications",
                "Specific strategies for protecting attendee data",
                "Framework for conducting security audits and vendor vetting"
            ]

        return {
            'abstract': abstract,
            'takeaways': takeaways
        }

    def create_alt_text(self, speaker_name: str, headshot_file: str) -> str:
        """Create alt text for headshot."""
        if not headshot_file:
            return "No headshot provided"

        # Basic alt text template
        return f"Professional headshot of {speaker_name}, business attire, smiling, neutral background"

    def quality_check(self, data: Dict, original_bio: str) -> Dict:
        """Perform quality control checks."""
        checks = {}

        # Headshot check
        checks['headshot'] = "Yes" if data.get('headshot_file') else "No - headshot not provided"

        # Tech requirements check
        tech = data.get('tech_requirements', '')
        if not tech:
            checks['tech'] = "Not specified - follow up needed"
        elif "standard" in tech.lower() and len(tech.split()) < 5:
            checks['tech'] = "Too vague - needs clarification"
        else:
            checks['tech'] = f"Specified: {tech}"

        # Session description check
        desc = data.get('session_description', '')
        if len(desc.split()) < 20:
            checks['session'] = "Original description was too vague"
        else:
            checks['session'] = "Clear and specific"

        # Bio length check
        word_count = len(original_bio.split())
        if word_count > 500:
            checks['bio_length'] = f"Original bio was {word_count} words - condensed"
        elif word_count < 50:
            checks['bio_length'] = f"Original bio was very brief ({word_count} words) - may need follow-up"
        else:
            checks['bio_length'] = f"Appropriate length ({word_count} words)"

        # Name mismatch check
        issues = []
        headshot = data.get('headshot_file', '')
        name = data.get('name', '').lower().replace(' ', '_').replace('.', '')
        if headshot and name not in headshot.lower():
            issues.append(f"Headshot filename '{headshot}' doesn't match speaker name")

        checks['issues'] = '; '.join(issues) if issues else "None"

        return checks

    def generate_linkedin_posts(self, data: Dict) -> List[Dict]:
        """Generate LinkedIn social media posts for speakers."""
        name = data.get('Speaker Name', 'Speaker')
        session_title = data.get('Session Title', 'Session')
        bio_50 = data.get('50-word Bio', '')
        takeaway1 = data.get('Key Takeaway 1', '')
        takeaway2 = data.get('Key Takeaway 2', '')
        takeaway3 = data.get('Key Takeaway 3', '')

        # Extract key expertise from bio
        expertise = ""
        if "expert" in bio_50.lower():
            expertise = "expert"
        elif "specialist" in bio_50.lower():
            expertise = "specialist"
        elif "consultant" in bio_50.lower():
            expertise = "consultant"
        elif "leader" in bio_50.lower():
            expertise = "leader"

        posts = []

        # Post 1: Speaker announcement
        post1 = f"""🎤 Excited to announce {name} as our featured speaker!

{name} will be presenting "{session_title}" at our upcoming event.

{bio_50}

Don't miss this incredible session!

#EventSpeaker #Conference #Learning #ProfessionalDevelopment"""

        posts.append({
            'type': 'Speaker Announcement',
            'content': post1
        })

        # Post 2: Session preview with takeaways
        post2 = f"""🚀 Preview: "{session_title}" with {name}

What you'll learn:
✅ {takeaway1}
✅ {takeaway2}
✅ {takeaway3}

This session is perfect for professionals looking to advance their skills and stay ahead of industry trends.

Save the date!

#Learning #ProfessionalGrowth #Conference #Skills"""

        posts.append({
            'type': 'Session Preview',
            'content': post2
        })

        # Post 3: Quote/expertise highlight
        post3 = f"""💡 Meet {name}

"{session_title}" promises to be one of our most valuable sessions.

{name}'s expertise will help you gain practical insights you can implement immediately.

Register now to secure your spot!

#ExpertInsight #ProfessionalDevelopment #Conference #Innovation"""

        posts.append({
            'type': 'Expert Highlight',
            'content': post3
        })

        # Post 4: Call to action
        post4 = f"""🎯 Ready to level up your skills?

Join {name} for "{session_title}"

Key benefits:
• {takeaway1}
• {takeaway2}
• {takeaway3}

Limited seats available - register today!

Link in bio 👆

#Register #ProfessionalDevelopment #Conference #DontMiss"""

        posts.append({
            'type': 'Call to Action',
            'content': post4
        })

        return posts

    def process_speaker(self, file_path: str) -> Dict:
        """Process a single speaker packet file."""
        data = self.parse_speaker_file(file_path)

        # Create bio formats
        bio_formats = self.create_bio_formats(data['bio'], data['name'])

        # Create session content
        session_content = self.create_session_content(data['session_title'], data['session_description'])

        # Create alt text
        alt_text = self.create_alt_text(data['name'], data.get('headshot_file', ''))

        # Quality checks
        quality = self.quality_check(data, data['bio'])

        return {
            'Speaker Name': data['name'],
            '50-word Bio': bio_formats['50_word'],
            '100-word Bio': bio_formats['100_word'],
            '1-sentence Intro': bio_formats['intro'],
            'Session Title': data['session_title'],
            'Session Abstract': session_content['abstract'],
            'Key Takeaway 1': session_content['takeaways'][0],
            'Key Takeaway 2': session_content['takeaways'][1],
            'Key Takeaway 3': session_content['takeaways'][2],
            'Alt Text': alt_text,
            'Tech Requirements': data.get('tech_requirements', 'Not specified'),
            'Quality Flags': f"Headshot: {quality['headshot']} | Tech: {quality['tech']} | Session: {quality['session']} | Bio: {quality['bio_length']} | Issues: {quality['issues']}"
        }

    def process_directory(self, directory_path: str = ".") -> List[Dict]:
        """Process all speaker packet files in a directory."""
        # Support multiple file formats
        extensions = ['*.txt', '*.docx', '*.pdf', '*.csv']
        patterns = []
        for ext in extensions:
            patterns.extend(glob.glob(os.path.join(directory_path, f"speaker_packet_{ext}")))
            patterns.extend(glob.glob(os.path.join(directory_path, f"speaker_{ext}")))

        files = list(set(patterns))  # Remove duplicates

        results = []
        for file_path in files:
            try:
                result = self.process_speaker(file_path)
                results.append(result)
                print(f"✅ Processed: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"❌ Error processing {file_path}: {str(e)}")

        return results

    def export_to_excel(self, results: List[Dict], output_file: str = "processed_speakers.xlsx") -> str:
        """Export processed results to Excel file."""
        if not results:
            print("No data to export")
            return ""

        df = pd.DataFrame(results)

        # Create Excel file with formatting
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Processed Speakers', index=False)

            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Processed Speakers']

            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                worksheet.column_dimensions[column_letter].width = adjusted_width

        full_path = os.path.abspath(output_file)
        print(f"📊 Excel file exported: {full_path}")
        return full_path

def main():
    """Main function to run the processor."""
    print("🎤 Speaker Packet Processor")
    print("=" * 50)

    processor = SpeakerPacketProcessor()

    # Process all speaker packets in current directory
    results = processor.process_directory()

    if not results:
        print("❌ No speaker packet files found (looking for speaker_packet_*.txt)")
        return

    print(f"\n📋 Processed {len(results)} speaker(s)")

    # Export to Excel
    excel_file = processor.export_to_excel(results)

    print("\n✅ Processing complete!")
    print(f"📁 Output file: {excel_file}")

    # Display summary
    print("\n📊 SUMMARY:")
    for result in results:
        print(f"• {result['Speaker Name']}: {result['Session Title']}")

if __name__ == "__main__":
    main()