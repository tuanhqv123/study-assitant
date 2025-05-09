import asyncio
from openai import OpenAI
from .file_service import FileService
from .web_search_service import WebSearchService
from .web_scraper_service import WebScraperService
import os
import httpx
from ..utils.logger import Logger
import zlib
from ..config.agents import get_agent
import json

logger = Logger()

class AiService:
    def __init__(self):
        # OpenRouter API Configuration
        self.OPENROUTER_API_KEY = "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"
        self.DEFAULT_MODEL = "mistralai/mistral-small-3.1-24b-instruct:free" 
        
        # Initialize OpenAI client with OpenRouter configuration
        try:
            # Cách 1: Không dùng tham số proxies
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.OPENROUTER_API_KEY
            )
        except TypeError:
            # Cách 2: Nếu có lỗi, thử tạo httpx client trước
            http_client = httpx.Client()
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.OPENROUTER_API_KEY,
                http_client=http_client
            )
            
        # Initialize web search service
        self.web_search_service = WebSearchService()
        # Initialize web scraper service
        self.web_scraper_service = WebScraperService()

    # PlantUML encoding for plantuml.com service
    @staticmethod
    def _plantuml_encode(text: str) -> str:
        """Compress and encode PlantUML text for URL."""
        data = text.encode('utf-8')
        compressed = zlib.compress(data, 9)[2:-4]
        # PlantUML custom base64
        enc_table = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
        result = ''
        buffer = 0
        bits_left = 0
        for byte in compressed:
            buffer = (buffer << 8) | byte
            bits_left += 8
            while bits_left >= 6:
                bits_left -= 6
                index = (buffer >> bits_left) & 0x3F
                result += enc_table[index]
        if bits_left:
            index = (buffer << (6 - bits_left)) & 0x3F
            result += enc_table[index]
        return result

    def _render_plantuml(self, ai_response: str) -> str:
        """Detect PlantUML code blocks and append rendered image URLs."""
        import re
        pattern = r'```plantuml\n(.*?)\n```'
        def replace(match):
            puml = match.group(1)
            encoded = self._plantuml_encode(puml)
            url = f"https://www.plantuml.com/plantuml/png/{encoded}"
            return f"{match.group(0)}\n\n![Diagram]({url})"
        return re.sub(pattern, replace, ai_response, flags=re.DOTALL)

    def chat_with_ai(self, message, conversation_history=None, agent_id=None):
        """
        Send a message to the AI model and get a response.
        
        Args:
            message (str): The user's message
            conversation_history (list, optional): Previous messages in the conversation
            agent_id (str, optional): ID of the agent to use
        
        Returns:
            tuple: (str, list) The AI's response and updated conversation history
        """
        if conversation_history is None:
            conversation_history = []
        
        # Get agent configuration
        agent_config = get_agent(agent_id)
        model = agent_config["model"]
        temperature = agent_config.get("temperature", 0.7)
        
        # Log which agent is being used
        logger.log_with_timestamp(
            'AI_SERVICE', 
            f'Using agent: {agent_config["display_name"]}',
            f'Model: {model}, Temperature: {temperature}'
        )
        
        # Add the user's message to the conversation history
        conversation_history.append({"role": "user", "content": message})
        
        try:
            # Call the OpenRouter API
            response = self.client.chat.completions.create(
                model=model,
                messages=conversation_history,
                temperature=temperature,
            )
            
            # Validate response structure before accessing properties
            if response and hasattr(response, 'choices') and response.choices:
                # Extract and return the AI's response
                ai_response = response.choices[0].message.content

                # Render any PlantUML diagrams via web service
                if '```plantuml' in ai_response:
                    ai_response = self._render_plantuml(ai_response)
                
                # Add the AI's response to the conversation history for context
                conversation_history.append({"role": "assistant", "content": ai_response})
                
                # Ensure we have a valid response
                if not ai_response or not isinstance(ai_response, str):
                    raise ValueError("Invalid response received from AI model")
                    
                return ai_response, conversation_history
            else:
                # Log the invalid response
                logger.log_with_timestamp('AI_SERVICE_ERROR', f'Invalid response structure: {response}')
                raise ValueError("Invalid or empty response from AI model")
        
        except Exception as e:
            print(f"Error calling OpenRouter API: {e}")
            logger.log_with_timestamp('AI_SERVICE_ERROR', f'Error: {str(e)}')
            error_response = "Sorry, I encountered an error while processing your request."
            conversation_history.append({"role": "assistant", "content": error_response})
            # Ensure we return a valid string response even in error cases
            if not isinstance(error_response, str):
                error_response = str(error_response)
            return error_response, conversation_history

    async def chat_with_file_context(self, message, file_id, conversation_history=None, agent_id=None):
        """
        Handle user message with file context: retrieve relevant chunks and query AI.
        
        Args:
            message (str): The user's message
            file_id (str): ID of the file to use as context
            conversation_history (list, optional): Previous messages in the conversation
            agent_id (str, optional): ID of the agent to use
        """
        if conversation_history is None:
            conversation_history = []
            
        # Get agent configuration
        agent_config = get_agent(agent_id)
        model = agent_config["model"]
        temperature = agent_config.get("temperature", 0.7)
        
        # Log which agent is being used
        logger.log_with_timestamp(
            'AI_SERVICE', 
            f'File context with agent: {agent_config["display_name"]}',
            f'Model: {model}, Temperature: {temperature}'
        )
            
        try:
            # Retrieve relevant chunks
            file_service = FileService()
            # Bỏ từ khóa await vì search_relevant_chunks_in_supabase không phải là hàm async
            chunks = file_service.search_relevant_chunks_in_supabase(message, file_id)
            
            # Kiểm tra xem chunks có phải là None không
            if chunks is None:
                chunks = []
                
            # Log thông tin chunks để debug
            logger.log_with_timestamp('AI_SERVICE', f'Retrieved {len(chunks)} chunks for query: "{message[:30]}..."')
                
            # Build system prompt
            if chunks:
                context = "\n\n---\n\n".join(chunks)
                system_content = f"You are a helpful study assistant. User uploaded a file and asks about its content.\nHere are relevant excerpts from the file:\n{context}\nAnswer based only on the above."
            else:
                system_content = "You are a helpful study assistant. User asked about an uploaded file, but no relevant content was found. Please inform them you cannot find info."
                
            system_message = {"role": "system", "content": system_content}
            
            # Prepare messages
            messages = [system_message]
            for msg in conversation_history:
                if msg.get('role') != 'system':
                    messages.append(msg)
            messages.append({"role":"user","content":message})
            
            # Call OpenRouter
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            
            # Kiểm tra response trước khi truy cập thuộc tính
            if response and hasattr(response, 'choices') and response.choices:
                ai_response = response.choices[0].message.content
            else:
                logger.log_with_timestamp('AI_SERVICE_ERROR', f'Invalid response structure: {response}')
                ai_response = "Sorry, I couldn't process your request properly. Please try again."
                
            # Update history
            conversation_history.append({"role":"user","content":message})
            conversation_history.append({"role":"assistant","content":ai_response})
            return ai_response, conversation_history
            
        except Exception as e:
            logger.log_with_timestamp('AI_SERVICE_ERROR', f'Error in chat_with_file_context: {str(e)}')
            error_response = "Sorry, I encountered an error while processing your request."
            conversation_history.append({"role":"user","content":message})
            conversation_history.append({"role":"assistant","content":error_response})
            return error_response, conversation_history

    async def chat_with_web_search(self, message, conversation_history=None, agent_id=None, chat_id=None):
        """
        Send a message to the AI model with web search results as context.
        
        Args:
            message (str): The user's message
            conversation_history (list, optional): Previous messages in the conversation
            agent_id (str, optional): ID of the agent to use
            chat_id (uuid, optional): The chat session ID to save messages to
        
        Returns:
            tuple: (dict, list) The AI's response with sources and updated conversation history
        """
        if conversation_history is None:
            conversation_history = []
        
        # Default empty sources in case of error
        formatted_sources = []
        
        # Get agent configuration
        agent_config = get_agent(agent_id)
        model = agent_config["model"]
        temperature = agent_config.get("temperature", 0.7)
        
        # Log which agent is being used
        logger.log_with_timestamp(
            'AI_SERVICE', 
            f'Web search with agent: {agent_config["display_name"]}',
            f'Model: {model}, Temperature: {temperature}'
        )
        
        try:
            # Log chat_id if provided for debugging
            if chat_id:
                logger.log_with_timestamp('CHAT_ID', f'Processing web search for chat_id: {chat_id}')
            
            # Save user message to database if chat_id is provided
            user_message_id = None
            if chat_id:
                try:
                    user_message_id = await self.web_search_service.save_message_with_sources(
                        chat_id=chat_id,
                        role="user",
                        content=message
                    )
                    logger.log_with_timestamp('USER_MESSAGE_SAVED', f'User message saved with ID: {user_message_id}')
                except Exception as save_error:
                    logger.log_with_timestamp('USER_MESSAGE_ERROR', f'Failed to save user message: {str(save_error)}')
            
            # Perform web search
            search_results = await self.web_search_service.search(message)
            
            # Log search results for debugging
            logger.log_with_timestamp('SEARCH_RESULTS', f'Found {len(search_results)} results for query: "{message}"')
            
            # Format search results for sources
            if search_results:
                # Format sources consistently for both AI context and database
                formatted_sources = []
                for src in search_results:
                    formatted_src = {
                        'title': src.get('title', 'Untitled'),
                        'url': src.get('url', '#'),
                        'snippet': src.get('snippet', '')
                    }
                    formatted_sources.append(formatted_src)
                
                # Use web scraper to get actual content from URLs (limited to 300 chars each)
                urls_to_scrape = [src['url'] for src in formatted_sources]
                scraped_contents = await self.web_scraper_service.scrape_urls(urls_to_scrape)
                
                # Create context from scraped content when available, fallback to snippets
                search_context = "Thông tin từ các nguồn tìm kiếm web:\n\n"
                
                # Map scraped content back to sources by URL
                scraped_by_url = {item['url']: item['content'] for item in scraped_contents if item['content']}
                
                for i, source in enumerate(formatted_sources, 1):
                    # Use scraped content if available, otherwise use the snippet
                    url = source['url']
                    title = source['title']
                    
                    # Log each source to help with debugging
                    logger.log_with_timestamp('SOURCE_DETAILS', f'Source {i}: {title[:30]}... | URL: {url[:30]}...')
                    
                    if url in scraped_by_url and scraped_by_url[url]:
                        # Add the scraped content to sources for future reference but keep it short
                        source['content'] = scraped_by_url[url]
                        search_context += f"{i}. {title}\nTrích dẫn: {scraped_by_url[url]}\n\n"
                    else:
                        # Use snippet if no scraped content available
                        search_context += f"{i}. {title}\nTrích dẫn: {source['snippet']}\n\n"
                
                # Create system message with context
                system_content = (
                    "Bạn là trợ lý nghiên cứu hữu ích. "
                    "Sử dụng thông tin từ kết quả tìm kiếm web dưới đây để trả lời câu hỏi của người dùng:\n\n"
                    f"{search_context}\n\n"
                    "Trả lời câu hỏi dựa trên các kết quả tìm kiếm này. "
                    "Nếu không tìm thấy thông tin liên quan, hãy nói rõ điều đó. "
                    "Sử dụng cùng ngôn ngữ với câu hỏi của người dùng để trả lời."
                )
            else:
                # Create system message for when no search results are found
                system_content = (
                    "Bạn là trợ lý nghiên cứu hữu ích. "
                    "Không tìm thấy kết quả tìm kiếm web liên quan đến truy vấn của người dùng. "
                    "Trả lời dựa trên kiến thức của bạn, nhưng hãy đề cập rằng bạn không tìm thấy nguồn cụ thể trên web. "
                    "Sử dụng cùng ngôn ngữ với câu hỏi của người dùng để trả lời."
                )
                
            # Create messages array with system message
            messages = [{"role": "system", "content": system_content}]
            
            # Add conversation history (excluding any system messages)
            for msg in conversation_history:
                if msg.get('role') != 'system':
                    messages.append(msg)
            
            # Add the user's message
            messages.append({"role": "user", "content": message})
            
            # Call the OpenRouter API with error handling
            logger.log_with_timestamp('AI_API_CALL', f'Sending request to AI model with {len(messages)} messages')
            try:
                # Log the size of the prompt to help with debugging
                system_size = len(system_content)
                total_size = system_size + len(message) + sum(len(msg.get('content', '')) for msg in conversation_history)
                logger.log_with_timestamp('PROMPT_SIZE', f'System message: {system_size} chars, Total: {total_size} chars')
                
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                )
                
                # Log response received for debugging
                logger.log_with_timestamp('AI_API_RESPONSE', f'Received response with type: {type(response)}')
                
                # Check if we have a valid response
                if not response or not hasattr(response, 'choices') or not response.choices:
                    logger.log_with_timestamp('AI_SERVICE_ERROR', f'Invalid response structure: {response}')
                    raise ValueError("Invalid or empty response from AI model")
                
                # Extract the AI's response
                ai_response = response.choices[0].message.content
                
            except Exception as api_error:
                logger.log_with_timestamp('AI_API_ERROR', f'Error calling AI API: {str(api_error)}')
                ai_response = "Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại."
            
            # Save assistant message with sources to database if chat_id is provided
            if chat_id:
                try:
                    # Log the data being saved for debugging
                    logger.log_with_timestamp('SAVE_ASSISTANT_MESSAGE', 
                                           f'Saving assistant message with {len(formatted_sources)} sources')
                    
                    assistant_message_id = await self.web_search_service.save_message_with_sources(
                        chat_id=chat_id,
                        role="assistant",
                        content=ai_response,
                        sources=formatted_sources
                    )
                    
                    logger.log_with_timestamp('ASSISTANT_MESSAGE_SAVED', 
                                           f'Assistant message saved with ID: {assistant_message_id}')
                except Exception as save_error:
                    logger.log_with_timestamp('SAVE_ERROR', f'Failed to save assistant message: {str(save_error)}')
                    # Try to log the full error details
                    import traceback
                    logger.log_with_timestamp('SAVE_ERROR_TRACE', traceback.format_exc())
            
            # Add metadata to response for frontend to recognize it's a web search result
            web_response = {
                "content": ai_response,
                "role": "assistant",
                "web_search_results": True,
                "sources": formatted_sources
            }
            
            # Log the response being returned
            logger.log_with_timestamp('WEB_SEARCH_RESPONSE', 
                                   f'Response type: {type(web_response)}, Keys: {list(web_response.keys())}')
            logger.log_with_timestamp('WEB_SEARCH_SOURCES', 
                                   f'Returning {len(formatted_sources)} sources to frontend')
            
            # Add the messages to conversation history
            conversation_history.append({"role": "user", "content": message})
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            logger.log_with_timestamp('WEB_SEARCH_COMPLETE', 'Web search complete, returning response')
            return web_response, conversation_history
        
        except Exception as e:
            logger.log_with_timestamp('AI_SERVICE_ERROR', f'Error in chat_with_web_search: {str(e)}')
            error_response = "Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu tìm kiếm của bạn."
            
            # Save error message to database if chat_id is provided
            if chat_id:
                try:
                    await self.web_search_service.save_message_with_sources(
                        chat_id=chat_id,
                        role="assistant",
                        content=error_response
                    )
                except Exception as save_error:
                    logger.log_with_timestamp('MESSAGE_SAVE_ERROR', f'Failed to save error message: {str(save_error)}')
            
            conversation_history.append({"role": "user", "content": message})
            conversation_history.append({"role": "assistant", "content": error_response})
            return {
                "content": error_response,
                "role": "assistant",
                "web_search_results": False,
                "sources": []
            }, conversation_history