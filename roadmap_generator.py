from google import genai
import json
import random

# Initialize Gemini client
client = genai.Client(api_key="AIzaSyBfaCWHvuaPV9mhNmUgaeIB4VaIbdEjsuI")

# Load problems database
with open('problems_database.json', 'r') as f:
    PROBLEMS_DB = json.load(f)

def analyze_quiz_results(user_answers, quiz_questions):
    """
    Analyze quiz performance and return detailed stats
    """
    total_correct = 0
    difficulty_stats = {"Easy": {"correct": 0, "total": 0}, 
                        "Medium": {"correct": 0, "total": 0}, 
                        "Hard": {"correct": 0, "total": 0}}
    topic_stats = {}
    
    for i, q in enumerate(quiz_questions):
        is_correct = (user_answers[i] == q['correct_answer'])
        
        if is_correct:
            total_correct += 1
        
        # Track by difficulty
        diff = q['difficulty']
        difficulty_stats[diff]['total'] += 1
        if is_correct:
            difficulty_stats[diff]['correct'] += 1
        
        # Track by topic
        topic = q['topic']
        if topic not in topic_stats:
            topic_stats[topic] = {"correct": 0, "total": 0}
        topic_stats[topic]['total'] += 1
        if is_correct:
            topic_stats[topic]['correct'] += 1
    
    return {
        "total_score": total_correct,
        "total_questions": len(quiz_questions),
        "difficulty_stats": difficulty_stats,
        "topic_stats": topic_stats
    }

def build_roadmap_prompt(analysis):
    """
    Build Chain-of-Thought prompt for LLM based on quiz analysis
    """
    total = analysis['total_questions']
    score = analysis['total_score']
    percentage = (score / total) * 100
    
    # Format difficulty performance
    diff_text = ""
    for diff, stats in analysis['difficulty_stats'].items():
        if stats['total'] > 0:
            acc = (stats['correct'] / stats['total']) * 100
            diff_text += f"- {diff}: {stats['correct']}/{stats['total']} correct ({acc:.1f}%)\n"
    
    # Format topic performance
    topic_text = ""
    weak_topics = []
    medium_topics = []
    strong_topics = []
    
    for topic, stats in analysis['topic_stats'].items():
        acc = (stats['correct'] / stats['total']) * 100
        topic_text += f"- {topic}: {stats['correct']}/{stats['total']} correct ({acc:.1f}%)\n"
        
        if acc < 50:
            weak_topics.append(topic)
        elif acc >= 50 and acc <= 70:
            medium_topics.append(topic)
        else:
            strong_topics.append(topic)
    
    # Get available topics from database
    available_topics = list(PROBLEMS_DB.keys())
    topic_list = ", ".join(available_topics)
    
    prompt = f"""
You are an expert DSA mentor creating a personalized 8-week learning roadmap.

USER PERFORMANCE ANALYSIS:
=========================
Total Score: {score}/{total} ({percentage:.1f}%)

Difficulty Performance:
{diff_text}

Topic Performance:
{topic_text}

Weak Topics (< 50%): {', '.join(weak_topics) if weak_topics else 'None'}
Medium Topics (50-70%): {', '.join(medium_topics) if medium_topics else 'None'}
Strong Topics (> 70%): {', '.join(strong_topics) if strong_topics else 'None'}

AVAILABLE TOPICS (use ONLY these exact names):
{topic_list}

CHAIN-OF-THOUGHT REASONING PROCESS:
===================================
Think through this step-by-step:

STEP 1: IDENTIFY PRIORITY TOPICS
- Which 2-3 topics need the most focus? (weakest topics)
- Which topics should we introduce later? (medium topics)
- Which topics can have harder problems? (strong topics)

STEP 2: PLAN WEEK DISTRIBUTION
- Weeks 1-2: Focus ONLY on weakest topic with mostly Easy problems
- Weeks 3-4: Continue weak topics OR introduce medium topics
- Weeks 5-6: Mix of medium and weak topics with Medium problems
- Weeks 7-8: Strong topics OR new topics with Hard problems

STEP 3: DETERMINE DIFFICULTY PROGRESSION
For each topic, based on user's difficulty performance:
- If user scored < 50% on Easy: Give 80% Easy, 20% Medium
- If user scored 50-70% on Easy: Give 60% Easy, 30% Medium, 10% Hard
- If user scored > 70% on Easy: Give 30% Easy, 50% Medium, 20% Hard

STEP 4: GENERATE EXACTLY 8 WEEKS
Count as you go: Week 1, Week 2, ..., Week 8
Each week must have 5-8 problems total.

CRITICAL RULES:
==============
1. Generate EXACTLY 8 weeks - no more, no less
2. Use ONLY topics from this list: {topic_list}
3. Do NOT combine topics (WRONG: "Arrays and Strings", CORRECT: "Arrays")
4. Each week focuses on ONE topic only
5. Week numbers must be 1, 2, 3, 4, 5, 6, 7, 8

EXAMPLE OF GOOD OUTPUT:
{{
  "roadmap": [
    {{
      "week": 1,
      "topic": "Binary Tree",
      "total_problems": 7,
      "difficulty_split": {{"Easy": 5, "Medium": 2, "Hard": 0}},
      "focus": "Master basic traversals: inorder, preorder, postorder"
    }},
    {{
      "week": 2,
      "topic": "Binary Tree",
      "total_problems": 6,
      "difficulty_split": {{"Easy": 3, "Medium": 3, "Hard": 0}},
      "focus": "Tree properties: height, diameter, balanced trees"
    }},
    {{
      "week": 3,
      "topic": "Graph",
      "total_problems": 6,
      "difficulty_split": {{"Easy": 4, "Medium": 2, "Hard": 0}},
      "focus": "Graph basics: DFS and BFS traversal"
    }},
    {{
      "week": 4,
      "topic": "Graph",
      "total_problems": 7,
      "difficulty_split": {{"Easy": 2, "Medium": 4, "Hard": 1}},
      "focus": "Cycle detection and topological sort"
    }},
    {{
      "week": 5,
      "topic": "Dynamic Programming",
      "total_problems": 6,
      "difficulty_split": {{"Easy": 3, "Medium": 3, "Hard": 0}},
      "focus": "DP fundamentals: memoization and tabulation"
    }},
    {{
      "week": 6,
      "topic": "Dynamic Programming",
      "total_problems": 7,
      "difficulty_split": {{"Easy": 2, "Medium": 3, "Hard": 2}},
      "focus": "Classic DP patterns: knapsack, LCS, LIS"
    }},
    {{
      "week": 7,
      "topic": "Linked List",
      "total_problems": 6,
      "difficulty_split": {{"Easy": 2, "Medium": 3, "Hard": 1}},
      "focus": "Advanced linked list: reversal, cycle detection"
    }},
    {{
      "week": 8,
      "topic": "Stack and Queue",
      "total_problems": 7,
      "difficulty_split": {{"Easy": 2, "Medium": 4, "Hard": 1}},
      "focus": "Stack/Queue applications: monotonic stack, sliding window"
    }}
  ]
}}

NOW, FOLLOWING THE CHAIN-OF-THOUGHT PROCESS ABOVE:

First, think through steps 1-3 silently.

Then, generate your roadmap with EXACTLY 8 weeks.

Return ONLY valid JSON (no explanations, no markdown, no code blocks):
"""
    
    return prompt

