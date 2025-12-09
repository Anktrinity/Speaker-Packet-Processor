# Speaker Packet Processor v3.0 - Product Requirements

## Overview
Transform messy speaker packets into professional content AND evaluate session submissions with AI-powered scoring.

---

## Core Module 1: Content Standardization (Existing)

### Input
- Speaker bios (any format)
- Headshots
- Session descriptions
- Tech requirements

### Output
- 3 bio formats (50/100 words, 1-sentence)
- Professional session abstracts
- LinkedIn posts (4 types)
- Quality control reports
- Excel exports

---

## Core Module 2: Session Evaluation System (NEW)

### Purpose
Help event organizers objectively evaluate and score session proposals to make data-driven programming decisions.

### Evaluation Criteria (Scored 1-10)

#### 1. **Theme Relevance** (Weight: 20%)
- How well does the session align with the event's main theme?
- Does it address the event's core focus areas?
- Is it appropriate for the target audience?

**Scoring Guide:**
- 9-10: Perfectly aligned, directly addresses theme
- 7-8: Strong alignment, relevant to theme
- 5-6: Moderate alignment, tangentially related
- 3-4: Weak alignment, loosely connected
- 1-2: Poor alignment, off-theme

#### 2. **Track/Goal Alignment** (Weight: 15%)
- Does the session fit within designated event tracks?
- Does it support the event's stated goals/objectives?
- Is it positioned correctly within the program structure?

**Scoring Guide:**
- 9-10: Perfect track fit, supports multiple goals
- 7-8: Clear track fit, supports key goals
- 5-6: Fits track but goals unclear
- 3-4: Unclear track fit
- 1-2: Doesn't fit any track

#### 3. **Speaker Credibility** (Weight: 25%)
- What are the speaker's qualifications and expertise?
- Do they have relevant industry experience?
- What is their track record (publications, speaking history)?
- Any past attendee feedback or ratings?

**Scoring Guide:**
- 9-10: Industry expert, proven track record, excellent feedback
- 7-8: Strong credentials, relevant experience, good feedback
- 5-6: Moderate credentials, some experience
- 3-4: Limited credentials, unclear experience
- 1-2: Insufficient credentials, no evidence of expertise

#### 4. **Attendee Appeal** (Weight: 20%)
- Is this topic likely to draw attendees based on the event theme?
- Does it address real pain points or interests?
- Is the presentation format engaging?
- Will it generate buzz/discussion?

**Scoring Guide:**
- 9-10: High demand topic, highly engaging format
- 7-8: Strong appeal, solid engagement potential
- 5-6: Moderate interest, standard format
- 3-4: Limited appeal, passive format
- 1-2: Low interest, boring format

#### 5. **Innovation & Uniqueness** (Weight: 20%)
- Is the topic fresh and innovative?
- Does it provide a unique perspective or approach?
- Is it differentiated from other sessions?
- Does it challenge conventional thinking?

**Scoring Guide:**
- 9-10: Groundbreaking, never-seen-before perspective
- 7-8: Fresh angle, innovative approach
- 5-6: Some new insights, mostly familiar
- 3-4: Repetitive, seen-it-before
- 1-2: Completely generic, no differentiation

---

## Evaluation Outputs

### 1. **Session Score Card**
```
Session Title: [Title]
Speaker: [Name]
Overall Score: 8.2/10 (Top 15%)

Detailed Scores:
├─ Theme Relevance: 9/10 (Weight: 20%) = 1.8 points
├─ Track Alignment: 8/10 (Weight: 15%) = 1.2 points
├─ Speaker Credibility: 9/10 (Weight: 25%) = 2.25 points
├─ Attendee Appeal: 7/10 (Weight: 20%) = 1.4 points
└─ Innovation: 8/10 (Weight: 20%) = 1.6 points

Recommendation: ✅ ACCEPT - Strong candidate
```

### 2. **Comparative Ranking**
- Rank all sessions by overall score
- Identify top performers by category
- Flag sessions that need improvement
- Suggest alternate tracks if misaligned

### 3. **AI-Generated Feedback**
- Strengths of the proposal
- Areas for improvement
- Specific recommendations
- Alternative positioning suggestions

### 4. **Programming Insights**
- Track balance analysis
- Topic diversity assessment
- Speaker lineup quality
- Attendee interest heatmap

---

## Integration with Existing System

### Workflow Option 1: Sequential Processing
1. Process speaker packet (content standardization)
2. Generate session score card
3. Output combined report (content + evaluation)

### Workflow Option 2: Standalone Evaluation
1. Upload session proposals (without full speaker packets)
2. Evaluate sessions independently
3. Generate rankings and recommendations

### Workflow Option 3: Batch Evaluation
1. Upload multiple session proposals
2. Evaluate and rank all sessions
3. Generate comparative analysis
4. Export selection recommendations

