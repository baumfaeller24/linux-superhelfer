#!/usr/bin/env python3
"""
Demo script for session management system
Shows session lifecycle, topic detection, and automatic management
"""

from modules.conversation_memory.models import ConversationEntry, Session
from modules.conversation_memory.storage import ConversationStorage
from modules.conversation_memory.session_manager import SessionManager
from datetime import datetime, timedelta
import time

def demo_session_management():
    """Demonstrate session management functionality"""
    print("🎯 Session Management System Demo")
    print("=" * 50)
    
    # Initialize storage and session manager
    storage = ConversationStorage("demo_session_data")
    session_manager = SessionManager(storage, max_sessions_per_user=3)
    
    print("📋 Testing Session Creation and Topic Detection")
    print("-" * 50)
    
    # Test different queries with topic detection
    test_queries = [
        ("How do I create a new user account?", "user_management"),
        ("Install docker on my Ubuntu server", "docker"),
        ("My network connection keeps dropping", "network"),
        ("How to fix permission denied errors?", "troubleshooting"),
        ("What's the best Python IDE for Linux?", "programming")
    ]
    
    user_id = "demo_user"
    sessions_created = []
    
    for query, expected_topic in test_queries:
        print(f"\n🔍 Query: '{query}'")
        
        # Get or create session (with topic detection)
        session = session_manager.get_or_create_session(user_id, query)
        sessions_created.append(session)
        
        detected_topic = session_manager.detect_topic(query)
        print(f"   Detected Topic: {detected_topic}")
        print(f"   Session ID: {session.session_id}")
        print(f"   Session Topic: {session.topic}")
        
        # Simulate conversation
        entry = ConversationEntry(
            session_id=session.session_id,
            query=query,
            response=f"Here's help with {detected_topic or 'your question'}...",
            model_used="llama3.2:3b",
            confidence_score=0.85
        )
        storage.save_conversation(entry)
        
        # Small delay to differentiate timestamps
        time.sleep(0.1)
    
    print(f"\n📊 Created {len(set(s.session_id for s in sessions_created))} unique sessions")
    
    # Test session limits
    print("\n🚫 Testing Session Limits (max 3 per user)")
    print("-" * 50)
    
    # Create additional sessions to test limit
    extra_queries = [
        "How to configure Apache web server?",
        "Database optimization techniques",
        "Linux kernel compilation guide"
    ]
    
    for query in extra_queries:
        session = session_manager.get_or_create_session(user_id, query)
        print(f"   Query: '{query[:40]}...'")
        print(f"   Session: {session.session_id}")
    
    # Check active sessions
    active_sessions = session_manager.get_user_sessions(user_id, active_only=True)
    print(f"\n   Active sessions for {user_id}: {len(active_sessions)}")
    for session in active_sessions:
        print(f"     - {session.session_id}: {session.topic}")
    
    print("\n🔄 Testing Topic Change Detection")
    print("-" * 50)
    
    # Get current session
    current_session = session_manager.get_active_session(user_id)
    
    # Test queries in same and different topics
    test_cases = [
        ("How to compile the Linux kernel from source?", "Same topic area"),
        ("What is Docker Compose?", "Different topic - should trigger change"),
        ("Can you help me with something else?", "Ambiguous - no change")
    ]
    
    for query, description in test_cases:
        topic_changed = session_manager.detect_topic_change(query, current_session)
        print(f"   Query: '{query[:40]}...'")
        print(f"   Description: {description}")
        print(f"   Topic Change Detected: {'✅ Yes' if topic_changed else '❌ No'}")
        print()
    
    print("⏰ Testing Session Expiration")
    print("-" * 50)
    
    # Create a session and manually expire it
    test_session = session_manager.create_session(user_id, "Test Expiration")
    print(f"   Created test session: {test_session.session_id}")
    
    # Manually set old timestamp
    test_session.last_activity = datetime.now() - timedelta(hours=2)
    storage.save_session(test_session)
    print(f"   Set last activity to 2 hours ago")
    
    # Auto-expire sessions
    expired_ids = session_manager.auto_expire_sessions(timeout_hours=1)
    print(f"   Auto-expired sessions: {len(expired_ids)}")
    for session_id in expired_ids:
        print(f"     - {session_id}")
    
    print("\n📈 Session Summaries")
    print("-" * 50)
    
    # Get summaries for all sessions
    all_sessions = session_manager.get_user_sessions(user_id)
    
    for session in all_sessions[:3]:  # Show first 3
        summary = session_manager.get_session_summary(session.session_id)
        print(f"\n   Session: {session.session_id}")
        print(f"   Topic: {summary.get('topic', 'Unknown')}")
        print(f"   Status: {summary.get('status', 'Unknown')}")
        print(f"   Conversations: {summary.get('total_conversations', 0)}")
        print(f"   Duration: {summary.get('duration_minutes', 0):.1f} minutes")
        print(f"   Avg Confidence: {summary.get('average_confidence', 0):.3f}")
        print(f"   Expired: {'Yes' if summary.get('is_expired') else 'No'}")
    
    print("\n🧹 Testing Session Cleanup")
    print("-" * 50)
    
    # Manual session ending
    if active_sessions:
        session_to_end = active_sessions[0]
        success = session_manager.end_session(session_to_end.session_id, "demo_completed")
        print(f"   Manually ended session: {session_to_end.session_id}")
        print(f"   Success: {'✅' if success else '❌'}")
    
    # Cleanup old sessions
    cleaned_count = session_manager.cleanup_old_sessions(max_age_days=0)  # Aggressive cleanup for demo
    print(f"   Cleaned up {cleaned_count} old items")
    
    print("\n📊 Final Statistics")
    print("-" * 50)
    
    # Storage stats
    stats = storage.get_storage_stats()
    print(f"   Conversation files: {stats.get('conversation_files', 0)}")
    print(f"   Session files: {stats.get('session_files', 0)}")
    print(f"   Total size: {stats.get('total_size_mb', 0)} MB")
    
    # Active sessions after cleanup
    final_active = session_manager.get_user_sessions(user_id, active_only=True)
    print(f"   Active sessions remaining: {len(final_active)}")
    
    print("\n🎉 Session Management Demo Completed!")
    print(f"   Data location: demo_session_data/")
    
    return len(final_active)

