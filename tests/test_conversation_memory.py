"""
Tests for conversation memory system
"""

import unittest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from modules.conversation_memory.models import ConversationEntry, Session, generate_conversation_id, generate_session_id
from modules.conversation_memory.storage import ConversationStorage


class TestConversationModels(unittest.TestCase):
    """Test conversation data models"""
    
    def test_conversation_entry_creation(self):
        """Test creating a conversation entry"""
        entry = ConversationEntry(
            query="What is Linux?",
            response="Linux is an operating system...",
            model_used="llama3.2:3b",
            confidence_score=0.85
        )
        
        self.assertIsNotNone(entry.id)
        self.assertIsInstance(entry.timestamp, datetime)
        self.assertEqual(entry.query, "What is Linux?")
        self.assertEqual(entry.confidence_score, 0.85)
    
    def test_conversation_entry_serialization(self):
        """Test JSON serialization/deserialization"""
        original = ConversationEntry(
            query="Test query",
            response="Test response",
            model_used="test_model",
            confidence_score=0.9,
            metadata={"test": "value"}
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = ConversationEntry.from_dict(data)
        
        self.assertEqual(original.query, restored.query)
        self.assertEqual(original.response, restored.response)
        self.assertEqual(original.confidence_score, restored.confidence_score)
        self.assertEqual(original.metadata, restored.metadata)
    
    def test_conversation_entry_json(self):
        """Test JSON string conversion"""
        entry = ConversationEntry(query="Test", response="Response")
        json_str = entry.to_json()
        restored = ConversationEntry.from_json(json_str)
        
        self.assertEqual(entry.query, restored.query)
        self.assertEqual(entry.response, restored.response)
    
    def test_session_creation(self):
        """Test creating a session"""
        session = Session(user_id="test_user", topic="Linux Help")
        
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.user_id, "test_user")
        self.assertEqual(session.topic, "Linux Help")
        self.assertEqual(session.status, "active")
        self.assertEqual(session.interaction_count, 0)
    
    def test_session_activity_update(self):
        """Test session activity updates"""
        session = Session()
        original_time = session.last_activity
        original_count = session.interaction_count
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        session.update_activity()
        
        self.assertGreater(session.last_activity, original_time)
        self.assertEqual(session.interaction_count, original_count + 1)
    
    def test_session_expiration(self):
        """Test session expiration logic"""
        session = Session()
        
        # Fresh session should not be expired
        self.assertFalse(session.is_expired(timeout_hours=1))
        
        # Manually set old timestamp
        session.last_activity = datetime.now() - timedelta(hours=2)
        self.assertTrue(session.is_expired(timeout_hours=1))
        
        # Inactive session should be expired
        session.status = "inactive"
        self.assertTrue(session.is_expired())
    
    def test_id_generation(self):
        """Test ID generation functions"""
        conv_id = generate_conversation_id()
        session_id = generate_session_id()
        
        self.assertTrue(conv_id.startswith("conv_"))
        self.assertTrue(session_id.startswith("session_"))
        
        # IDs should be unique
        conv_id2 = generate_conversation_id()
        self.assertNotEqual(conv_id, conv_id2)