---

## User Interface Updates

### New Features to Add:

#### 1. **Evaluation Mode Toggle**
```
[ Content Processing ] [ Session Evaluation ] [ Both ]
```

#### 2. **Event Configuration Panel**
```
Event Theme: [AI & Innovation in Events]
Event Tracks: [Technology, Design, Marketing, Leadership]
Event Goals: [Education, Networking, Innovation]
Target Audience: [Event professionals, 5-15 years experience]
```

#### 3. **Scoring Criteria Customization**
Allow organizers to adjust weights:
```
Theme Relevance: [20%] ████████░░
Track Alignment: [15%] ██████░░░░
Speaker Credibility: [25%] ██████████
Attendee Appeal: [20%] ████████░░
Innovation: [20%] ████████░░
```

#### 4. **Results Dashboard**
- **Top Sessions**: List highest-scoring submissions
- **Category Leaders**: Best by each criterion
- **Red Flags**: Sessions that need review
- **Track Balance**: Visual distribution across tracks

---

## Excel Export Enhancement

### New Sheets:

#### Sheet 1: Session Scores
| Session Title | Speaker | Overall Score | Theme | Track | Credibility | Appeal | Innovation | Recommendation |
|--------------|---------|---------------|-------|-------|-------------|--------|-----------|----------------|
| ... | ... | 8.2/10 | 9/10 | 8/10 | 9/10 | 7/10 | 8/10 | ✅ Accept |

#### Sheet 2: Detailed Feedback
| Session Title | Strengths | Improvements | Recommendations |
|--------------|-----------|--------------|-----------------|
| ... | • Highly relevant<br>• Expert speaker | • Could add more examples | Position in keynote track |

#### Sheet 3: Comparative Rankings
| Rank | Session Title | Score | Percentile |
|------|---------------|-------|------------|
| 1 | Session A | 9.2 | Top 5% |
| 2 | Session B | 8.8 | Top 10% |

#### Sheet 4: Programming Insights
- Track distribution
- Topic diversity score
- Speaker lineup quality
- Recommended accepts/rejects

---

## Technical Implementation

### New Python Module: `session_evaluator.py`

Key functions:
```python
class SessionEvaluator:
    def evaluate_theme_relevance(session, event_config)
    def evaluate_track_alignment(session, event_config)
    def evaluate_speaker_credibility(speaker_bio, speaker_history)
    def evaluate_attendee_appeal(session, event_theme)
    def evaluate_innovation(session, existing_sessions)
    def calculate_weighted_score(scores, weights)
    def generate_recommendations(score, feedback)
    def rank_sessions(sessions_list)
```

### Claude API Integration
- Use Claude to analyze qualitative aspects
- Generate natural language feedback
- Identify patterns and insights
- Suggest improvements

---

## Use Cases

### Use Case 1: Conference Call for Proposals
1. Receive 200+ session submissions
2. Upload all to Speaker Packet Processor
3. Get ranked list with scores
4. Review top 30% for acceptance
5. Flag bottom 20% for rejection
6. Middle 50% get detailed feedback for revision

### Use Case 2: Curating Existing Content
1. Upload current speaker lineup
2. Evaluate for balance and quality
3. Identify gaps in programming
4. Find opportunities for improvement
5. Reposition sessions to better tracks

### Use Case 3: Feedback to Speakers
1. Evaluate rejected proposals
2. Generate constructive feedback
3. Provide specific improvement suggestions
4. Encourage resubmission for future events

---

## Success Metrics

- **Time Savings**: Reduce evaluation time from 10 min/session to 2 min/session
- **Objectivity**: Eliminate subjective bias with standardized scoring
- **Quality**: Increase attendee satisfaction with better programming
- **Transparency**: Provide clear rationale for acceptance/rejection
- **Efficiency**: Enable data-driven programming decisions

---

## Future Enhancements (v3.1+)

1. **Machine Learning**: Learn from past event success data
2. **Conflict Detection**: Identify competing/duplicate sessions
3. **Schedule Optimization**: Suggest optimal session timing
4. **Speaker Diversity**: Track diversity metrics
5. **Historical Comparison**: Compare to past events
6. **Attendee Matching**: Predict which attendees would be interested

---

## Implementation Priority

### Phase 1 (MVP): Core Evaluation
- ✅ Basic scoring for 5 criteria
- ✅ Weighted score calculation
- ✅ Simple recommendations
- ✅ Excel export with scores

### Phase 2: Advanced Features
- Event configuration panel
- Customizable weights
- Comparative rankings
- Detailed feedback generation

### Phase 3: Intelligence Layer
- Pattern detection
- Programming insights
- Track balance analysis
- AI-generated recommendations

---

**Status**: Ready for development
**Target**: v3.0 Release
**Impact**: Transform from content processor to comprehensive speaker/session management platform
