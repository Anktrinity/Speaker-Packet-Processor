#!/usr/bin/env python3
"""
Test script for the Session Evaluation System
"""

from speaker_packet_processor import SpeakerPacketProcessor

def test_evaluation_system():
    """Test the evaluation system with sample data."""

    print("=" * 60)
    print("🎯 SESSION EVALUATION SYSTEM TEST")
    print("=" * 60)

    # Configure event settings
    event_theme = "AI, Automation and Innovation for Event Professionals"
    event_tracks = [
        "Artificial Intelligence",
        "Event Technology",
        "Audience Engagement",
        "Digital Transformation"
    ]

    print(f"\n📋 Event Configuration:")
    print(f"   Theme: {event_theme}")
    print(f"   Tracks: {', '.join(event_tracks)}")

    # Initialize processor with event configuration
    processor = SpeakerPacketProcessor(event_theme=event_theme, event_tracks=event_tracks)

    # Test sample speakers
    sample_speakers = [
        {
            'name': 'Dr. Sarah AI Expert',
            'bio': 'Dr. Sarah is a PhD in Artificial Intelligence and founder of AI Events Inc. She has published 15 research papers on machine learning applications in event technology and is an award-winning speaker with 10 years of experience.',
            'session_title': 'AI-Powered Event Innovation: Practical Applications for 2025',
            'session_description': "In this interactive workshop, you'll learn how to implement AI solutions in your events. Discover practical strategies for automating attendee engagement, personalizing event experiences, and measuring ROI with machine learning tools."
        },
        {
            'name': 'John Basic Speaker',
            'bio': 'John works in events.',
            'session_title': 'Introduction to Event Management',
            'session_description': 'An overview of basic event planning concepts.'
        },
        {
            'name': 'Maria Innovation Leader',
            'bio': 'Maria is a senior director of event innovation with 15 years of experience in digital transformation. She has led groundbreaking projects for Fortune 500 companies and specializes in emerging technologies.',
            'session_title': 'Future of Audience Engagement: Immersive Technologies and AI',
            'session_description': "This hands-on session will teach you how to implement cutting-edge engagement strategies. You'll learn practical techniques for using AR, VR, and AI to create unforgettable attendee experiences with live demonstrations and case studies."
        }
    ]

    print("\n" + "=" * 60)
    print("📊 EVALUATION RESULTS")
    print("=" * 60)

    results = []
    for speaker in sample_speakers:
        print(f"\n🎤 Speaker: {speaker['name']}")
        print(f"   Session: {speaker['session_title']}")
        print("-" * 60)

        # Evaluate the session
        evaluation = processor.evaluate_session(speaker)

        # Display scores
        print(f"\n   📈 Individual Scores (1-5):")
        for criterion, score in evaluation['scores'].items():
            stars = "★" * score + "☆" * (5 - score)
            print(f"      {criterion:.<30} {score} {stars}")

        print(f"\n   🎯 Total Score: {evaluation['total_score']}/30 ({evaluation['percentage']}%)")
        print(f"   📋 Recommendation: {evaluation['recommendation']}")
        print(f"   💡 Reason: {evaluation['recommendation_reason']}")

        if evaluation['strengths']:
            print(f"   ✅ Strengths: {', '.join(evaluation['strengths'])}")

        if evaluation['improvements']:
            print(f"   ⚠️  Needs Improvement: {', '.join(evaluation['improvements'])}")

        # Store for ranking
        results.append({
            'speaker': speaker['name'],
            'session': speaker['session_title'],
            'evaluation': evaluation
        })

    # Rank all submissions
    print("\n" + "=" * 60)
    print("🏆 COMPARATIVE RANKING")
    print("=" * 60)

    ranked = processor.rank_submissions(results)

    for rank, item in enumerate(ranked, 1):
        eval_data = item['evaluation']
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"\n{medal} Rank {rank}: {item['speaker']}")
        print(f"   Score: {eval_data['total_score']}/30 ({eval_data['percentage']}%)")
        print(f"   Decision: {eval_data['recommendation']}")
        print(f"   Session: {item['session'][:60]}...")

    print("\n" + "=" * 60)
    print("✅ Evaluation System Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_evaluation_system()
