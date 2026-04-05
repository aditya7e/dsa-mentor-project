from google import genai
import json
import random

# Initialize Gemini client
client = genai.Client(api_key="//")

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
    Respects topic hierarchy: Basic → Intermediate → Advanced
    Adjusts difficulty based on user's performance in each topic
    """
    total = analysis['total_questions']
    score = analysis['total_score']
    percentage = (score / total) * 100
    
    # Topic categorization by learning level
    BASIC_TOPICS = ['Arrays', 'String', 'Linked List', 'Stack and Queue', 'Recursion']
    INTERMEDIATE_TOPICS = ['Binary Search', 'Binary Tree', 'Binary Search Tree', 'Heaps', 'Greedy']
    ADVANCED_TOPICS = ['Graph', 'Dynamic Programming', 'Trie']
    
    # Format difficulty performance
    diff_text = ""
    for diff, stats in analysis['difficulty_stats'].items():
        if stats['total'] > 0:
            acc = (stats['correct'] / stats['total']) * 100
            diff_text += f"- {diff}: {stats['correct']}/{stats['total']} correct ({acc:.1f}%)\n"
    
    # Categorize topics by performance AND level
    basic_weak = []
    basic_medium = []
    basic_strong = []
    
    intermediate_weak = []
    intermediate_medium = []
    intermediate_strong = []
    
    advanced_weak = []
    advanced_medium = []
    advanced_strong = []
    
    for topic, stats in analysis['topic_stats'].items():
        acc = (stats['correct'] / stats['total']) * 100
        
        # Categorize by level and performance
        if topic in BASIC_TOPICS:
            if acc < 50:
                basic_weak.append(f"{topic} ({acc:.0f}%)")
            elif acc <= 70:
                basic_medium.append(f"{topic} ({acc:.0f}%)")
            else:
                basic_strong.append(f"{topic} ({acc:.0f}%)")
        
        elif topic in INTERMEDIATE_TOPICS:
            if acc < 50:
                intermediate_weak.append(f"{topic} ({acc:.0f}%)")
            elif acc <= 70:
                intermediate_medium.append(f"{topic} ({acc:.0f}%)")
            else:
                intermediate_strong.append(f"{topic} ({acc:.0f}%)")
        
        elif topic in ADVANCED_TOPICS:
            if acc < 50:
                advanced_weak.append(f"{topic} ({acc:.0f}%)")
            elif acc <= 70:
                advanced_medium.append(f"{topic} ({acc:.0f}%)")
            else:
                advanced_strong.append(f"{topic} ({acc:.0f}%)")
    
    # Calculate overall performance in each level
    def calc_level_performance(topic_list, all_topics):
        if not all_topics:
            return 100  # If not tested, assume mastery
        total_correct = 0
        total_questions = 0
        for topic_entry in all_topics:
            topic_name = topic_entry.split('(')[0].strip()
            if topic_name in analysis['topic_stats']:
                total_correct += analysis['topic_stats'][topic_name]['correct']
                total_questions += analysis['topic_stats'][topic_name]['total']
        return (total_correct / total_questions * 100) if total_questions > 0 else 100
    
    all_basic = basic_weak + basic_medium + basic_strong
    all_intermediate = intermediate_weak + intermediate_medium + intermediate_strong
    
    basic_performance = calc_level_performance(BASIC_TOPICS, all_basic)
    intermediate_performance = calc_level_performance(INTERMEDIATE_TOPICS, all_intermediate)
    
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

TOPIC PERFORMANCE BY LEARNING LEVEL:
====================================

BASIC TOPICS (Foundation - Learn First):
- Weak (< 50%): {', '.join(basic_weak) if basic_weak else 'None'}
- Medium (50-70%): {', '.join(basic_medium) if basic_medium else 'None'}
- Strong (> 70%): {', '.join(basic_strong) if basic_strong else 'None'}
- Overall Basic Performance: {basic_performance:.0f}%

INTERMEDIATE TOPICS (Need Basic Foundation):
- Weak (< 50%): {', '.join(intermediate_weak) if intermediate_weak else 'None'}
- Medium (50-70%): {', '.join(intermediate_medium) if intermediate_medium else 'None'}
- Strong (> 70%): {', '.join(intermediate_strong) if intermediate_strong else 'None'}
- Overall Intermediate Performance: {intermediate_performance:.0f}%

ADVANCED TOPICS (Need Strong Foundation):
- Weak (< 50%): {', '.join(advanced_weak) if advanced_weak else 'None'}
- Medium (50-70%): {', '.join(advanced_medium) if advanced_medium else 'None'}
- Strong (> 70%): {', '.join(advanced_strong) if advanced_strong else 'None'}

AVAILABLE TOPICS (use ONLY these exact names):
{topic_list}

TOPIC HIERARCHY (MUST FOLLOW):
==============================
BASIC: Arrays, String, Linked List, Stack and Queue, Recursion
INTERMEDIATE: Binary Search, Binary Tree, Binary Search Tree, Heaps, Greedy
ADVANCED: Graph, Dynamic Programming, Trie

CHAIN-OF-THOUGHT REASONING PROCESS:
===================================

STEP 1: DETERMINE STARTING LEVEL
- If Basic Performance < 70%: START with Basic topics ONLY (weeks 1-4)
- If Basic Performance ≥ 70% AND Intermediate < 70%: START with Intermediate topics
- If both Basic AND Intermediate ≥ 70%: Can include Advanced topics

STEP 2: PRIORITIZE WITHIN EACH LEVEL
- Focus on weakest topics within the appropriate level
- Example: If user weak in Arrays (40%) and Graph (0%), prioritize Arrays first (it's basic)
- NEVER jump to Advanced topics if Basic topics are weak

STEP 3: PLAN PROGRESSION
- Weeks 1-3: Weakest BASIC topics (if any weak basic topics exist)
- Weeks 4-5: Medium BASIC topics OR start INTERMEDIATE (if basics are strong)
- Weeks 6-7: INTERMEDIATE topics (if basics mastered)
- Week 8: ADVANCED topics (ONLY if both basic and intermediate are strong)

STEP 4: DIFFICULTY DISTRIBUTION (Based on user's performance in that specific topic)

FOR BASIC TOPICS (Arrays, String, Linked List, Stack and Queue, Recursion):
- If user WEAK (< 50%): 70% Easy, 30% Medium, 0% Hard
- If user MEDIUM (50-70%): 30% Easy, 60% Medium, 10% Hard
- If user STRONG (> 70%): 0% Easy, 50% Medium, 50% Hard

FOR INTERMEDIATE TOPICS (Binary Search, Binary Tree, BST, Heaps, Greedy):
- If user WEAK (< 50%): 60% Easy, 40% Medium, 0% Hard
- If user MEDIUM (50-70%): 20% Easy, 70% Medium, 10% Hard
- If user STRONG (> 70%): 0% Easy, 40% Medium, 60% Hard

FOR ADVANCED TOPICS (Graph, Dynamic Programming, Trie):
- If user WEAK (< 50%): 50% Easy, 50% Medium, 0% Hard
- If user MEDIUM (50-70%): 10% Easy, 60% Medium, 30% Hard
- If user STRONG (> 70%): 0% Easy, 30% Medium, 70% Hard

CRITICAL: Match difficulty to user's ACTUAL performance in that specific topic.
Example: If user scored 65% in Arrays (MEDIUM), give 30% Easy, 60% Medium, 10% Hard.
Example: If user scored 85% in Binary Tree (STRONG), give 0% Easy, 40% Medium, 60% Hard.
Example: If user scored 35% in Linked List (WEAK), give 70% Easy, 30% Medium, 0% Hard.

CRITICAL RULES:
==============
1. Generate EXACTLY 8 weeks - no more, no less
2. RESPECT TOPIC HIERARCHY - Never suggest Graph/DP if user weak in Arrays/Linked List
3. Use ONLY topics from this list: {topic_list}
4. Do NOT combine topics (WRONG: "Arrays and Strings", CORRECT: "Arrays")
5. Each week focuses on ONE topic only
6. Week numbers must be 1, 2, 3, 4, 5, 6, 7, 8
7. ADJUST DIFFICULTY based on user's performance in that specific topic

EXAMPLE SCENARIOS:

SCENARIO A: User weak in basics (Arrays 40%, Binary Tree 30%, Graph 0%)
CORRECT roadmap: Start with Arrays (weeks 1-2), then other basics, NO Graph until week 7-8
WRONG roadmap: Starting with Graph because 0% score

SCENARIO B: User strong in basics (Arrays 85%, Linked List 90%), weak in intermediate
CORRECT: Focus on intermediate topics (Binary Tree, BST, Heaps)
WRONG: Spending weeks on Arrays when already mastered

SCENARIO C: User medium in Arrays (65%)
CORRECT difficulty: 30% Easy, 60% Medium, 10% Hard (challenge them!)
WRONG difficulty: 70% Easy, 30% Medium (too basic for their level)

EXAMPLE OF GOOD OUTPUT (for a user who is MEDIUM in Arrays 65%, WEAK in Binary Tree 35%):
{{
  "roadmap": [
    {{
      "week": 1,
      "topic": "Arrays",
      "total_problems": 7,
      "difficulty_split": {{"Easy": 2, "Medium": 4, "Hard": 1}},
      "focus": "Advanced array techniques: sliding window, two pointers (user already has basics)"
    }},
    {{
      "week": 2,
      "topic": "Arrays",
      "total_problems": 6,
      "difficulty_split": {{"Easy": 2, "Medium": 3, "Hard": 1}},
      "focus": "Complex array problems: prefix sum, binary search on arrays"
    }},
    {{
      "week": 3,
      "topic": "Binary Tree",
      "total_problems": 7,
      "difficulty_split": {{"Easy": 4, "Medium": 3, "Hard": 0}},
      "focus": "Tree traversal fundamentals (user is weak, start with easier problems)"
    }},
    {{
      "week": 4,
      "topic": "Binary Tree",
      "total_problems": 6,
      "difficulty_split": {{"Easy": 4, "Medium": 2, "Hard": 0}},
      "focus": "Tree properties and basic recursion"
    }},
    {{
      "week": 5,
      "topic": "Linked List",
      "total_problems": 6,
      "difficulty_split": {{"Easy": 4, "Medium": 2, "Hard": 0}},
      "focus": "Linked list basics and reversal"
    }},
    {{
      "week": 6,
      "topic": "Stack and Queue",
      "total_problems": 7,
      "difficulty_split": {{"Easy": 3, "Medium": 3, "Hard": 1}},
      "focus": "Stack/Queue applications"
    }},
    {{
      "week": 7,
      "topic": "Binary Search Tree",
      "total_problems": 6,
      "difficulty_split": {{"Easy": 3, "Medium": 3, "Hard": 0}},
      "focus": "BST operations and validation"
    }},
    {{
      "week": 8,
      "topic": "Heaps",
      "total_problems": 7,
      "difficulty_split": {{"Easy": 2, "Medium": 4, "Hard": 1}},
      "focus": "Priority queue and heap applications"
    }}
  ]
}}

NOTICE: 
- Arrays gets harder problems (2 Easy, 4 Medium, 1 Hard) because user is MEDIUM (65%).
- Binary Tree gets easier problems (4 Easy, 3 Medium) because user is WEAK (35%).
- This respects both topic hierarchy AND user's actual performance level.

BEFORE GENERATING EACH WEEK:
1. Check user's performance in that specific topic from the analysis above
2. Classify as WEAK (< 50%), MEDIUM (50-70%), or STRONG (> 70%)
3. Identify if topic is BASIC/INTERMEDIATE/ADVANCED
4. Apply the appropriate difficulty distribution from STEP 4
5. Adjust problem count to match the difficulty split

DOUBLE CHECK: 
- If user scored 60% in a topic, they should NOT get 70% Easy problems!
- If user scored 85% in a topic, they should get 0% Easy problems!
- Respect the topic hierarchy - basics before advanced!

NOW, FOLLOWING THE CHAIN-OF-THOUGHT PROCESS ABOVE:

First, analyze the user's performance level (Basic/Intermediate/Advanced).
Then, think through which level to start from.
For each week, check the user's score in that topic and apply correct difficulty.
Finally, generate your roadmap with EXACTLY 8 weeks, respecting both topic hierarchy AND difficulty appropriateness.

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