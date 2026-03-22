from google import genai
import json

# Initialize Gemini client
client = genai.Client(api_key="AIzaSyBfaCWHvuaPV9mhNmUgaeIB4VaIbdEjsuI")

def generate_quiz_few_shot():
    """
    Generate 30 DSA MCQs using few-shot prompting
    """
    
    prompt = """
Generate exactly 30 Data Structures and Algorithms multiple choice questions.

Here are 5 EXAMPLES of the exact format I want:

EXAMPLE 1:
{
  "id": 1,
  "question": "What is the time complexity of binary search on a sorted array?",
  "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
  "correct_answer": "B",
  "difficulty": "Easy",
  "topic": "Binary Search"
}

EXAMPLE 2:
{
  "id": 2,
  "question": "In a max heap, which property must be satisfied?",
  "options": ["Parent node is smaller than children", "Parent node is greater than or equal to children", "All nodes are equal", "Left child is always greater than right child"],
  "correct_answer": "B",
  "difficulty": "Medium",
  "topic": "Heaps"
}

EXAMPLE 3:
{
  "id": 3,
  "question": "What is the worst-case time complexity of QuickSort?",
  "options": ["O(n log n)", "O(n²)", "O(n)", "O(log n)"],
  "correct_answer": "B",
  "difficulty": "Medium",
  "topic": "Sorting"
}

EXAMPLE 4:
{
  "id": 4,
  "question": "Which traversal of a Binary Tree visits nodes in the order: Left, Root, Right?",
  "options": ["Preorder", "Inorder", "Postorder", "Level Order"],
  "correct_answer": "B",
  "difficulty": "Easy",
  "topic": "Binary Tree"
}

EXAMPLE 5:
{
  "id": 5,
  "question": "What data structure is used to implement Dijkstra's shortest path algorithm efficiently?",
  "options": ["Stack", "Queue", "Priority Queue (Min Heap)", "Hash Table"],
  "correct_answer": "C",
  "difficulty": "Hard",
  "topic": "Graph"
}

Now generate 30 MORE questions in the EXACT SAME FORMAT.

REQUIREMENTS:
- Exactly 30 questions (ids 1-30)
- Difficulty distribution: 10 Easy, 12 Medium, 8 Hard
- Topics to cover: Arrays, Linked List, Binary Tree, Graph, Dynamic Programming, Stack and Queue, Binary Search, Heaps, Recursion, String
- Each question must have exactly 4 options
- Correct answer must be A, B, C, or D
- Questions should test DSA concepts, time complexity, or problem-solving approaches

Return ONLY valid JSON (no markdown, no code blocks, no extra text):
{
  "questions": [
    ... 30 questions here ...
  ]
}
"""
    
    try:
        print("🔄 Generating quiz using few-shot prompting...")
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        # Get the response text
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        # Parse JSON
        quiz_data = json.loads(response_text)
        
        # Validate we got 30 questions
        num_questions = len(quiz_data['questions'])
        if num_questions != 30:
            print(f"⚠️ Warning: Generated {num_questions} questions instead of 30")
        
        print(f"✅ Successfully generated {num_questions} questions!")
        
        return quiz_data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Response text: {response_text[:200]}...")
        return None
        
    except Exception as e:
        print(f"❌ Error generating quiz: {e}")
        return None


# For backwards compatibility, keep the old function name
def generate_quiz_zero_shot():
    """
    Wrapper function - now uses few-shot internally
    """
    return generate_quiz_few_shot()

def generate_topic_quiz(topic, num_questions=30):
    """
    Generate quiz focused on a specific topic using few-shot prompting
    """
    
    prompt = f"""
Generate exactly {num_questions} Data Structures and Algorithms questions focused ONLY on: {topic}

Here are 3 EXAMPLES of the exact format I want:

EXAMPLE 1:
{{
  "id": 1,
  "question": "What is the time complexity of binary search on a sorted array?",
  "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
  "correct_answer": "B",
  "difficulty": "Medium",
  "topic": "{topic}"
}}

EXAMPLE 2:
{{
  "id": 2,
  "question": "Which data structure is best suited for implementing a priority queue?",
  "options": ["Array", "Linked List", "Heap", "Stack"],
  "correct_answer": "C",
  "difficulty": "Medium",
  "topic": "{topic}"
}}

EXAMPLE 3:
{{
  "id": 3,
  "question": "What is the worst-case time complexity for insertion in a balanced BST?",
  "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
  "correct_answer": "B",
  "difficulty": "Hard",
  "topic": "{topic}"
}}

Now generate {num_questions} MORE questions ONLY about {topic} in the EXACT SAME FORMAT.

CRITICAL REQUIREMENTS:
- ALL questions must be about {topic} - no other topics allowed
- Difficulty distribution: 40% Medium, 40% Hard, 20% Easy (these should be challenging)
- Questions should test deeper understanding, not just basic concepts
- All questions MUST have topic: "{topic}"

Return ONLY valid JSON (no markdown, no code blocks):
{{
  "questions": [
    ... {num_questions} questions here ...
  ]
}}
"""
    
    try:
        print(f"🔄 Generating {num_questions}-question quiz for topic: {topic}...")
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        quiz_data = json.loads(response_text)
        
        print(f"✅ Successfully generated {len(quiz_data['questions'])} questions for {topic}!")
        
        return quiz_data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return None
        
    except Exception as e:
        print(f"❌ Error generating topic quiz: {e}")
        return None


# Test the function
if __name__ == "__main__":
    quiz = generate_quiz_zero_shot()
    
    if quiz:
        print("\n📊 Quiz Preview:")
        print(f"Total questions: {len(quiz['questions'])}")
        print("\nFirst question:")
        print(json.dumps(quiz['questions'][0], indent=2))