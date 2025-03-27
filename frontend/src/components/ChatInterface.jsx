import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabase";
import MessageItem from "./MessageItem";
import ChatInput from "./ChatInput";
import Settings from "./Settings";
import { X, Settings as SettingsIcon } from "lucide-react"; // Import Settings icon

const ChatInterface = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [chatSessions, setChatSessions] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const checkAuth = async () => {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (user) {
        setUser(user);
        // Load chat sessions
        const { data, error: sessionsError } = await supabase
          .from("chat_sessions")
          .select("*")
          .eq("user_id", user.id)
          .order("created_at", { ascending: false });

        if (sessionsError) {
          console.error("Error loading chat sessions:", sessionsError);
          return;
        }

        setChatSessions(data || []);

        if (data?.length > 0) {
          // Load most recent chat
          setActiveChat(data[0].id);
          loadMessages(data[0].id);
        } else {
          // Create a new chat session if user has none
          await createNewChatSession(user.id);
        }
      }
    };
    checkAuth();
  }, [navigate]);

  const loadMessages = async (chatId) => {
    const { data } = await supabase
      .from("messages")
      .select("*")
      .eq("chat_id", chatId)
      .order("created_at", { ascending: true });
    setMessages(data || []);
  };

  // New function to create a chat session
  const createNewChatSession = async (userId) => {
    const { data, error } = await supabase
      .from("chat_sessions")
      .insert([{ user_id: userId }])
      .select()
      .single();

    if (error) {
      console.error("Error creating new chat session:", error);
      return null;
    }

    setChatSessions((prev) => [data, ...prev]);
    setActiveChat(data.id);
    setMessages([]);
    return data;
  };

  // Enhanced function to handle chat session limit
  const handleNewChat = async () => {
    // Check if user has reached the limit of 10 chat sessions
    if (chatSessions.length >= 10) {
      // Find the oldest chat session
      const oldestSession = [...chatSessions].sort(
        (a, b) => new Date(a.created_at) - new Date(b.created_at)
      )[0];

      // Delete the oldest chat session
      await supabase.from("chat_sessions").delete().eq("id", oldestSession.id);

      // Also delete associated messages
      await supabase.from("messages").delete().eq("chat_id", oldestSession.id);

      // Remove from state
      setChatSessions((prev) =>
        prev.filter((session) => session.id !== oldestSession.id)
      );
    }

    // Create new chat session
    await createNewChatSession(user.id);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate("/login");
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Update sendMessage to save messages to database
  const handleSendMessage = async (message) => {
    if (!message.trim() || isLoading) return;
    setIsLoading(true);

    try {
      const newMessage = {
        role: "user",
        content: message,
        chat_id: activeChat, // Gắn chat_id của phiên chat hiện tại
        created_at: new Date().toISOString(),
      };

      // Add message to UI immediately
      setMessages((prev) => [...prev, newMessage]);

      // Save message to Supabase
      const { error: insertError } = await supabase.from("messages").insert([newMessage]);

      if (insertError) {
        console.error("Error saving message to database:", insertError);
        throw new Error("Failed to save message to database");
      }

      // Get university credentials
      const { data: credentials, error: credentialsError } = await supabase
        .from("university_credentials")
        .select(
          "university_username, university_password, access_token, refresh_token, token_expiry"
        )
        .eq("user_id", user?.id)
        .single();

      if (credentialsError) {
        console.error(
          "Error loading university credentials:",
          credentialsError
        );
      }

      // Prepare the request payload with user ID and credentials
      const payload = {
        message,
        conversation_history: messages,
        user_id: user?.id || null,
        university_credentials: credentials || null,
      };

      console.log("Sending chat request with user ID:", user?.id);
      if (credentials) {
        console.log("University credentials found for user");
      } else {
        console.log("No university credentials found for user");
      }

      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      let data;
      try {
        data = await response.json();
      } catch (jsonError) {
        console.error("JSON parsing error:", jsonError);
        throw new Error("Invalid response format from server");
      }

      if (response.ok) {
        // Add assistant's response to messages
        const assistantMessage = {
          role: "assistant",
          content: data.response,
          chat_id: activeChat, // Gắn chat_id của phiên chat hiện tại
          created_at: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, assistantMessage]);

        // Save assistant's message to Supabase
        const { error: assistantInsertError } = await supabase
          .from("messages")
          .insert([assistantMessage]);

        if (assistantInsertError) {
          console.error("Error saving assistant message to database:", assistantInsertError);
        }
      } else {
        throw new Error(data.error || "Failed to get response");
      }
    } catch (error) {
      console.error("Error sending message:", error);
      // Show error in chat
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Add function to delete a chat session
  const handleDeleteChat = async (sessionId, e) => {
    // Prevent click event from bubbling up to parent
    e.stopPropagation();

    // If this is the active chat, switch to another chat if available
    if (activeChat === sessionId) {
      const remainingSessions = chatSessions.filter((s) => s.id !== sessionId);
      if (remainingSessions.length > 0) {
        setActiveChat(remainingSessions[0].id);
        loadMessages(remainingSessions[0].id);
      } else {
        setActiveChat(null);
        setMessages([]);
      }
    }

    // Delete messages first (foreign key constraint)
    await supabase.from("messages").delete().eq("chat_id", sessionId);

    // Delete the session
    await supabase.from("chat_sessions").delete().eq("id", sessionId);

    // Update state to remove the deleted session
    setChatSessions((prev) =>
      prev.filter((session) => session.id !== sessionId)
    );
  };

  return (
    <div className="flex h-screen bg-[#1f1f1f] overflow-hidden">
      {/* Sidebar - fixed height, no scrolling */}
      <div className="w-64 bg-[#1a1a1a] border-r border-[#d1cfc0]/10 flex flex-col h-screen overflow-hidden">
        <div className="flex-1 flex flex-col">
          {/* Logo */}
          <div className="flex justify-center items-center mt-6 mb-2">
            <h1 className="font-['Montserrat',sans-serif] font-semibold text-[#d1cfc0] text-2xl tracking-wide">
              <em>&#8220;forPTITer&#8221;</em>
            </h1>
          </div>
          <button
            onClick={handleNewChat}
            className="m-4 p-2 bg-[#2a2a2a] rounded-lg text-[#d1cfc0] hover:bg-[#333333] border border-[#d1cfc0]/10"
          >
            + New Chat
          </button>
          <div className="overflow-y-auto flex-1">
            {chatSessions.map((session) => (
              <div
                key={session.id}
                className={`p-3 hover:bg-[#2a2a2a] cursor-pointer relative group ${
                  activeChat === session.id ? "bg-[#333333]" : ""
                }`}
                onClick={() => {
                  setActiveChat(session.id);
                  loadMessages(session.id);
                }}
              >
                <p className="text-sm text-[#d1cfc0]/80 truncate pr-7">
                  Chat {new Date(session.created_at).toLocaleDateString()}{" "}
                  {new Date(session.created_at).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
                {/* Simple X icon that appears on hover */}
                <button
                  onClick={(e) => handleDeleteChat(session.id, e)}
                  className="absolute top-1/2 right-2 -translate-y-1/2 
                             text-[#d1cfc0]/60 hover:text-[#d1cfc0]/90
                             opacity-0 group-hover:opacity-100
                             transition-opacity"
                  aria-label="Delete chat"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
        {user && (
          <div className="p-4 border-t border-[#d1cfc0]/10 mt-auto">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-[#d1cfc0]/80 truncate">{user.email}</p>
              <button
                onClick={() => setSettingsOpen(true)}
                className="p-1.5 rounded-full bg-[#2a2a2a] hover:bg-[#333333] transition-colors"
                aria-label="Settings"
              >
                <SettingsIcon className="h-4 w-4 text-[#d1cfc0]/70" />
              </button>
            </div>
            <button
              onClick={handleLogout}
              className="w-full p-2 bg-red-500/10 text-red-500 rounded-lg hover:bg-red-500/20"
            >
              Log Out
            </button>
          </div>
        )}
      </div>
      {/* Add Settings modal */}
      {user && (
        <Settings
          isOpen={settingsOpen}
          onClose={() => setSettingsOpen(false)}
          userId={user.id}
        />
      )}
      {/* Chat Area - scrollable area with fixed position */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <div className="flex-1 overflow-y-auto pb-32">
          <div className="mx-auto p-4">
            {messages.map((message, index) => (
              <MessageItem key={index} message={message} />
            ))}
            {isLoading && (
              <div className="flex items-center gap-2 p-4">
                <div className="flex space-x-1">
                  <div
                    className="h-2 w-2 animate-bounce rounded-full bg-[#d1cfc0]/30"
                    style={{ animationDelay: "0ms" }}
                  />
                  <div
                    className="h-2 w-2 animate-bounce rounded-full bg-[#d1cfc0]/30"
                    style={{ animationDelay: "150ms" }}
                  />
                  <div
                    className="h-2 w-2 animate-bounce rounded-full bg-[#d1cfc0]/30"
                    style={{ animationDelay: "300ms" }}
                  />
                </div>
                <span className="text-sm text-[#d1cfc0]/70">
                  Study Assistant AI đang trả lời...
                </span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
        <div className="absolute bottom-0 left-64 right-0 bg-[#1f1f1f]">
          <div className="mx-auto max-w-3xl">
            <ChatInput
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
