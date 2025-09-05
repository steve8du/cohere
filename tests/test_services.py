"""
Unit tests for services module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.core.services import process_query, get_history, load_history, save_history, add_to_history, get_cohere_client
from src.core.models import ChatHistoryEntry
from src.tools.wikipedia import search_wikipedia


class TestWikipediaService:
    """Test Wikipedia service functionality"""
    
    def test_search_success(self):
        """Test successful Wikipedia search"""
        with patch('wikipedia.page') as mock_page, \
             patch('wikipedia.summary') as mock_summary:
            
            mock_page.return_value.url = "https://en.wikipedia.org/wiki/Python"
            mock_summary.return_value = "Python is a programming language."
            
            result = search_wikipedia("Python programming", sentences=2)
            
            assert "Python is a programming language" in result
            assert "Wikipedia Summary:" in result
            assert "Source:" in result
    
    def test_search_disambiguation(self):
        """Test Wikipedia disambiguation handling"""
        import wikipedia
        
        with patch('wikipedia.summary') as mock_summary:
            mock_summary.side_effect = wikipedia.exceptions.DisambiguationError("Python", ["Python (programming)", "Python (snake)"])
            
            result = search_wikipedia("Python", sentences=2)
            
            assert "Multiple pages found" in result
            assert "Python (programming)" in result
            assert "Python (snake)" in result
    
    def test_search_page_not_found(self):
        """Test Wikipedia page not found"""
        import wikipedia
        
        with patch('wikipedia.page') as mock_page:
            mock_page.side_effect = wikipedia.exceptions.PageError("NonExistentPage")
            
            result = search_wikipedia("NonExistentPage")
            
            assert "No Wikipedia page found" in result


class TestChatHistoryService:
    """Test chat history service functionality"""
    
    def test_load_empty_history(self):
        """Test loading history when file doesn't exist"""
        with patch('pathlib.Path.exists', return_value=False):
            history = load_history()
            assert history == []
    
    def test_save_and_load_history(self):
        """Test saving and loading chat history"""
        test_entry = ChatHistoryEntry(
            conversation_id="test-123",
            user_query="Test query",
            response="Test response",
            timestamp=datetime.now().isoformat(),
            used_wikipedia=False
        )
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            save_history([test_entry])
            
            # Verify write was called
            mock_file.write.called
    
    def test_add_entry(self):
        """Test adding a new chat history entry"""
        with patch('src.core.services.load_history', return_value=[]), \
             patch('src.core.services.save_history') as mock_save:
            
            add_to_history(
                conversation_id="test-456",
                user_query="What is Python?",
                response="Python is a programming language.",
                used_wikipedia=True
            )
            
            # Verify save was called with one entry
            assert mock_save.called
            saved_history = mock_save.call_args[0][0]
            assert len(saved_history) == 1
            assert saved_history[0].conversation_id == "test-456"


class TestChatService:
    """Test chat service functionality"""
    
    @pytest.mark.asyncio
    async def test_process_query_without_tools(self):
        """Test processing a query without tool calls"""
        mock_client = Mock()
        mock_response = Mock()
        mock_message = Mock()
        mock_content = [Mock()]
        mock_content[0].text = "Paris is the capital of France."
        mock_message.content = mock_content
        mock_message.tool_calls = None
        mock_response.message = mock_message
        mock_client.chat.return_value = mock_response
        
        with patch('src.core.services.get_cohere_client', return_value=mock_client), \
             patch('src.core.services.add_to_history'):
            
            result = await process_query("What is the capital of France?")
            
            assert result["response"] == "Paris is the capital of France."
            assert result["used_wikipedia"] == False
            assert "conversation_id" in result
            assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_process_query_with_wikipedia(self):
        """Test processing a query that triggers Wikipedia search"""
        mock_client = Mock()
        
        # First response with tool call
        mock_response1 = Mock()
        mock_message1 = Mock()
        mock_content1 = [Mock()]
        mock_content1[0].text = "I'll search Wikipedia for you."
        mock_message1.content = mock_content1
        
        mock_tool_call = Mock()
        mock_function = Mock()
        mock_function.name = "search_wikipedia"
        mock_function.arguments = '{"query": "Python", "sentences": 3}'
        mock_tool_call.function = mock_function
        mock_message1.tool_calls = [mock_tool_call]
        mock_response1.message = mock_message1
        
        # Second response after tool use
        mock_response2 = Mock()
        mock_message2 = Mock()
        mock_content2 = [Mock()]
        mock_content2[0].text = "Python is a high-level programming language."
        mock_message2.content = mock_content2
        mock_response2.message = mock_message2
        
        mock_client.chat.side_effect = [mock_response1, mock_response2]
        
        with patch('src.core.services.get_cohere_client', return_value=mock_client), \
             patch('src.tools.wikipedia.search_wikipedia', return_value="Wikipedia: Python info"), \
             patch('src.core.services.add_to_history'):
            
            result = await process_query("Tell me about Python")
            
            assert result["response"] == "Python is a high-level programming language."
            assert result["used_wikipedia"] == True
            assert mock_client.chat.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_history(self):
        """Test getting chat history"""
        test_history = [
            ChatHistoryEntry(
                conversation_id="test-1",
                user_query="Query 1",
                response="Response 1",
                timestamp=datetime.now().isoformat(),
                used_wikipedia=False
            ),
            ChatHistoryEntry(
                conversation_id="test-2",
                user_query="Query 2",
                response="Response 2",
                timestamp=datetime.now().isoformat(),
                used_wikipedia=True
            )
        ]
        
        with patch('src.core.services.load_history', return_value=test_history):
            result = await get_history()
            
            assert result["total_conversations"] == 2
            assert len(result["history"]) == 2
            assert result["history"][0].conversation_id == "test-1"
            assert result["history"][1].used_wikipedia == True