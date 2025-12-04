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
    def __init__(self, event_theme: str = "", event_tracks: List[str] = None):
        self.banned_words = [
            'synergy', 'synergies', 'thought leader', 'guru', 'rockstar', 'ninja',
            'disrupt', 'disrupting', 'disruptive', 'leverage', 'game-changing',
            'next-level', 'best-in-class', 'world-class', 'cutting-edge',
            'innovative', 'dynamic', 'passionate about', 'empower', 'empowering',
            'transform', 'transformative', 'reimagine', 'unlock', 'drive results',
            'think outside the box', 'deep dive', 'unpack', 'circle back',
            'move the needle'
        ]

        # Event configuration for evaluation
        self.event_theme = event_theme
        self.event_tracks = event_tracks or []

    def clean_buzzwords(self, text: str) -> str:
        """Remove banned buzzwords from text."""
        for word in self.banned_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def clean_filename(self, name: str) -> str:
        """Clean speaker name for use in filenames."""
        # Remove special characters and spaces
        import re
        clean_name = re.sub(r'[^\w\s-]', '', name)
        clean_name = re.sub(r'[-\s]+', '_', clean_name)
        return clean_name.lower()

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

        # Look for headshot reference in content first
        headshot_match = re.search(r'HEADSHOT:\s*\n.*?([^\/\n]+\.jpe?g)', content, re.IGNORECASE)
        if headshot_match:
            speaker_data['headshot_file'] = headshot_match.group(1).strip()
        else:
            # If not found in content, search multiple directories for headshot files
            directories_to_search = [
                os.path.dirname(file_path) if file_path else '.',  # Upload folder
                '.',  # Main project directory
                os.path.join('..', '..') if 'uploads' in file_path else None  # Parent directory if in uploads
            ]

            found_headshot = ""
            for directory_path in directories_to_search:
                if directory_path and os.path.exists(directory_path):
                    found_headshot = self.find_headshot_in_directory(speaker_data['name'], directory_path)
                    if found_headshot:
                        break

            speaker_data['headshot_file'] = found_headshot

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

    def find_headshot_in_directory(self, speaker_name: str, directory_path: str = '.') -> str:
        """Find headshot file in directory based on speaker name."""
        import os
        import glob

        # Common image extensions
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']

        # Clean speaker name for matching
        clean_name = speaker_name.lower().replace(' ', '_').replace('.', '').replace('(', '').replace(')', '').replace('dr_', '').replace('dr', '')
        name_parts = clean_name.split('_')

        # Look for files in the directory
        for ext in image_extensions:
            files = glob.glob(os.path.join(directory_path, ext))
            for file_path in files:
                filename = os.path.basename(file_path).lower()

                # Direct name match (e.g., "dr. olivia thorne.jpeg" matches "Dr. Olivia Thorne")
                if clean_name in filename.replace(' ', '_').replace('.', ''):
                    return os.path.basename(file_path)

                # Check if any part of speaker name is in filename
                for part in name_parts:
                    if len(part) > 2 and part in filename:  # Avoid matching single letters
                        return os.path.basename(file_path)

                # Check for common headshot patterns
                headshot_patterns = ['headshot', 'speaker', 'photo']
                for pattern in headshot_patterns:
                    if pattern in filename:
                        # Check if speaker name parts are also in filename
                        for part in name_parts:
                            if len(part) > 2 and part in filename:
                                return os.path.basename(file_path)

        return ""

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

    def generate_missing_content(self, data: Dict) -> Dict:
        """Generate missing content based on available information."""
        suggestions = {}

        bio = data.get('bio', '')
        session_description = data.get('session_description', '')
        name = data.get('name', '')

        # Generate session titles if missing or placeholder
        session_title = data.get('session_title', '').strip()
        if (not session_title or
            any(placeholder in session_title.lower() for placeholder in ['tbd', 'working title', 'placeholder', 'something cool', 'temp', '[working'])):
            titles = self.generate_session_titles(bio, session_description)
            suggestions['session_titles'] = titles

        # Generate session description if missing
        if not session_description.strip() and bio:
            description = self.generate_session_description(bio)
            suggestions['session_description'] = description

        # Generate tech requirements if missing or vague
        tech_req = data.get('tech_requirements', '')
        if not tech_req.strip() or len(tech_req.split()) < 3:
            tech_suggestions = self.generate_tech_requirements(bio, session_description)
            suggestions['tech_requirements'] = tech_suggestions

        # Generate bio if too short
        if len(bio.split()) < 30:
            enhanced_bio = self.generate_enhanced_bio(name, bio, session_description)
            suggestions['enhanced_bio'] = enhanced_bio

        return suggestions

    def generate_session_titles(self, bio: str, description: str) -> List[str]:
        """Generate 2 session title options based on bio and description."""
        expertise_keywords = self.extract_expertise_keywords(bio)
        content = (bio + " " + description).lower()

        titles = []

        # Analyze content for specific concepts
        if 'immersive' in content or 'experience' in content and ('space' in content or 'room' in content):
            titles.extend([
                "Immersive Experiences: When Spaces Become Performers",
                "Beyond Passive Attendance: Creating Interactive Event Environments"
            ])
        elif 'ai' in content or 'artificial intelligence' in content:
            if 'legacy' in content or 'code' in content:
                titles.extend([
                    "AI-Powered Legacy Transformation: From Technical Debt to Innovation Engine",
                    "Modernizing Legacy Systems with Artificial Intelligence"
                ])
            else:
                titles.extend([
                    f"AI-Powered Innovation: Transforming {expertise_keywords[0] if expertise_keywords else 'Business'} for the Future",
                    f"The Future of {expertise_keywords[0] if expertise_keywords else 'Technology'}: Practical AI Applications"
                ])
        elif 'security' in content or 'cyber' in content:
            titles.extend([
                f"Cybersecurity Best Practices: Protecting Your {expertise_keywords[0] if expertise_keywords else 'Organization'}",
                f"Security in the Digital Age: {expertise_keywords[0] if expertise_keywords else 'Modern'} Threat Prevention"
            ])
        elif 'customer' in content or 'feedback' in content:
            titles.extend([
                "Customer Experience Excellence: Building Lasting Relationships",
                "Transforming Customer Feedback into Actionable Insights"
            ])
        elif 'leadership' in content or 'management' in content:
            titles.extend([
                f"Leadership in the Digital Era: {expertise_keywords[0] if expertise_keywords else 'Strategic'} Management",
                f"Building High-Performance Teams: {expertise_keywords[0] if expertise_keywords else 'Modern'} Leadership Principles"
            ])
        elif 'creative' in content or 'alchemist' in content or 'technologist' in content:
            titles.extend([
                "Creative Technology: The Art of Experience Design",
                "Event Alchemy: Transforming Concepts into Unforgettable Moments"
            ])
        elif 'performance' in content or 'participant' in content:
            titles.extend([
                "Participant as Performer: Redefining Event Engagement",
                "Interactive Storytelling: When Audience Becomes Cast"
            ])
        elif 'vibe' in content or 'atmosphere' in content:
            titles.extend([
                "Designing Atmosphere: The Science of Memorable Experiences",
                "Beyond Content: Creating Transformative Event Environments"
            ])
        else:
            # Generic based on expertise or fallback
            if expertise_keywords:
                titles.extend([
                    f"{expertise_keywords[0]} Innovation: Strategies for Success",
                    f"Mastering {expertise_keywords[0]}: Practical Applications and Best Practices"
                ])
            else:
                titles.extend([
                    "Innovation and Strategy: Building for the Future",
                    "Industry Best Practices: Lessons from the Field"
                ])

        return titles[:2]

    def generate_session_description(self, bio: str) -> str:
        """Generate session description based on bio content."""
        expertise = self.extract_expertise_keywords(bio)

        description = f"In this session, you'll learn practical strategies and insights from an industry expert with extensive experience in {', '.join(expertise[:2]) if expertise else 'their field'}. "
        description += "Discover actionable techniques you can implement immediately to improve your processes and achieve better results. "
        description += "This session includes real-world case studies, proven frameworks, and interactive discussions to help you apply these concepts in your own work."

        return description

    def generate_tech_requirements(self, bio: str, description: str) -> List[str]:
        """Generate appropriate tech requirements based on session content."""
        requirements = [
            "Projector with HDMI connection",
            "Wireless lavalier microphone",
            "Screen for presentation slides",
            "Power outlet for laptop",
            "WiFi access for attendees"
        ]

        # Add specific requirements based on content
        if 'demo' in description.lower() or 'demonstration' in description.lower():
            requirements.insert(2, "Internet connection for live demonstrations")

        if 'interactive' in description.lower() or 'workshop' in description.lower():
            requirements.append("Tables for small group work")
            requirements.append("Flip chart paper and markers")

        if 'security' in bio.lower() or 'cyber' in bio.lower():
            requirements.insert(2, "Secure network connection")

        return requirements[:4]  # Return top 4 most relevant

    def generate_enhanced_bio(self, name: str, bio: str, description: str) -> str:
        """Generate enhanced bio when original is too short."""
        if not bio.strip():
            bio = f"{name} is a seasoned professional with extensive experience in their field."

        expertise = self.extract_expertise_keywords(bio + " " + description)

        enhanced = bio + " "
        if expertise:
            enhanced += f"With deep expertise in {', '.join(expertise[:2])}, {name.split()[0] if name else 'they'} brings practical insights and proven strategies to help organizations succeed. "

        enhanced += f"{name.split()[0] if name else 'They'} is known for delivering actionable content that attendees can implement immediately in their work."

        return enhanced

    def extract_expertise_keywords(self, text: str) -> List[str]:
        """Extract key expertise areas from text."""
        expertise_patterns = [
            r'\b(artificial intelligence|AI|machine learning|ML)\b',
            r'\b(cybersecurity|security|cyber)\b',
            r'\b(customer experience|CX|user experience|UX)\b',
            r'\b(leadership|management|strategy)\b',
            r'\b(data science|analytics|data)\b',
            r'\b(cloud computing|cloud|AWS|Azure)\b',
            r'\b(digital transformation|digitalization)\b',
            r'\b(software development|programming|coding)\b',
            r'\b(marketing|digital marketing|social media)\b',
            r'\b(project management|agile|scrum)\b'
        ]

        expertise = []
        text_lower = text.lower()

        for pattern in expertise_patterns:
            if re.search(pattern, text_lower):
                match = re.search(pattern, text_lower)
                if match:
                    expertise.append(match.group(1).title())

        return list(set(expertise))  # Remove duplicates

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

    def evaluate_session(self, speaker_data: Dict) -> Dict:
        """
        Evaluate a session submission on 6 criteria using 1-5 scale.
        Returns evaluation scores and recommendation.
        """
        bio = speaker_data.get('bio', '') or speaker_data.get('100-word Bio', '')
        session_title = speaker_data.get('session_title', '') or speaker_data.get('Session Title', '')
        session_description = speaker_data.get('session_description', '') or speaker_data.get('Session Abstract', '')

        # Initialize scores (1-5 scale, equal weights)
        scores = {}

        # 1. Relevance to Event Theme (1-5)
        relevance_score = self._score_relevance(session_title, session_description)
        scores['Relevance to Theme'] = relevance_score

        # 2. Track Alignment (1-5)
        alignment_score = self._score_track_alignment(session_title, session_description)
        scores['Track Alignment'] = alignment_score

        # 3. Speaker Credibility (1-5)
        credibility_score = self._score_credibility(bio)
        scores['Speaker Credibility'] = credibility_score

        # 4. Presentation Quality (1-5)
        presentation_score = self._score_presentation(session_description, speaker_data)
        scores['Presentation Quality'] = presentation_score

        # 5. Audience Engagement Potential (1-5)
        engagement_score = self._score_engagement(session_title, session_description)
        scores['Audience Engagement'] = engagement_score

        # 6. Innovation Factor (1-5)
        innovation_score = self._score_innovation(session_title, session_description)
        scores['Innovation Factor'] = innovation_score

        # Calculate total score (out of 30, equal weights)
        total_score = sum(scores.values())

        # Get recommendation
        recommendation = self._get_recommendation(total_score)

        # Compile evaluation results
        evaluation = {
            'scores': scores,
            'total_score': total_score,
            'max_score': 30,
            'percentage': round((total_score / 30) * 100, 1),
            'recommendation': recommendation['decision'],
            'recommendation_reason': recommendation['reason'],
            'strengths': self._identify_strengths(scores),
            'improvements': self._identify_improvements(scores)
        }

        return evaluation

    def _score_relevance(self, title: str, description: str) -> int:
        """Score relevance to event theme (1-5)."""
        if not self.event_theme:
            return 3  # Default moderate score if no theme set

        content = (title + " " + description).lower()
        theme_lower = self.event_theme.lower()

        # Check for exact theme matches
        if theme_lower in content:
            return 5

        # Check for related keywords
        theme_keywords = theme_lower.split()
        matches = sum(1 for keyword in theme_keywords if keyword in content)

        if matches >= len(theme_keywords) * 0.7:  # 70%+ keywords match
            return 4
        elif matches >= len(theme_keywords) * 0.4:  # 40-69% match
            return 3
        elif matches > 0:  # Some match
            return 2
        else:
            return 1  # No clear relevance

    def _score_track_alignment(self, title: str, description: str) -> int:
        """Score alignment with event tracks (1-5)."""
        if not self.event_tracks:
            return 3  # Default if no tracks defined

        content = (title + " " + description).lower()

        # Check for exact track matches
        for track in self.event_tracks:
            if track.lower() in content:
                return 5

        # Check for related keywords from tracks
        track_keywords = set()
        for track in self.event_tracks:
            track_keywords.update(track.lower().split())

        matches = sum(1 for keyword in track_keywords if keyword in content)

        if matches >= 3:
            return 4
        elif matches == 2:
            return 3
        elif matches == 1:
            return 2
        else:
            return 1

    def _score_credibility(self, bio: str) -> int:
        """Score speaker credibility based on qualifications (1-5)."""
        if not bio or len(bio.strip()) < 20:
            return 1

        credibility_indicators = {
            5: ['phd', 'professor', 'founder', 'ceo', 'author', 'published', 'award-winning'],
            4: ['director', 'vp', 'senior', 'expert', 'consultant', 'years experience', 'certified'],
            3: ['manager', 'specialist', 'professional', 'experienced'],
            2: ['coordinator', 'associate', 'assistant'],
        }

        bio_lower = bio.lower()

        # Check for highest level indicators first
        for score in [5, 4, 3, 2]:
            for indicator in credibility_indicators[score]:
                if indicator in bio_lower:
                    return score

        # Default score if bio exists but no clear indicators
        return 2

    def _score_presentation(self, description: str, speaker_data: Dict) -> int:
        """Score presentation quality and structure (1-5)."""
        if not description or len(description.strip()) < 30:
            return 1

        score = 3  # Start with baseline

        # Check for clear learning outcomes
        if any(phrase in description.lower() for phrase in ["you'll learn", "you will learn", "attendees will", "participants will"]):
            score += 1

        # Check for specificity and detail
        word_count = len(description.split())
        if word_count >= 75:
            score += 1

        # Check for takeaways
        if speaker_data.get('Key Takeaway 1'):
            score = min(score + 1, 5)

        return min(score, 5)

    def _score_engagement(self, title: str, description: str) -> int:
        """Score likelihood to draw interest and participation (1-5)."""
        content = (title + " " + description).lower()

        engagement_keywords = {
            'high': ['interactive', 'hands-on', 'workshop', 'demo', 'live', 'participate', 'engagement'],
            'medium': ['practical', 'actionable', 'learn', 'discover', 'explore', 'case study'],
            'low': ['overview', 'introduction', 'basics', 'fundamentals']
        }

        # Check for high engagement indicators
        high_matches = sum(1 for keyword in engagement_keywords['high'] if keyword in content)
        if high_matches >= 2:
            return 5
        elif high_matches == 1:
            return 4

        # Check for medium engagement indicators
        medium_matches = sum(1 for keyword in engagement_keywords['medium'] if keyword in content)
        if medium_matches >= 3:
            return 4
        elif medium_matches >= 2:
            return 3
        elif medium_matches == 1:
            return 2

        # Check for low engagement indicators
        low_matches = sum(1 for keyword in engagement_keywords['low'] if keyword in content)
        if low_matches > 0:
            return 2

        return 3  # Default moderate score

    def _score_innovation(self, title: str, description: str) -> int:
        """Score freshness, innovation, and unique perspective (1-5)."""
        content = (title + " " + description).lower()

        innovation_keywords = {
            'high': ['future', 'emerging', 'breakthrough', 'revolutionary', 'pioneering', 'cutting-edge', 'novel'],
            'medium': ['new', 'modern', 'contemporary', 'recent', 'latest', 'advanced'],
            'traditional': ['traditional', 'classic', 'established', 'conventional']
        }

        high_matches = sum(1 for keyword in innovation_keywords['high'] if keyword in content)
        medium_matches = sum(1 for keyword in innovation_keywords['medium'] if keyword in content)
        traditional_matches = sum(1 for keyword in innovation_keywords['traditional'] if keyword in content)

        if high_matches >= 2:
            return 5
        elif high_matches >= 1:
            return 4
        elif medium_matches >= 2:
            return 3
        elif traditional_matches > 0:
            return 2
        else:
            return 3  # Default moderate

    def _get_recommendation(self, total_score: int) -> Dict:
        """Get Accept/Maybe/Reject recommendation based on total score."""
        if total_score >= 24:  # 80%+ (24-30 points)
            return {
                'decision': 'Accept',
                'reason': 'Excellent session that strongly meets all evaluation criteria.'
            }
        elif total_score >= 18:  # 60-79% (18-23 points)
            return {
                'decision': 'Maybe',
                'reason': 'Good session with potential. Consider requesting minor improvements or clarifications.'
            }
        else:  # <60% (6-17 points)
            return {
                'decision': 'Reject',
                'reason': 'Session does not meet minimum standards. Significant improvements needed.'
            }

    def _identify_strengths(self, scores: Dict) -> List[str]:
        """Identify strong areas (scores of 4-5)."""
        strengths = []
        for criterion, score in scores.items():
            if score >= 4:
                strengths.append(criterion)
        return strengths

    def _identify_improvements(self, scores: Dict) -> List[str]:
        """Identify areas needing improvement (scores of 1-2)."""
        improvements = []
        for criterion, score in scores.items():
            if score <= 2:
                improvements.append(criterion)
        return improvements

    def rank_submissions(self, evaluations: List[Dict]) -> List[Dict]:
        """
        Rank all submissions by total score for comparative analysis.
        Returns sorted list with rankings.
        """
        # Add ranking information
        sorted_evals = sorted(evaluations, key=lambda x: x.get('evaluation', {}).get('total_score', 0), reverse=True)

        for rank, eval_data in enumerate(sorted_evals, 1):
            eval_data['rank'] = rank

        return sorted_evals

    def set_event_configuration(self, theme: str, tracks: List[str]):
        """Set event theme and tracks for evaluation."""
        self.event_theme = theme
        self.event_tracks = tracks

    def process_speaker(self, file_path: str) -> Dict:
        """Process a single speaker packet file."""
        data = self.parse_speaker_file(file_path)

        # Generate missing content intelligently
        suggestions = self.generate_missing_content(data)

        # Use generated content to fill gaps
        session_title = data.get('session_title', '').strip()
        if 'session_titles' in suggestions and (
            not session_title or
            any(placeholder in session_title.lower() for placeholder in ['tbd', 'working title', 'placeholder', 'something cool', 'temp', '[working'])
        ):
            data['session_title'] = suggestions['session_titles'][0]  # Use first suggested title

        if 'session_description' in suggestions and not data.get('session_description', '').strip():
            data['session_description'] = suggestions['session_description']

        if 'enhanced_bio' in suggestions:
            data['bio'] = suggestions['enhanced_bio']

        # Create bio formats
        bio_formats = self.create_bio_formats(data['bio'], data['name'])

        # Create session content
        session_content = self.create_session_content(data['session_title'], data['session_description'])

        # Create alt text
        alt_text = self.create_alt_text(data['name'], data.get('headshot_file', ''))

        # Quality checks
        quality = self.quality_check(data, data['bio'])

        # Prepare tech requirements - use generated if missing/vague
        tech_requirements = data.get('tech_requirements', 'Not specified')
        if 'tech_requirements' in suggestions:
            tech_requirements = '; '.join(suggestions['tech_requirements'][:3])  # Use top 3

        # Add suggestions to output for reference
        suggestions_text = ""
        if suggestions:
            if 'session_titles' in suggestions and len(suggestions['session_titles']) > 1:
                suggestions_text += f"Alt Title: {suggestions['session_titles'][1]} | "
            if 'tech_requirements' in suggestions:
                suggestions_text += f"Suggested Tech: {'; '.join(suggestions['tech_requirements'][:2])} | "

        # Create base result
        result = {
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
            'Tech Requirements': tech_requirements,
            'Quality Flags': f"Headshot: {quality['headshot']} | Tech: {quality['tech']} | Session: {quality['session']} | Bio: {quality['bio_length']} | Issues: {quality['issues']}",
            'AI Suggestions': suggestions_text.rstrip(' | ') if suggestions_text else "None",
            'Generated Content': suggestions  # Store full suggestions for web interface
        }

        # Add evaluation if event theme/tracks are configured
        if self.event_theme or self.event_tracks:
            evaluation = self.evaluate_session({
                'bio': bio_formats['100_word'],
                'session_title': data['session_title'],
                'session_description': session_content['abstract'],
                'Key Takeaway 1': session_content['takeaways'][0]
            })

            # Add evaluation columns
            result['Eval: Relevance'] = evaluation['scores']['Relevance to Theme']
            result['Eval: Track Alignment'] = evaluation['scores']['Track Alignment']
            result['Eval: Credibility'] = evaluation['scores']['Speaker Credibility']
            result['Eval: Presentation'] = evaluation['scores']['Presentation Quality']
            result['Eval: Engagement'] = evaluation['scores']['Audience Engagement']
            result['Eval: Innovation'] = evaluation['scores']['Innovation Factor']
            result['Eval: Total Score'] = f"{evaluation['total_score']}/30 ({evaluation['percentage']}%)"
            result['Eval: Recommendation'] = evaluation['recommendation']
            result['Eval: Strengths'] = ', '.join(evaluation['strengths']) if evaluation['strengths'] else 'None identified'
            result['Eval: Improvements'] = ', '.join(evaluation['improvements']) if evaluation['improvements'] else 'None needed'
            result['evaluation'] = evaluation  # Store full evaluation for web interface

        return result

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

        # Generate filename with speaker names if multiple speakers
        if len(results) > 1:
            speaker_names = [self.clean_filename(result.get('Speaker Name', 'Unknown')) for result in results[:3]]
            if len(results) > 3:
                speaker_names.append('and_others')
            filename_base = f"speakers_{'_'.join(speaker_names)}"
        else:
            # Single speaker - use their name
            speaker_name = self.clean_filename(results[0].get('Speaker Name', 'Unknown'))
            filename_base = f"speaker_{speaker_name}"

        # Add timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if output_file == "processed_speakers.xlsx":  # Default filename
            output_file = f"outputs/{filename_base}_{timestamp}.xlsx"

        # Remove Generated Content and evaluation from Excel export (keep for web interface)
        export_results = []
        for result in results:
            export_result = {k: v for k, v in result.items() if k not in ['Generated Content', 'evaluation']}
            export_results.append(export_result)

        df = pd.DataFrame(export_results)

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