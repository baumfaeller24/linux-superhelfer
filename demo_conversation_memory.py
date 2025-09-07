#!/usr/bin/env python3
"""
Demo script for conversation memory system
Shows basic functionality of storing and retrieving conversations
"""

from modules.conversation_memory.models import ConversationEntry, Session
from modules.conversation_memory.storage import ConversationStorage
from datetime import datetime
import time

def demo_conversation_memory():
    """Demonstrate conversation memory functionality"""
    print("🧠 Conversation Memory System Demo")
    print("=" * 50)
    
    # Initialize storage
    storage = ConversationStorage("demo_conversation_data")
    
    # Create a session
    session = Session(
        user_id="demo_user",
        topic="Linux Help Session"
    )
    
    print(f"📝 Created session: {session.session_id}")
    print(f"   User: {session.user_id}")
    print(f"   Topic: {session.topic}")
    print()
    
    # Save session
    storage.save_session(session)
    
    # Simulate a conversation
    conversations = [
        {
            "query": "What is Linux?",
            "response": "Linux is an open-source operating system kernel originally created by Linus Torvalds in 1991. It forms the core of many operating system distributions.",
            "model": "llama3.2:3b",
            "confidence": 0.92
        },
        {
            "query": "How do I install software on Linux?",
            "response": "You can install software on Linux using package managers like apt (Ubuntu/Debian), yum/dnf (Red Hat/Fedora), or pacman (Arch Linux). For example: sudo apt install package-name",
            "model": "llama3.2:3b", 
            "confidence": 0.88
        },
        {
            "query": "ja, zeige mir ein beispiel mit apt",
            "response": "Here's an example using apt: sudo apt update && sudo apt install firefox. This updates the package list and installs Firefox browser.",
            "model": "llama3.2:3b",
            "confidence": 0.75
        }
    ]
    
    print("💬 Simulating conversation...")
    
    # Store each conversation with small delays
    for i, conv in enumerate(conversations, 1):
        # Small delay to show timestamp differences
        if i > 1:
            time.sleep(0.1)
        
        entry = ConversationEntry(
            session_id=session.session_id,
            query=conv["query"],
            response=conv["response"],
            model_used=conv["model"],
            confidence_score=conv["confidence"],
            processing_time=1.5 + i * 0.3,
            context_used=(i > 1),  # Later queries use context
            metadata={
                "query_number": i,
                "language_detected": "de" if "ja" in conv["query"] else "en"
            }
        )
        
        # Save conversation
        success = storage.save_conversation(entry)
        print(f"   {i}. Query: '{conv['query'][:50]}...'")
        print(f"      Saved: {'✅' if success else '❌'}")
        
        # Update session activity
        session.update_activity()
    
    # Save updated session
    storage.save_session(session)
    
    print()
    print("🔍 Retrieving conversation history...")
    
    # Load conversation history
    history = storage.load_session_conversations(session.session_id)
    
    print(f"   Found {len(history)} conversations:")
    for i, conv in enumerate(history, 1):
        print(f"   {i}. [{conv.timestamp.strftime('%H:%M:%S')}] Q: {conv.query[:40]}...")
        print(f"      R: {conv.response[:60]}...")
        print(f"      Model: {conv.model_used}, Confidence: {conv.confidence_score}")
        if conv.context_used:
            print(f"      🔗 Used context from previous conversation")
        print()
    
    print("🔎 Testing search functionality...")
    
    # Search for specific terms
    search_terms = ["Linux", "apt", "install"]
    
    for term in search_terms:
        results = storage.search_conversations(term, session.session_id)
        print(f"   Search '{term}': {len(results)} results")
        for result in results:
            print(f"      - {result.query[:30]}... (confidence: {result.confidence_score})")
    
    print()
    print("📊 Storage statistics:")
    stats = storage.get_storage_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print()
    print("📤 Testing export functionality...")
    
    # Export conversations
    json_export = storage.export_conversations(session.session_id, "json")
    csv_export = storage.export_conversations(session.session_id, "csv")
    
    print(f"   JSON export: {len(json_export)} characters")
    print(f"   CSV export: {len(csv_export)} characters")
    
    print()
    print("🎯 Demo completed successfully!")
    print(f"   Session ID: {session.session_id}")
    print(f"   Conversations stored: {len(history)}")
    print(f"   Data location: demo_conversation_data/")
    
    return session.session_id

def demo_context_resolution():
    """Demonstrate how context resolution would work"""
    print("\n🔗 Context Resolution Demo")
    print("=" * 50)
    
    # Example of how the system would resolve references
    conversation_history = [
        {
            "query": "How do I create a new user in Linux?",
            "response": "To create a new user in Linux, use the useradd command: sudo useradd -m username. This creates a new user with a home directory."
        },
        {
            "query": "ja, setze deinen vorschlag um!",
            "resolved_query": "ja, setze deinen vorschlag um! [Context: Previous suggestion was to create a new user using 'sudo useradd -m username']",
            "response": "I'll help you implement the user creation. Here's the complete command with explanation: sudo useradd -m newuser && sudo passwd newuser"
        }
    ]
    
    print("Original conversation flow:")
    for i, conv in enumerate(conversation_history, 1):
        print(f"\n{i}. User: {conv['query']}")
        if 'resolved_query' in conv:
            print(f"   Resolved: {conv['resolved_query']}")
        print(f"   System: {conv['response'][:80]}...")
    
    print("\n✨ This shows how 'deinen vorschlag' gets resolved using conversation context!")

if __name__ == "__main__":
    session_id = demo_conversation_memory()
    demo_context_resolution()