class TestConversationStorage(unittest.TestCase):
    """Test conversation storage system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = ConversationStorage(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_storage_initialization(self):
        """Test storage directory creation"""
        self.assertTrue(self.storage.storage_dir.exists())
        self.assertTrue(self.storage.conversations_dir.exists())
        self.assertTrue(self.storage.sessions_dir.exists())
        self.assertTrue(self.storage.archive_dir.exists())
    
    def test_save_and_load_conversation(self):
        """Test saving and loading conversations"""
        # Create test conversation
        entry = ConversationEntry(
            session_id="test_session_123",
            query="Test query",
            response="Test response",
            model_used="test_model"
        )
        
        # Save conversation
        success = self.storage.save_conversation(entry)
        self.assertTrue(success)
        
        # Load conversations for session
        conversations = self.storage.load_session_conversations("test_session_123")
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0].query, "Test query")
        self.assertEqual(conversations[0].response, "Test response")
    
    def test_save_and_load_session(self):
        """Test saving and loading sessions"""
        # Create test session
        session = Session(
            session_id="test_session_456",
            user_id="test_user",
            topic="Test Topic"
        )
        
        # Save session
        success = self.storage.save_session(session)
        self.assertTrue(success)
        
        # Load session
        loaded_session = self.storage.load_session("test_session_456")
        self.assertIsNotNone(loaded_session)
        self.assertEqual(loaded_session.user_id, "test_user")
        self.assertEqual(loaded_session.topic, "Test Topic")
    
    def test_multiple_conversations_same_session(self):
        """Test multiple conversations in same session"""
        session_id = "multi_test_session"
        
        # Create multiple conversations
        for i in range(3):
            entry = ConversationEntry(
                session_id=session_id,
                query=f"Query {i}",
                response=f"Response {i}"
            )
            self.storage.save_conversation(entry)
        
        # Load all conversations
        conversations = self.storage.load_session_conversations(session_id)
        self.assertEqual(len(conversations), 3)
        
        # Should be in reverse chronological order (newest first)
        self.assertEqual(conversations[0].query, "Query 2")
        self.assertEqual(conversations[1].query, "Query 1")
        self.assertEqual(conversations[2].query, "Query 0")
    
    def test_list_active_sessions(self):
        """Test listing active sessions"""
        # Create test sessions
        session1 = Session(user_id="user1", topic="Topic 1")
        session2 = Session(user_id="user2", topic="Topic 2")
        session3 = Session(user_id="user1", topic="Topic 3")
        session3.status = "inactive"  # This should be filtered out
        
        # Save sessions
        self.storage.save_session(session1)
        self.storage.save_session(session2)
        self.storage.save_session(session3)
        
        # List all active sessions
        active_sessions = self.storage.list_active_sessions()
        self.assertEqual(len(active_sessions), 2)
        
        # List sessions for specific user
        user1_sessions = self.storage.list_active_sessions("user1")
        self.assertEqual(len(user1_sessions), 1)
        self.assertEqual(user1_sessions[0].topic, "Topic 1")
    
    def test_search_conversations(self):
        """Test conversation search functionality"""
        session_id = "search_test_session"
        
        # Create conversations with different content
        conversations = [
            ("How to install Linux?", "Use the installer..."),
            ("What is Docker?", "Docker is a containerization platform..."),
            ("Linux file permissions", "Use chmod command...")
        ]
        
        for query, response in conversations:
            entry = ConversationEntry(
                session_id=session_id,
                query=query,
                response=response
            )
            self.storage.save_conversation(entry)
        
        # Search for "Linux"
        results = self.storage.search_conversations("Linux")
        self.assertEqual(len(results), 2)  # Should find 2 conversations
        
        # Search for "Docker"
        results = self.storage.search_conversations("Docker")
        self.assertEqual(len(results), 1)
        self.assertIn("Docker", results[0].response)
        
        # Search within specific session
        results = self.storage.search_conversations("chmod", session_id=session_id)
        self.assertEqual(len(results), 1)
        self.assertIn("chmod", results[0].response)
    
    def test_export_conversations(self):
        """Test conversation export functionality"""
        session_id = "export_test_session"
        
        # Create test conversations
        entry = ConversationEntry(
            session_id=session_id,
            query="Test query",
            response="Test response",
            model_used="test_model",
            confidence_score=0.8
        )
        self.storage.save_conversation(entry)
        
        # Export as JSON
        json_export = self.storage.export_conversations(session_id, "json")
        self.assertIsNotNone(json_export)
        self.assertIn("Test query", json_export)
        self.assertIn("Test response", json_export)
        
        # Export as CSV
        csv_export = self.storage.export_conversations(session_id, "csv")
        self.assertIsNotNone(csv_export)
        self.assertIn("timestamp,query,response", csv_export)
        self.assertIn("Test query", csv_export)
    
    def test_storage_stats(self):
        """Test storage statistics"""
        # Create some test data
        session = Session()
        self.storage.save_session(session)
        
        entry = ConversationEntry(session_id=session.session_id)
        self.storage.save_conversation(entry)
        
        # Get stats
        stats = self.storage.get_storage_stats()
        
        self.assertIn("conversation_files", stats)
        self.assertIn("session_files", stats)
        self.assertIn("total_size_mb", stats)
        self.assertGreaterEqual(stats["conversation_files"], 1)
        self.assertGreaterEqual(stats["session_files"], 1)


class TestSessionManager(unittest.TestCase):
    """Test session management functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = ConversationStorage(self.temp_dir)
        
        # Import here to avoid circular imports during module loading
        from modules.conversation_memory.session_manager import SessionManager
        self.session_manager = SessionManager(self.storage)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_session(self):
        """Test session creation"""
        session = self.session_manager.create_session("test_user", "Linux Help")
        
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.user_id, "test_user")
        self.assertEqual(session.topic, "Linux Help")
        self.assertEqual(session.status, "active")
        
        # Verify session was saved
        loaded_session = self.storage.load_session(session.session_id)
        self.assertIsNotNone(loaded_session)
        self.assertEqual(loaded_session.user_id, "test_user")
    
    def test_get_or_create_session(self):
        """Test getting existing session or creating new one"""
        # First call should create new session
        session1 = self.session_manager.get_or_create_session("test_user", "How to install Linux?")
        self.assertIsNotNone(session1)
        
        # Second call should return same session (not expired)
        session2 = self.session_manager.get_or_create_session("test_user", "What is apt?")
        self.assertEqual(session1.session_id, session2.session_id)
        
        # Verify interaction count increased
        self.assertGreater(session2.interaction_count, session1.interaction_count)
    
    def test_topic_detection(self):
        """Test automatic topic detection"""
        test_cases = [
            ("How do I create a new user account?", "user_management"),
            ("Install docker on Ubuntu", "docker"),
            ("My network connection is not working", "network"),
            ("How to fix permission denied error?", "troubleshooting"),
            ("What is the best Python IDE?", "programming"),
            ("Random text without clear topic", "")
        ]
        
        for query, expected_topic in test_cases:
            detected_topic = self.session_manager.detect_topic(query)
            if expected_topic:
                self.assertEqual(detected_topic, expected_topic, f"Failed for query: {query}")
            else:
                self.assertEqual(detected_topic, "", f"Should not detect topic for: {query}")
    
    def test_topic_change_detection(self):
        """Test topic change detection"""
        # Create session with specific topic
        session = self.session_manager.create_session("test_user", "user_management")
        
        # Query in same topic should not trigger change
        same_topic_query = "How to delete a user account?"
        self.assertFalse(self.session_manager.detect_topic_change(same_topic_query, session))
        
        # Query in different topic should trigger change
        different_topic_query = "How to configure Docker containers?"
        self.assertTrue(self.session_manager.detect_topic_change(different_topic_query, session))
        
        # Ambiguous query should not trigger change
        ambiguous_query = "What do you think?"
        self.assertFalse(self.session_manager.detect_topic_change(ambiguous_query, session))
    
    def test_session_expiration(self):
        """Test session expiration functionality"""
        # Create session
        session = self.session_manager.create_session("test_user")
        
        # Session should not be expired initially
        self.assertFalse(session.is_expired(1))
        
        # Manually set old timestamp
        session.last_activity = datetime.now() - timedelta(hours=2)
        self.storage.save_session(session)
        
        # Auto-expire sessions
        expired_ids = self.session_manager.auto_expire_sessions(timeout_hours=1)
        self.assertIn(session.session_id, expired_ids)
        
        # Verify session is marked as inactive
        updated_session = self.storage.load_session(session.session_id)
        self.assertEqual(updated_session.status, "inactive")
    
    def test_max_sessions_per_user(self):
        """Test maximum sessions per user limit"""
        user_id = "test_user"
        max_sessions = 3
        
        # Create session manager with low limit for testing
        from modules.conversation_memory.session_manager import SessionManager
        limited_manager = SessionManager(self.storage, max_sessions_per_user=max_sessions)
        
        # Create maximum number of sessions
        sessions = []
        for i in range(max_sessions):
            session = limited_manager.create_session(user_id, f"Topic {i}")
            sessions.append(session)
        
        # All sessions should be active
        active_sessions = limited_manager.get_user_sessions(user_id, active_only=True)
        self.assertEqual(len(active_sessions), max_sessions)
        
        # Creating one more should expire the oldest
        new_session = limited_manager.create_session(user_id, "New Topic")
        
        # Should still have max_sessions active sessions
        active_sessions = limited_manager.get_user_sessions(user_id, active_only=True)
        self.assertEqual(len(active_sessions), max_sessions)
        
        # New session should be in the active list
        active_session_ids = [s.session_id for s in active_sessions]
        self.assertIn(new_session.session_id, active_session_ids)
    
    def test_end_session_manually(self):
        """Test manually ending a session"""
        session = self.session_manager.create_session("test_user")
        
        # End session
        success = self.session_manager.end_session(session.session_id, "test_completed")
        self.assertTrue(success)
        
        # Verify session is inactive
        updated_session = self.storage.load_session(session.session_id)
        self.assertEqual(updated_session.status, "inactive")
        self.assertEqual(updated_session.metadata["end_reason"], "test_completed")
    
    def test_session_summary(self):
        """Test session summary generation"""
        # Create session and add some conversations
        session = self.session_manager.create_session("test_user", "Linux Help")
        
        # Add conversations
        from modules.conversation_memory.models import ConversationEntry
        for i in range(3):
            entry = ConversationEntry(
                session_id=session.session_id,
                query=f"Query {i}",
                response=f"Response {i}",
                model_used="test_model",
                confidence_score=0.8 + i * 0.05
            )
            self.storage.save_conversation(entry)
        
        # Get summary
        summary = self.session_manager.get_session_summary(session.session_id)
        
        self.assertEqual(summary["session_id"], session.session_id)
        self.assertEqual(summary["user_id"], "test_user")
        self.assertEqual(summary["topic"], "Linux Help")
        self.assertEqual(summary["total_conversations"], 3)
        self.assertGreater(summary["average_confidence"], 0.8)
        self.assertEqual(summary["models_used"], ["test_model"])
    
    def test_get_active_session(self):
        """Test getting active session for user"""
        user_id = "test_user"
        
        # No active session initially
        session = self.session_manager.get_active_session(user_id)
        self.assertIsNone(session)
        
        # Create session
        created_session = self.session_manager.create_session(user_id)
        
        # Should return the created session
        active_session = self.session_manager.get_active_session(user_id)
        self.assertIsNotNone(active_session)
        self.assertEqual(active_session.session_id, created_session.session_id)
        
        # Create another session (more recent)
        import time
        time.sleep(0.01)  # Small delay to ensure different timestamps
        newer_session = self.session_manager.create_session(user_id)
        
        # Should return the newer session
        active_session = self.session_manager.get_active_session(user_id)
        self.assertEqual(active_session.session_id, newer_session.session_id)


