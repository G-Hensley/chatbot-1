"""
Dataset Management Utilities for Portfolio Chatbot
This script helps you create, manage, and expand your portfolio chatbot dataset.
"""

import json
import random
from typing import List, Dict, Any

class PortfolioDatasetManager:
    def __init__(self, dataset_path: str = "portfolio_dataset.json"):
        self.dataset_path = dataset_path
        self.data = self.load_dataset()
    
    def load_dataset(self) -> Dict[str, Any]:
        """Load the dataset from JSON file."""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"conversations": []}
    
    def save_dataset(self):
        """Save the dataset to JSON file."""
        with open(self.dataset_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def add_conversation(self, category: str, input_text: str, output_text: str):
        """Add a new conversation to the dataset."""
        conversation = {
            "category": category,
            "input": input_text,
            "output": output_text
        }
        self.data["conversations"].append(conversation)
    
    def get_conversations_by_category(self, category: str) -> List[Dict[str, str]]:
        """Get all conversations for a specific category."""
        return [conv for conv in self.data["conversations"] if conv.get("category") == category]
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories in the dataset."""
        categories = set()
        for conv in self.data["conversations"]:
            if "category" in conv:
                categories.add(conv["category"])
        return sorted(list(categories))
    
    def generate_variations(self, base_input: str, variations: List[str]) -> List[str]:
        """Generate input variations for the same response."""
        return [base_input] + variations
    
    def export_for_training(self, output_path: str = "training_data.json"):
        """Export data in format suitable for training."""
        training_data = []
        for conv in self.data["conversations"]:
            training_data.append({
                "text": f"Human: {conv['input']}\nAssistant: {conv['output']}"
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> Dict[str, int]:
        """Get dataset statistics."""
        stats = {
            "total_conversations": len(self.data["conversations"]),
            "categories": len(self.get_all_categories())
        }
        
        # Count conversations per category
        for category in self.get_all_categories():
            stats[f"conversations_in_{category}"] = len(self.get_conversations_by_category(category))
        
        return stats

def create_sample_portfolio_data():
    """Create sample portfolio data with placeholders."""
    manager = PortfolioDatasetManager()
    
    # Add more conversation examples
    sample_conversations = [
        ("introduction", "What's your background?", "I'm [Wife's Name], a [profession] with a passion for [area of interest]. I've been working in this field for [X] years and love helping [target audience] achieve [specific goals]."),
        ("introduction", "Tell me about your journey", "My journey started [time period] when I [initial experience]. Since then, I've [career progression] and now specialize in [current focus area]."),
        ("skills", "What tools do you use?", "I'm proficient in [tool 1], [tool 2], and [tool 3]. I also have experience with [additional tools] and stay updated with the latest industry technologies."),
        ("portfolio", "What's your best project?", "One of my favorite projects was [project name] where I [what you did]. It was challenging because [challenge] but the result was [positive outcome] for the client."),
        ("process", "How long do projects typically take?", "Project timelines vary based on scope, but typically [timeframe] for [project type] and [different timeframe] for [different project type]. I always provide realistic timelines during our initial consultation."),
        ("collaboration", "Do you work with teams?", "Absolutely! I enjoy collaborating with [types of team members] and have experience working in both [work environment 1] and [work environment 2] settings."),
        ("future", "What are your goals?", "I'm excited about [future goal] and continuing to [growth area]. I'm also interested in [new area of interest] and how it can benefit my clients."),
    ]
    
    for category, input_text, output_text in sample_conversations:
        manager.add_conversation(category, input_text, output_text)
    
    manager.save_dataset()
    return manager

if __name__ == "__main__":
    # Example usage
    manager = create_sample_portfolio_data()
    
    print("Dataset Statistics:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\nCategories: {manager.get_all_categories()}")
    
    # Export for training
    manager.export_for_training()
    print("\nTraining data exported to 'training_data.json'")
