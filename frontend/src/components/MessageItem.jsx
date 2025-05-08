import React, { useState } from "react";
import { cn } from "../lib/utils";
import { Avatar, AvatarImage } from "./ui/avatar";
import { Button } from "./ui/button";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check, Globe } from "lucide-react";
import * as Tooltip from "@radix-ui/react-tooltip";
import { useTheme } from "./ui/theme-provider";

const MessageItem = ({ message }) => {
  const isUser = message.role === "user";
  const [showCopy, setShowCopy] = useState(false);
  const [copied, setCopied] = useState(false);
  const { theme } = useTheme();
  const isLight = theme === "light";

  // Check if message has content
  const hasContent = message.content && message.content.trim() !== "";

  // Check if message has web search results
  const hasWebSources =
    !isUser &&
    hasContent &&
    (message.content?.includes("URL:") ||
      message.content?.includes("Source") ||
      message.web_search_results === true ||
      (message.sources &&
        Array.isArray(message.sources) &&
        message.sources.length > 0));

  // Extract sources from message if available
  const sources = message.sources || [];

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content || "");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Web search source list component
  const WebSearchSources = ({ sources }) => {
    if (!sources || sources.length === 0) return null;

    return (
      <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
        <div className="font-medium text-gray-700 dark:text-gray-300">
          Nguồn tham khảo:
        </div>
        <ul className="list-none">
          {sources.map((source, index) => (
            <li key={index} className="text-md flex items-start gap-2">
              <span className="font-medium text-gray-600 dark:text-gray-400">
                {index + 1}:
              </span>
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:underline"
              >
                {source.title}
              </a>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div
      className={cn(
        "flex w-full gap-3 p-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <Avatar>
          <AvatarImage
            src="/src/assets/avatars/assistant-avatar.svg"
            alt="AI"
          />
        </Avatar>
      )}
      <div
        className="relative group max-w-[70%]"
        onMouseEnter={() => setShowCopy(true)}
        onMouseLeave={() => setShowCopy(false)}
      >
        {/* Message Container */}
        {!isUser && isLight ? (
          <div className="p-[1px] rounded-[0.75rem] bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500">
            <div className="bg-white p-4 rounded-[0.7rem]">
              {hasWebSources && (
                <div className="flex items-center gap-1 text-xs text-blue-600 mb-2">
                  <Globe className="h-3 w-3" />
                  <span>Kết quả từ tìm kiếm web</span>
                </div>
              )}

              {!hasContent ? (
                <div className="prose max-w-none text-gray-500 italic">
                  <p>Không có nội dung</p>
                </div>
              ) : (
                <div className="prose max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                  </ReactMarkdown>

                  {/* Display web search sources */}
                  {hasWebSources && <WebSearchSources sources={sources} />}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div
            className={cn(
              "flex flex-col gap-2 px-4 py-3 rounded-[0.75rem]",
              isUser
                ? isLight
                  ? "bg-secondary text-gray-800 border border-blue-500 shadow-sm"
                  : "bg-secondary text-foreground border border-border/50"
                : "bg-card text-foreground border border-border/50"
            )}
          >
            {isUser ? (
              <p
                className={`text-base break-words whitespace-pre-wrap ${
                  isLight ? "text-gray-800" : ""
                }`}
              >
                {message.content}
              </p>
            ) : (
              <>
                {hasWebSources && (
                  <div className="flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 mb-2">
                    <Globe className="h-3 w-3" />
                    <span>Kết quả từ tìm kiếm web</span>
                  </div>
                )}

                {!hasContent ? (
                  <div className="prose prose-invert dark:prose-invert max-w-none text-gray-400 italic">
                    <p>Không có nội dung</p>
                  </div>
                ) : (
                  <div className="prose prose-invert dark:prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>

                    {/* Display web search sources for dark theme */}
                    {hasWebSources && <WebSearchSources sources={sources} />}
                  </div>
                )}
              </>
            )}
          </div>
        )}
        {showCopy && !isUser && hasContent && (
          <Tooltip.Provider>
            <Tooltip.Root>
              <Tooltip.Trigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className={`absolute -right-1 -bottom-1 h-6 w-6 rounded-sm opacity-0 group-hover:opacity-100 transition-opacity ${
                    isLight
                      ? "bg-gray-100 hover:bg-gray-200 text-gray-700"
                      : "bg-muted hover:bg-accent text-muted-foreground"
                  }`}
                  onClick={handleCopy}
                >
                  {copied ? (
                    <Check className="h-3 w-3" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                </Button>
              </Tooltip.Trigger>
              <Tooltip.Portal>
                <Tooltip.Content
                  className={`text-xs px-2 py-1 rounded border ${
                    isLight
                      ? "bg-white text-gray-800 border-gray-200"
                      : "bg-card text-foreground border-border"
                  }`}
                  sideOffset={5}
                >
                  {copied ? "Copied!" : "Copy to clipboard"}
                  <Tooltip.Arrow
                    className={isLight ? "fill-white" : "fill-card"}
                  />
                </Tooltip.Content>
              </Tooltip.Portal>
            </Tooltip.Root>
          </Tooltip.Provider>
        )}
      </div>
      {isUser && (
        <Avatar>
          <AvatarImage src="/src/assets/avatars/user-avatar.svg" alt="User" />
        </Avatar>
      )}
    </div>
  );
};

export default MessageItem;
