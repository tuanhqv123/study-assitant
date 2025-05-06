import React, { useState } from "react";
import { cn } from "../lib/utils";
import { Avatar, AvatarImage } from "./ui/avatar";
import { Button } from "./ui/button";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check } from "lucide-react";
import * as Tooltip from "@radix-ui/react-tooltip";
import { useTheme } from "./ui/theme-provider";

const MessageItem = ({ message }) => {
  const isUser = message.role === "user";
  const [showCopy, setShowCopy] = useState(false);
  const [copied, setCopied] = useState(false);
  const { theme } = useTheme();
  const isLight = theme === "light";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
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
        {/* Message Container - với kiểu bo tròn khác */}
        {!isUser && isLight ? (
          <div className="p-[1px] rounded-[0.75rem] bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500">
            <div className="bg-white p-4 rounded-[0.7rem]">
              <div
                className={`prose max-w-none ${
                  isLight ? "prose" : "prose-invert dark:prose-invert"
                }`}
              >
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Customize how code blocks are rendered
                    code({ inline, className, children, ...props }) {
                      // Handle regular code blocks
                      if (inline) {
                        return (
                          <code
                            className={`rounded px-1 py-0.5 text-base ${
                              isLight ? "bg-gray-100" : "bg-muted"
                            }`}
                            {...props}
                          >
                            {children}
                          </code>
                        );
                      }

                      // Special handling for PlantUML blocks
                      if (className && /language-plantuml/.test(className)) {
                        return (
                          <div className="flex flex-col md:flex-row gap-4 my-4">
                            <pre
                              className={`!mt-0 flex-1 overflow-x-auto rounded p-2 ${
                                isLight
                                  ? "bg-gray-100 text-gray-800"
                                  : "bg-muted"
                              }`}
                            >
                              <code className="block whitespace-pre-wrap text-base">
                                {children}
                              </code>
                            </pre>
                            <div className="flex-1 flex items-center justify-center">
                              {/* Find any PlantUML images that might be in the message */}
                              {message.content.includes(
                                "![Diagram](https://www.plantuml.com/plantuml/png/"
                              ) && (
                                <img
                                  src={
                                    message.content.match(
                                      /!\[Diagram\]\((https:\/\/www\.plantuml\.com\/plantuml\/png\/[^)]+)\)/
                                    )?.[1]
                                  }
                                  alt="PlantUML diagram"
                                  className="max-w-full h-auto border rounded shadow-sm"
                                />
                              )}
                            </div>
                          </div>
                        );
                      }

                      // Regular code blocks
                      return (
                        <pre className="!mt-0 max-w-full overflow-x-auto">
                          <code
                            className={`block rounded p-1 my-2 whitespace-pre-wrap text-base ${
                              isLight ? "bg-gray-100" : "bg-muted"
                            }`}
                            {...props}
                          >
                            {children}
                          </code>
                        </pre>
                      );
                    },
                    // Prevent rendering Markdown image for PlantUML to avoid duplicate image
                    img({ src, alt, ...props }) {
                      // Skip rendering images that are PlantUML diagrams
                      if (
                        src &&
                        src.includes("plantuml.com/plantuml/png/") &&
                        alt === "Diagram"
                      ) {
                        return null;
                      }
                      return <img src={src} alt={alt} {...props} />;
                    },
                    p({ children }) {
                      return (
                        <p
                          className={`text-base mb-4 last:mb-0 break-words ${
                            isLight ? "text-gray-800" : ""
                          }`}
                        >
                          {children}
                        </p>
                      );
                    },
                    // Add styling for other elements
                    h1({ children }) {
                      return (
                        <h1
                          className={`text-xl font-bold mb-4 break-words ${
                            isLight ? "text-gray-900" : ""
                          }`}
                        >
                          {children}
                        </h1>
                      );
                    },
                    h2({ children }) {
                      return (
                        <h2
                          className={`text-lg font-bold mb-3 break-words ${
                            isLight ? "text-gray-900" : ""
                          }`}
                        >
                          {children}
                        </h2>
                      );
                    },
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
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
              <div
                className={`prose max-w-none ${
                  isLight ? "prose" : "prose-invert dark:prose-invert"
                }`}
              >
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Customize how code blocks are rendered
                    code({ inline, className, children, ...props }) {
                      // Handle regular code blocks
                      if (inline) {
                        return (
                          <code
                            className={`rounded px-1 py-0.5 text-base ${
                              isLight ? "bg-gray-100" : "bg-muted"
                            }`}
                            {...props}
                          >
                            {children}
                          </code>
                        );
                      }

                      // Special handling for PlantUML blocks
                      if (className && /language-plantuml/.test(className)) {
                        return (
                          <div className="flex flex-col md:flex-row gap-4 my-4">
                            <pre
                              className={`!mt-0 flex-1 overflow-x-auto rounded p-2 ${
                                isLight
                                  ? "bg-gray-100 text-gray-800"
                                  : "bg-muted"
                              }`}
                            >
                              <code className="block whitespace-pre-wrap text-base">
                                {children}
                              </code>
                            </pre>
                            <div className="flex-1 flex items-center justify-center">
                              {/* Find any PlantUML images that might be in the message */}
                              {message.content.includes(
                                "![Diagram](https://www.plantuml.com/plantuml/png/"
                              ) && (
                                <img
                                  src={
                                    message.content.match(
                                      /!\[Diagram\]\((https:\/\/www\.plantuml\.com\/plantuml\/png\/[^)]+)\)/
                                    )?.[1]
                                  }
                                  alt="PlantUML diagram"
                                  className="max-w-full h-auto border rounded shadow-sm"
                                />
                              )}
                            </div>
                          </div>
                        );
                      }

                      // Regular code blocks
                      return (
                        <pre className="!mt-0 max-w-full overflow-x-auto">
                          <code
                            className={`block rounded p-1 my-2 whitespace-pre-wrap text-base ${
                              isLight ? "bg-gray-100" : "bg-muted"
                            }`}
                            {...props}
                          >
                            {children}
                          </code>
                        </pre>
                      );
                    },
                    // Prevent rendering Markdown image for PlantUML to avoid duplicate image
                    img({ src, alt, ...props }) {
                      // Skip rendering images that are PlantUML diagrams
                      if (
                        src &&
                        src.includes("plantuml.com/plantuml/png/") &&
                        alt === "Diagram"
                      ) {
                        return null;
                      }
                      return <img src={src} alt={alt} {...props} />;
                    },
                    p({ children }) {
                      return (
                        <p
                          className={`text-base mb-4 last:mb-0 break-words ${
                            isLight ? "text-gray-800" : ""
                          }`}
                        >
                          {children}
                        </p>
                      );
                    },
                    // Add styling for other elements
                    h1({ children }) {
                      return (
                        <h1
                          className={`text-xl font-bold mb-4 break-words ${
                            isLight ? "text-gray-900" : ""
                          }`}
                        >
                          {children}
                        </h1>
                      );
                    },
                    h2({ children }) {
                      return (
                        <h2
                          className={`text-lg font-bold mb-3 break-words ${
                            isLight ? "text-gray-900" : ""
                          }`}
                        >
                          {children}
                        </h2>
                      );
                    },
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            )}
          </div>
        )}
        {showCopy && !isUser && (
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
