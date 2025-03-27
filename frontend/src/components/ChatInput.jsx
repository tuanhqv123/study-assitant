import { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Send } from 'lucide-react';

const ChatInput = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const newHeight = Math.min(textarea.scrollHeight, 200);
      textarea.style.height = `${newHeight}px`;
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;
    
    onSendMessage(message);
    setMessage('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t border-[#d1cfc0]/10 bg-opacity-50 px-4 py-2">
      <div className="mx-auto max-w-3xl">
        <form 
          onSubmit={handleSubmit} 
          className="relative mx-auto flex max-w-[85%] items-end gap-2 rounded-lg border border-[#d1cfc0]/20 bg-[#1a1a1a] p-2"
        >
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhắn tin với Study Assistant AI..."
            className="min-h-[40px] max-h-[200px] resize-none border-0 bg-transparent p-2 text-[#d1cfc0] placeholder-[#d1cfc0]/50 focus:outline-none focus-visible:ring-0 focus:ring-0 focus-within:ring-0"
            disabled={isLoading}
            rows={1}
          />
          <Button 
            type="submit" 
            disabled={!message.trim() || isLoading} 
            size="icon"
            className="h-9 w-9 shrink-0 rounded-full bg-[#2a2a2a] text-[#d1cfc0] hover:bg-[#333333] border border-[#d1cfc0]/10"
          >
            <Send className="h-4 w-4" />
            <span className="sr-only">Gửi</span>
          </Button>
        </form>
      </div>
    </div>
  );
};

export default ChatInput;