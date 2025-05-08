import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabase";
import MessageItem from "./MessageItem";
import ChatInput from "./ChatInput";
import Settings from "./Settings";
import AgentSelector from "./AgentSelector";
import { X, Settings as SettingsIcon } from "lucide-react";
// Import theme toggle
import { ThemeToggle } from "./ui/theme-toggle";

const ChatInterface = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [chatSessions, setChatSessions] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [activeFileContext, setActiveFileContext] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
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

          // Load agent preference if exists
          const { data: chatData } = await supabase
            .from("chat_sessions")
            .select("agent_id")
            .eq("id", data[0].id)
            .single();

          if (chatData && chatData.agent_id) {
            setSelectedAgent(chatData.agent_id);
          }
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

    // Debug sources
    if (data && data.length > 0) {
      console.log("Loaded messages from DB:", data.length);
      // Kiểm tra xem có message nào có sources không
      const messagesWithSources = data.filter(
        (msg) => msg.sources && msg.sources.length > 0
      );
      console.log("Messages with sources:", messagesWithSources.length);
      if (messagesWithSources.length > 0) {
        console.log("First message with sources:", messagesWithSources[0]);
      }
    }

    setMessages(data || []);

    // Load agent preference when switching chats
    const { data: chatData } = await supabase
      .from("chat_sessions")
      .select("agent_id")
      .eq("id", chatId)
      .single();

    if (chatData && chatData.agent_id) {
      setSelectedAgent(chatData.agent_id);
    } else {
      setSelectedAgent(null); // Reset to default if no agent is set
    }
  };

  // New function to create a chat session
  const createNewChatSession = async (userId) => {
    const { data, error } = await supabase
      .from("chat_sessions")
      .insert([{ user_id: userId, agent_id: selectedAgent }])
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

  // Handle agent selection change
  const handleAgentChange = async (agentId) => {
    setSelectedAgent(agentId);

    // Save the selected agent to the current chat session
    if (activeChat) {
      try {
        await supabase
          .from("chat_sessions")
          .update({ agent_id: agentId })
          .eq("id", activeChat);

        // Add a system message indicating agent change
        const { data: agentData } = await fetch(
          "http://localhost:8000/agents"
        ).then((res) => res.json());
        const agents = agentData?.agents || [];
        const newAgent = agents.find((a) => a.id === agentId);

        if (newAgent) {
          setMessages((prev) => [
            ...prev,
            {
              role: "system",
              content: `Switched to ${newAgent.display_name} ${newAgent.avatar}. ${newAgent.description}`,
              chat_id: activeChat,
              created_at: new Date().toISOString(),
            },
          ]);
        }
      } catch (error) {
        console.error("Error updating agent for chat session:", error);
      }
    }
  };

  // Handle file upload success from ChatInput
  const handleFileUpload = (fileId, fileName) => {
    setActiveFileContext({ id: fileId, name: fileName });
    setMessages((prev) => [
      ...prev,
      {
        role: "system",
        content: `Đã tải file "${fileName}" lên. Bạn có thể hỏi về nội dung file này.`,
      },
    ]);
  };

  // Clear file context when user clicks remove
  const clearFileContext = async () => {
    if (!activeFileContext) return;
    try {
      await fetch(`/api/files/${activeFileContext.id}?user_id=${user.id}`, {
        method: "DELETE",
      });
      setMessages((prev) => [
        ...prev,
        { role: "system", content: "Đã xóa ngữ cảnh file." },
      ]);
    } catch (e) {
      console.error("Error deleting file context:", e);
    }
    setActiveFileContext(null);
  };

  // Update sendMessage to include web_search_enabled
  const handleSendMessage = async (message, webSearchEnabled) => {
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
      const { error: insertError } = await supabase
        .from("messages")
        .insert([newMessage]);

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

      if (credentialsError && credentialsError.code !== "PGRST116") {
        // PGRST116 is "No rows found", which is expected for new users
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
        file_id: activeFileContext?.id,
        agent_id: selectedAgent,
        web_search_enabled: webSearchEnabled || false,
        chat_id: activeChat, // Thêm chat_id để backend có thể lưu tin nhắn
      };

      console.log("Sending chat request with user ID:", user?.id);
      if (credentials) {
        console.log("University credentials found for user");
      } else {
        console.log("No university credentials found for user");
      }

      if (webSearchEnabled) {
        console.log("Web search is enabled for this request");
      }

      try {
        const response = await fetch("http://localhost:8000/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`Server responded with status: ${response.status}`);
        }

        let data;
        try {
          data = await response.json();
        } catch (jsonError) {
          console.error("JSON parsing error:", jsonError);
          throw new Error("Invalid response format from server");
        }

        // Add assistant's response to messages
        const assistantMessage = {
          role: "assistant",
          content: data.response,
          chat_id: activeChat, // Gắn chat_id của phiên chat hiện tại
          created_at: new Date().toISOString(),
        };

        // If this is a web search result, add the sources
        if (data.web_search_results && data.sources) {
          assistantMessage.sources = data.sources;
          assistantMessage.web_search_results = true;
        }

        setMessages((prev) => [...prev, assistantMessage]);

        // Save assistant's message to Supabase
        const { error: assistantInsertError } = await supabase
          .from("messages")
          .insert([assistantMessage]);

        if (assistantInsertError) {
          console.error(
            "Error saving assistant message to database:",
            assistantInsertError
          );
          console.log("Failed to save message:", assistantMessage);
        } else {
          console.log(
            "Successfully saved assistant message with sources:",
            assistantMessage.sources ? assistantMessage.sources.length : 0
          );
        }
      } catch (requestError) {
        console.error("Error communicating with backend:", requestError);

        // Show friendly error message in chat
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này. Vui lòng thử lại sau hoặc liên hệ hỗ trợ kỹ thuật.",
            chat_id: activeChat,
            created_at: new Date().toISOString(),
          },
        ]);

        // Save error message to database
        await supabase.from("messages").insert([
          {
            role: "assistant",
            content:
              "Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này. Vui lòng thử lại sau hoặc liên hệ hỗ trợ kỹ thuật.",
            chat_id: activeChat,
            created_at: new Date().toISOString(),
          },
        ]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      // Show error in chat
      const errorMessage = {
        role: "assistant",
        content: "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
        chat_id: activeChat,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);

      // Try to save the error message to the database
      try {
        await supabase.from("messages").insert([errorMessage]);
      } catch (dbError) {
        console.error("Failed to save error message to database:", dbError);
      }
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
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar - fixed height, no scrolling */}
      <div className="w-64 bg-card border-r border-border flex flex-col h-screen overflow-hidden">
        <div className="flex-1 flex flex-col">
          {/* Logo */}
          <div className="flex justify-center items-center mt-6 mb-2">
            <h1 className="font-['Montserrat',sans-serif] font-semibold text-foreground text-2xl tracking-wide">
              <em>&#8220;forPTITer&#8221;</em>
            </h1>
          </div>
          <button
            onClick={handleNewChat}
            className="m-4 p-2 bg-secondary rounded-lg text-foreground hover:bg-accent border border-border"
          >
            + New Chat
          </button>
          <div className="overflow-y-auto flex-1">
            {chatSessions.map((session) => (
              <div
                key={session.id}
                className={`p-3 hover:bg-secondary cursor-pointer relative group ${
                  activeChat === session.id ? "bg-accent" : ""
                }`}
                onClick={() => {
                  setActiveChat(session.id);
                  loadMessages(session.id);
                }}
              >
                <p className="text-sm text-muted-foreground truncate pr-7">
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
                             text-muted-foreground hover:text-foreground
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
          <div className="p-4 border-t border-border mt-auto">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground truncate">
                {user.email}
              </p>
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
        {/* Sticky header */}
        <div className="sticky top-0 bg-card/90 backdrop-blur-sm border-b border-border z-10 shadow-sm">
          <div className="flex items-center justify-between px-8 py-3">
            <div className="flex items-center gap-3">
              <div className="w-50">
                <AgentSelector
                  selectedAgent={selectedAgent}
                  onAgentChange={handleAgentChange}
                />
              </div>
            </div>
            <div className="flex items-center gap-3">
              {activeFileContext && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-accent/50 rounded-md text-xs">
                  <span className="truncate max-w-[200px]">
                    {activeFileContext.name}
                  </span>
                  <button
                    onClick={clearFileContext}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              )}
              <div className="flex items-center space-x-4">
                <ThemeToggle />
                <button
                  onClick={() => setSettingsOpen(true)}
                  className="p-1.5 rounded-full bg-secondary hover:bg-accent transition-colors"
                  aria-label="Settings"
                >
                  <SettingsIcon className="h-4 w-4 text-muted-foreground" />
                </button>
              </div>
            </div>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto pb-32">
          <div className="mx-auto p-4">
            {messages.map((message, index) => (
              <MessageItem key={index} message={message} />
            ))}
            {isLoading && (
              <div className="flex items-center gap-2 p-4">
                <div className="flex space-x-1">
                  <div
                    className="h-2 w-2 animate-bounce rounded-full bg-muted"
                    style={{ animationDelay: "0ms" }}
                  />
                  <div
                    className="h-2 w-2 animate-bounce rounded-full bg-muted"
                    style={{ animationDelay: "150ms" }}
                  />
                  <div
                    className="h-2 w-2 animate-bounce rounded-full bg-muted"
                    style={{ animationDelay: "300ms" }}
                  />
                </div>
                <span className="text-sm text-muted-foreground">
                  Study Assistant AI đang trả lời...
                </span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
        <div className="absolute bottom-0 left-64 right-0 bg-background">
          <div className="mx-auto max-w-2xl px-4 pb-4">
            <ChatInput
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              onFileUpload={handleFileUpload}
              userId={user?.id}
              activeFileContext={activeFileContext}
              clearFileContext={clearFileContext}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