if __name__ == '__main__':
    unittest.main()


class TestConversationMemoryManager(unittest.TestCase):
    """Test the main conversation memory manager"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Import here to avoid circular imports during module loading
        from modules.conversation_memory.manager import ConversationMemoryManager
        self.memory_manager = ConversationMemoryManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_store_interaction(self):
        """Test storing a complete interaction"""
        query = "How do I install Docker?"
        response = "To install Docker, run: sudo apt install docker.io"
        metadata = {
            "model_used": "llama3.2:3b",
            "confidence_score": 0.9,
            "processing_time": 1.5,
            "vram_usage": "25%"
        }
        
        # Store interaction
        interaction_id = self.memory_manager.store_interaction(query, response, metadata)
        
        self.assertIsNotNone(interaction_id)
        self.assertNotIn("error_", interaction_id)
        
        # Verify it was stored by getting context
        context = self.memory_manager.get_conversation_context()
        self.assertEqual(len(context), 1)
        self.assertEqual(context[0]["query"], query)
        self.assertEqual(context[0]["response"], response)
    
    def test_get_conversation_context(self):
        """Test retrieving conversation context"""
        user_id = "test_user"
        
        # Store multiple interactions
        interactions = [
            ("What is Linux?", "Linux is an operating system..."),
            ("How to install packages?", "Use apt install package-name..."),
            ("What about Docker?", "Docker is a containerization platform...")
        ]
        
        for query, response in interactions:
            metadata = {"model_used": "test_model", "confidence_score": 0.8}
            self.memory_manager.store_interaction(query, response, metadata, user_id)
        
        # Get context
        context = self.memory_manager.get_conversation_context(user_id, limit=2)
        
        self.assertEqual(len(context), 2)
        # Should be in reverse chronological order (newest first)
        self.assertEqual(context[0]["query"], "What about Docker?")
        self.assertEqual(context[1]["query"], "How to install packages?")
    
    def test_search_history(self):
        """Test searching conversation history"""
        user_id = "search_user"
        
        # Store conversations with different content
        conversations = [
            ("How to install Docker?", "Use apt install docker.io"),
            ("What is Linux?", "Linux is an operating system"),
            ("Docker container management", "Use docker run, docker stop commands"),
            ("Python programming tips", "Use virtual environments")
        ]
        
        for query, response in conversations:
            metadata = {"model_used": "test_model", "confidence_score": 0.8}
            self.memory_manager.store_interaction(query, response, metadata, user_id)
        
        # Search for "Docker"
        results = self.memory_manager.search_history("Docker", user_id)
        
        self.assertEqual(len(results), 2)  # Should find 2 Docker-related conversations
        
        # Results should be sorted by relevance
        self.assertGreater(results[0]["relevance_score"], 0)
        
        # Check that Docker conversations are found
        docker_queries = [r["query"] for r in results]
        self.assertIn("How to install Docker?", docker_queries)
        self.assertIn("Docker container management", docker_queries)
    
    def test_session_management_integration(self):
        """Test session management through the main manager"""
        user_id = "session_test_user"
        
        # Get session info (should have no active session initially)
        session_info = self.memory_manager.get_session_info(user_id)
        self.assertFalse(session_info["has_active_session"])
        
        # Store an interaction (should create session)
        metadata = {"model_used": "test_model", "confidence_score": 0.8}
        self.memory_manager.store_interaction("Test query", "Test response", metadata, user_id)
        
        # Now should have active session
        session_info = self.memory_manager.get_session_info(user_id)
        self.assertTrue(session_info["has_active_session"])
        self.assertEqual(session_info["user_id"], user_id)
        self.assertGreater(session_info["total_conversations"], 0)
        
        # Get user sessions
        sessions = self.memory_manager.get_user_sessions(user_id)
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["user_id"], user_id)
    
    def test_manual_session_creation(self):
        """Test manually creating sessions"""
        user_id = "manual_session_user"
        topic = "Linux Administration"
        
        # Create session manually
        session_id = self.memory_manager.create_session(user_id, topic)
        self.assertIsNotNone(session_id)
        self.assertNotEqual(session_id, "")
        
        # Verify session exists
        session_info = self.memory_manager.get_session_info(user_id)
        self.assertTrue(session_info["has_active_session"])
        self.assertEqual(session_info["topic"], topic)
        
        # End session
        success = self.memory_manager.end_session(session_id, "test_completed")
        self.assertTrue(success)
        
        # Verify session is ended
        session_info = self.memory_manager.get_session_info(user_id)
        self.assertFalse(session_info["has_active_session"])
    
    def test_export_conversations(self):
        """Test conversation export functionality"""
        user_id = "export_user"
        
        # Store some conversations
        conversations = [
            ("Query 1", "Response 1"),
            ("Query 2", "Response 2")
        ]
        
        for query, response in conversations:
            metadata = {"model_used": "test_model", "confidence_score": 0.8}
            self.memory_manager.store_interaction(query, response, metadata, user_id)
        
        # Export as JSON
        json_export = self.memory_manager.export_conversations(user_id=user_id, format="json")
        self.assertIsNotNone(json_export)
        self.assertIn("Query 1", json_export)
        self.assertIn("Response 1", json_export)
        
        # Export as CSV
        csv_export = self.memory_manager.export_conversations(user_id=user_id, format="csv")
        self.assertIsNotNone(csv_export)
        self.assertIn("timestamp,query,response", csv_export)
    
    def test_system_stats(self):
        """Test system statistics"""
        # Store some test data
        metadata = {"model_used": "test_model", "confidence_score": 0.8}
        self.memory_manager.store_interaction("Test query", "Test response", metadata)
        
        # Get stats
        stats = self.memory_manager.get_system_stats()
        
        self.assertIn("storage", stats)
        self.assertIn("sessions", stats)
        self.assertIn("system", stats)
        
        # Check storage stats
        self.assertIn("conversation_files", stats["storage"])
        self.assertIn("session_files", stats["storage"])
        
        # Check session stats
        self.assertGreaterEqual(stats["sessions"]["total_sessions"], 1)
        self.assertGreaterEqual(stats["sessions"]["total_interactions"], 1)
        
        # Check system config
        self.assertIn("auto_cleanup_enabled", stats["system"])
        self.assertIn("max_context_entries", stats["system"])
    
    def test_cleanup_old_data(self):
        """Test data cleanup functionality"""
        # Store some test data
        metadata = {"model_used": "test_model", "confidence_score": 0.8}
        self.memory_manager.store_interaction("Test query", "Test response", metadata)
        
        # Run cleanup (with 0 days to force cleanup)
        cleanup_stats = self.memory_manager.cleanup_old_data(max_age_days=0)
        
        self.assertIn("archived_conversations", cleanup_stats)
        self.assertIn("expired_sessions", cleanup_stats)
        self.assertIn("total_cleaned", cleanup_stats)
        
        # Should be a number (even if 0)
        self.assertIsInstance(cleanup_stats["total_cleaned"], int)
    
    def test_relevance_scoring(self):
        """Test relevance scoring for search results"""
        user_id = "relevance_user"
        
        # Store conversations with varying relevance to "Docker"
        conversations = [
            ("How to install Docker on Ubuntu?", "Run sudo apt install docker.io"),  # High relevance
            ("Docker container best practices", "Use multi-stage builds"),  # High relevance
            ("What is containerization?", "Docker is a popular tool for containers"),  # Medium relevance
            ("Linux file permissions", "Use chmod command")  # Low relevance
        ]
        
        for query, response in conversations:
            metadata = {"model_used": "test_model", "confidence_score": 0.9}
            self.memory_manager.store_interaction(query, response, metadata, user_id)
        
        # Search for "Docker"
        results = self.memory_manager.search_history("Docker", user_id)
        
        # Should find 3 results (excluding the one with no Docker mention)
        self.assertEqual(len(results), 3)
        
        # Results should be sorted by relevance (highest first)
        relevance_scores = [r["relevance_score"] for r in results]
        self.assertEqual(relevance_scores, sorted(relevance_scores, reverse=True))
        
        # First result should have highest relevance
        self.assertGreater(results[0]["relevance_score"], results[-1]["relevance_score"])
    
    def test_multi_user_isolation(self):
        """Test that users' conversations are properly isolated"""
        users = ["alice", "bob", "charlie"]
        
        # Each user stores different conversations
        for i, user in enumerate(users):
            query = f"User {user}'s question {i}"
            response = f"Response for {user}"
            metadata = {"model_used": "test_model", "confidence_score": 0.8}
            self.memory_manager.store_interaction(query, response, metadata, user)
        
        # Each user should only see their own conversations
        for user in users:
            context = self.memory_manager.get_conversation_context(user)
            self.assertEqual(len(context), 1)
            self.assertIn(user, context[0]["query"])
            
            # Search should only return their conversations
            results = self.memory_manager.search_history(user, user)
            self.assertEqual(len(results), 1)
            self.assertIn(user, results[0]["query"])
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test with invalid user ID
        context = self.memory_manager.get_conversation_context("nonexistent_user")
        self.assertEqual(len(context), 0)
        
        # Test search with empty query
        results = self.memory_manager.search_history("")
        self.assertEqual(len(results), 0)
        
        # Test ending nonexistent session
        success = self.memory_manager.end_session("nonexistent_session")
        self.assertFalse(success)
        
        # Test export with no data
        export_result = self.memory_manager.export_conversations(user_id="nonexistent_user")
        self.assertIsNone(export_result)