def demo_multi_user_sessions():
    """Demonstrate multi-user session management"""
    print("\n👥 Multi-User Session Management Demo")
    print("=" * 50)
    
    storage = ConversationStorage("demo_multiuser_data")
    session_manager = SessionManager(storage)
    
    # Create sessions for different users
    users = ["alice", "bob", "charlie"]
    user_sessions = {}
    
    for user in users:
        print(f"\n👤 Creating sessions for {user}:")
        
        # Each user gets 2 sessions with different topics
        queries = [
            f"How do I set up SSH keys for {user}?",
            f"Docker container management for {user}'s project"
        ]
        
        user_sessions[user] = []
        for query in queries:
            session = session_manager.get_or_create_session(user, query)
            user_sessions[user].append(session)
            print(f"   Session: {session.session_id} (Topic: {session.topic})")
    
    # Show session isolation
    print(f"\n🔒 Session Isolation Test:")
    for user in users:
        user_active_sessions = session_manager.get_user_sessions(user, active_only=True)
        print(f"   {user}: {len(user_active_sessions)} active sessions")
    
    # Test cross-user session access
    print(f"\n🚫 Cross-User Access Test:")
    alice_session_id = user_sessions["alice"][0].session_id
    
    # Bob tries to get Alice's session (should not work through user-specific methods)
    bob_sessions = session_manager.get_user_sessions("bob", active_only=True)
    alice_session_in_bob_list = any(s.session_id == alice_session_id for s in bob_sessions)
    
    print(f"   Alice's session in Bob's list: {'❌ Yes (ERROR!)' if alice_session_in_bob_list else '✅ No (Correct)'}")
    
    print(f"\n🎯 Multi-user demo completed successfully!")

if __name__ == "__main__":
    remaining_sessions = demo_session_management()
    demo_multi_user_sessions()
    
    print(f"\n🏁 All demos completed!")
    print(f"   Check demo_session_data/ and demo_multiuser_data/ for generated data")