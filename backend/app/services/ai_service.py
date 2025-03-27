from openai import OpenAI

class AiService:
    def __init__(self):
        # OpenRouter API Configuration
        self.OPENROUTER_API_KEY = "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"
        self.MODEL = "qwen/qwen-2-7b-instruct:free"  # Using Qwen 2 7B model (free tier)
        
        # Initialize OpenAI client with OpenRouter configuration
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.OPENROUTER_API_KEY,
        )

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
            
            # Extract and return the AI's response
            ai_response = response.choices[0].message.content
            
            # Add the AI's response to the conversation history for context
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Ensure we have a valid response
            if not ai_response or not isinstance(ai_response, str):
                raise ValueError("Invalid response received from AI model")
                
            return ai_response, conversation_history
        
        except Exception as e:
            print(f"Error calling OpenRouter API: {e}")
            error_response = "Sorry, I encountered an error while processing your request."
            conversation_history.append({"role": "assistant", "content": error_response})
            # Ensure we return a valid string response even in error cases
            if not isinstance(error_response, str):
                error_response = str(error_response)
            return error_response, conversation_history