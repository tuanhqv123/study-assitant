import datetime

class Logger:
    @staticmethod
    def get_timestamp():
        """Get current timestamp in a readable format"""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def log_with_timestamp(message_type, content, additional_info=None):
        """
        Log messages with timestamps
        
        Args:
            message_type (str): Type of message being logged
            content (str): Main content of the message
            additional_info (str, optional): Any additional information to include
        
        Returns:
            str: The timestamp when the message was logged
        """
        timestamp = Logger.get_timestamp()
        log_message = f"[{timestamp}] {message_type}: {content[:100]}{'...' if len(content) > 100 else ''}"
        
        if additional_info:
            log_message += f" | Additional info: {additional_info}"
        
        print(log_message)
        return timestamp