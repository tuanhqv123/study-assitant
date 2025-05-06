import asyncio
from openai import OpenAI
from .file_service import FileService
import os
import httpx
from ..utils.logger import Logger
import zlib

logger = Logger()

class AiService:
    def __init__(self):
        # OpenRouter API Configuration
        self.OPENROUTER_API_KEY = "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"
        self.MODEL = "mistralai/mistral-small-24b-instruct-2501:free" 
        
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

    def chat_with_ai(self, message, conversation_history=None):
        """
        Send a message to the AI model and get a response.
        
        Args:
            message (str): The user's message
            conversation_history (list, optional): Previous messages in the conversation
        
        Returns:
            tuple: (str, list) The AI's response and updated conversation history
        """
        if conversation_history is None:
            conversation_history = []
        
        # Add the user's message to the conversation history
        conversation_history.append({"role": "user", "content": message})
        
        try:
            # Call the OpenRouter API
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=conversation_history,
                temperature=0.7,
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

    async def chat_with_file_context(self, message, file_id, conversation_history=None):
        """
        Handle user message with file context: retrieve relevant chunks and query AI.
        """
        if conversation_history is None:
            conversation_history = []
            
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
                model=self.MODEL,
                messages=messages,
                temperature=0.7,
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