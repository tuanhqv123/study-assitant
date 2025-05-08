import { useState, useRef, useEffect } from "react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Send, Paperclip, X, Globe } from "lucide-react";
import { useTheme } from "./ui/theme-provider";

const ChatInput = ({
  onSendMessage,
  isLoading,
  onFileUpload,
  userId,
  activeFileContext,
  clearFileContext,
}) => {
  const [message, setMessage] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);
  const { theme } = useTheme();
  const isLight = theme === "light";

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      const newHeight = Math.min(textarea.scrollHeight, 200);
      textarea.style.height = `${newHeight}px`;
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    onSendMessage(message, webSearchEnabled);
    setMessage("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const toggleWebSearch = () => {
    setWebSearchEnabled(!webSearchEnabled);
  };

  const handleFileButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type (PDF only)
    if (file.type !== "application/pdf") {
      alert("Chỉ hỗ trợ tải lên file PDF");
      return;
    }

    // Maximum file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert("File quá lớn. Kích thước tối đa là 10MB");
      return;
    }

    setIsUploading(true);

    try {
      // Create form data
      const formData = new FormData();
      formData.append("file", file);

      // Sử dụng userId từ props thay vì từ localStorage
      if (userId) {
        formData.append("user_id", userId);
        console.log("Uploading file with user ID:", userId);
      } else {
        console.error("Missing user ID for file upload");
        alert("Không thể tải lên file: Thiếu thông tin người dùng");
        setIsUploading(false);
        return;
      }

      // Send file to backend
      const response = await fetch("http://localhost:8000/file/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      // Call the onFileUpload callback with file ID and name
      if (onFileUpload && data.file_id) {
        onFileUpload(data.file_id, file.name);
      }

      // Reset file input
      e.target.value = null;
    } catch (error) {
      console.error("File upload error:", error);
      alert("Không thể tải lên file. Vui lòng thử lại sau.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div
      className={`border-t ${
        isLight
          ? "border-gray-200 bg-white"
          : "border-[#d1cfc0]/10 bg-opacity-50"
      } py-2`}
    >
      <div className="w-full">
        {activeFileContext && (
          <div
            className={`mb-2 flex items-center justify-between rounded-lg border p-2 ${
              isLight
                ? "border-blue-200 bg-blue-50 text-gray-700"
                : "border-[#d1cfc0]/20 bg-[#2a2a2a] text-[#d1cfc0]/70"
            }`}
          >
            <span className="truncate">
              Đang tham khảo file: <strong>{activeFileContext.name}</strong>
            </span>
            <Button
              type="button"
              size="icon"
              className={`h-6 w-6 shrink-0 rounded-full bg-transparent ${
                isLight
                  ? "text-gray-500 hover:text-gray-700 hover:bg-gray-200"
                  : "text-[#d1cfc0]/70 hover:text-[#d1cfc0] hover:bg-[#333333]"
              }`}
              onClick={clearFileContext}
              title="Xóa file đính kèm"
            >
              <X className="h-4 w-4" />
              <span className="sr-only">Xóa file</span>
            </Button>
          </div>
        )}
        <form
          onSubmit={handleSubmit}
          className={`relative flex w-full items-end gap-2 rounded-lg border p-2 ${
            isLight
              ? "border-gray-300 bg-white shadow-sm"
              : "border-[#d1cfc0]/20 bg-[#1a1a1a]"
          }`}
          style={
            isLight
              ? {
                  background: "white",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                }
              : {}
          }
        >
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden"
            disabled={isLoading || isUploading}
          />

          {/* File attachment button */}
          <Button
            type="button"
            onClick={handleFileButtonClick}
            size="icon"
            className={`h-9 w-9 flex-shrink-0 rounded-full bg-transparent ${
              isLight
                ? "text-gray-500 hover:text-gray-700 hover:bg-gray-100"
                : "text-[#d1cfc0]/70 hover:text-[#d1cfc0] hover:bg-[#2a2a2a]"
            }`}
            disabled={isLoading || isUploading}
            title="Đính kèm file PDF"
          >
            <Paperclip className="h-4 w-4" />
            <span className="sr-only">Đính kèm file</span>
          </Button>

          {/* Web search toggle button */}
          <Button
            type="button"
            onClick={toggleWebSearch}
            size="icon"
            className={`h-9 w-9 flex-shrink-0 rounded-full ${
              webSearchEnabled
                ? isLight
                  ? "bg-blue-100 text-blue-700 hover:bg-blue-200"
                  : "bg-[#2a2a2a] text-blue-400 hover:bg-[#333333]"
                : "bg-transparent " +
                  (isLight
                    ? "text-gray-500 hover:text-gray-700 hover:bg-gray-100"
                    : "text-[#d1cfc0]/70 hover:text-[#d1cfc0] hover:bg-[#2a2a2a]")
            }`}
            disabled={isLoading || isUploading}
            title={webSearchEnabled ? "Tắt tìm kiếm web" : "Bật tìm kiếm web"}
          >
            <Globe className="h-4 w-4" />
            <span className="sr-only">Tìm kiếm web</span>
          </Button>

          <Textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhắn tin với Study Assistant AI..."
            className={`flex-1 min-h-[40px] max-h-[200px] resize-none border-0 bg-transparent p-2 ${
              isLight
                ? "text-gray-800 placeholder-gray-400"
                : "text-[#d1cfc0] placeholder-[#d1cfc0]/50"
            } focus:outline-none focus-visible:ring-0 focus:ring-0 focus-within:ring-0`}
            disabled={isLoading || isUploading}
            rows={1}
          />

          <Button
            type="submit"
            disabled={!message.trim() || isLoading || isUploading}
            size="icon"
            className={`h-9 w-9 flex-shrink-0 rounded-full ${
              isLight
                ? "bg-blue-600 text-white hover:bg-blue-700 border border-blue-700"
                : "bg-[#2a2a2a] text-[#d1cfc0] hover:bg-[#333333] border border-[#d1cfc0]/10"
            }`}
          >
            <Send className="h-4 w-4" />
            <span className="sr-only">Gửi</span>
          </Button>

          {/* Upload status indicator */}
          {isUploading && (
            <div
              className={`absolute -top-10 left-0 right-0 flex items-center justify-center p-2 rounded-md text-sm ${
                isLight
                  ? "bg-blue-50 text-blue-700"
                  : "bg-[#2a2a2a] text-[#d1cfc0]/70"
              }`}
            >
              <div
                className={`h-2 w-2 animate-pulse rounded-full mr-2 ${
                  isLight ? "bg-blue-600" : "bg-blue-400"
                }`}
              ></div>
              Đang tải lên file...
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default ChatInput;
