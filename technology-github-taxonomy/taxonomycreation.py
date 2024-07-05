import csv
import json

class SkillEntity:
    def __init__(self, name):
        self.Name = name
        self.childSkillEntities = []

    def to_dict(self, visited=None):
        if visited is None:
            visited = set()
        if self in visited:
            # If this node has been visited before, return its name only to break the recursion
            return {"Name": self.Name}
        visited.add(self)
        # Serialize child entities while avoiding circular references
        child_entities = [child.to_dict(visited) for child in self.childSkillEntities]
        return {
            "Name": self.Name,
            "childSkillEntities": child_entities
        }

def process_topic_csv(file_path):
    unique_names = set()

    # Reading the CSV file and storing topicName and repositoryName in newData
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        for row in csv_reader:
            topicName = row['name'].strip().lower()  # Normalize name
            unique_names.add(topicName)

    return unique_names

def process_repo_csv(file_path):
    repoData = []

    # Reading the CSV file and storing topicName and repositoryName in newData
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        for row in csv_reader:
            topicName = row['topicName'].strip().lower()  # Normalize topicName
            repositoryName = row['repositoryName'].strip().lower()  # Normalize repositoryName
            repoData.append((topicName, repositoryName))

    return repoData

def mainFlow(file_path, topics_filepath):
    topic_unique_names = process_topic_csv(topics_filepath)
    repoData = process_repo_csv(file_path)
    # Creating SkillEntity objects based on unique_names set
    hashEntities = {name: SkillEntity(name) for name in topic_unique_names}

    # Building the hierarchy based on newData
    for topicName, repositoryName in repoData:
        if topicName == repositoryName:
            continue
        
        if topicName in hashEntities and repositoryName in hashEntities:
            topic_entity = hashEntities[topicName]
            repo_entity = hashEntities[repositoryName]

            # Link repo_entity as a child of topic_entity only if it's not already linked
            if repo_entity not in topic_entity.childSkillEntities:
                topic_entity.childSkillEntities.append(repo_entity)
        else:
            print(f"*** {topicName} and/or {repositoryName} are/is not a topic\n")

    # Finding top-level entities (entities without any parent)
    top_level_entities = []
    for name in topic_unique_names:
        entity = hashEntities[name]
        if not any(entity in e.childSkillEntities for e in hashEntities.values()):
            top_level_entities.append(entity)

    return top_level_entities

# Usage example
file_path = 'github-topics-repositories.csv'
topics_filepath = 'github-topics.csv'
top_level_entities = mainFlow(file_path, topics_filepath)

# Convert the top-level entities to a JSON-compatible dictionary
SkillData = [entity.to_dict() for entity in top_level_entities]

# Save to a JSON file
with open('SkillData.json', 'w', encoding='utf-8') as json_file:
    json.dump(SkillData, json_file, indent=4)

print("*** END")
