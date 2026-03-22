import json

# Load all three data files
with open('data_a.json', 'r') as f:
    data_a = json.load(f)

with open('data_b.json', 'r') as f:
    data_b = json.load(f)

with open('data_c.json', 'r') as f:
    data_c = json.load(f)

with open('learning_resources.json', 'r') as f:
    learning_resources = json.load(f)

# Merge all problem data
all_problems = {}
all_problems.update(data_a)
all_problems.update(data_b)
all_problems.update(data_c)

# Add learning resources to each topic
final_data = {}
for topic, problems in all_problems.items():
    final_data[topic] = {
        "learning_resources": learning_resources.get(topic, []),
        "problems": problems
    }

# Save merged data
with open('problems_database.json', 'w') as f:
    json.dump(final_data, f, indent=2)

print("✅ Successfully merged all data!")
print(f"Total topics: {len(final_data)}")

# Count total problems
total_problems = sum(len(topic_data['problems']) for topic_data in final_data.values())
print(f"Total problems: {total_problems}")

# Show topic breakdown
print("\nTopic breakdown:")
for topic, data in final_data.items():
    print(f"  {topic}: {len(data['problems'])} problems")