def generate_roadmap(user_answers, quiz_questions):
    """
    Main function to generate personalized roadmap with retry logic
    """
    max_retries = 3
    attempt = 0
    
    while attempt < max_retries:
        try:
            attempt += 1
            print(f"\n{'='*50}")
            print(f"Attempt {attempt}/{max_retries}")
            print(f"{'='*50}")
            
            # Step 1: Analyze quiz results
            print("📊 Analyzing quiz performance...")
            analysis = analyze_quiz_results(user_answers, quiz_questions)
            
            # Step 2: Build prompt
            print("🤖 Building Chain-of-Thought prompt...")
            prompt = build_roadmap_prompt(analysis)
            
            # Step 3: Call LLM
            print("🔄 Generating roadmap with AI...")
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            # Step 4: Parse response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            llm_roadmap = json.loads(response_text)
            
            # VALIDATION: Check if we got exactly 8 weeks
            if 'roadmap' not in llm_roadmap:
                raise ValueError("LLM response missing 'roadmap' key")
            
            weeks_generated = len(llm_roadmap['roadmap'])
            print(f"📅 Weeks generated: {weeks_generated}")
            
            if weeks_generated == 8:
                # Success! We got exactly 8 weeks
                print("✅ Perfect! Got exactly 8 weeks.")
                
                # Step 5: Select actual problems from database
                print("📚 Selecting problems from database...")
                final_roadmap = select_problems_for_roadmap(llm_roadmap)
                
                print("✅ Roadmap generated successfully!")
                return {
                    "status": "success",
                    "analysis": analysis,
                    "roadmap": final_roadmap
                }
            else:
                # Didn't get 8 weeks, retry
                print(f"⚠️ Got {weeks_generated} weeks instead of 8. Retrying...")
                if attempt >= max_retries:
                    # Last attempt failed, return what we have
                    print("⚠️ Max retries reached. Returning partial roadmap.")
                    final_roadmap = select_problems_for_roadmap(llm_roadmap)
                    return {
                        "status": "success",
                        "analysis": analysis,
                        "roadmap": final_roadmap,
                        "warning": f"Generated {weeks_generated} weeks instead of 8"
                    }
                continue
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Response: {response_text[:200]}...")
            if attempt >= max_retries:
                return {"status": "error", "message": "Failed to parse LLM response after retries"}
            continue
            
        except Exception as e:
            print(f"❌ Error: {e}")
            if attempt >= max_retries:
                return {"status": "error", "message": str(e)}
            continue
    
    return {"status": "error", "message": "Failed to generate roadmap after all retries"}


def select_problems_for_roadmap(llm_roadmap):
    """
    Select actual problems from database based on LLM's roadmap
    """
    final_roadmap = []
    
    for week_plan in llm_roadmap['roadmap']:
        topic = week_plan['topic']
        difficulty_split = week_plan['difficulty_split']
        
        # Get all problems for this topic
        if topic not in PROBLEMS_DB:
            print(f"⚠️ Warning: Topic '{topic}' not found in database")
            continue
        
        topic_problems = PROBLEMS_DB[topic]['problems']
        learning_resources = PROBLEMS_DB[topic]['learning_resources']
        
        # Select problems by difficulty
        selected_problems = []
        
        for difficulty, count in difficulty_split.items():
            # Filter by difficulty
            available = [p for p in topic_problems if p['difficulty'] == difficulty]
            
            # Randomly select
            if len(available) >= count:
                chosen = random.sample(available, count)
            else:
                chosen = available  # Take all if not enough
            
            selected_problems.extend(chosen)
        
        # Build week data
        final_roadmap.append({
            "week": week_plan['week'],
            "topic": topic,
            "focus": week_plan['focus'],
            "total_problems": week_plan['total_problems'],
            "difficulty_split": difficulty_split,
            "learning_resources": learning_resources,
            "problems": selected_problems
        })
    
    return final_roadmap

# Test function
if __name__ == "__main__":
    # Example: Load quiz data and user answers
    print("This module should be imported by app.py")
    print("Test it through the API endpoint!")