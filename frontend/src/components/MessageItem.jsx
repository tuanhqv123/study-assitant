import React, { useState } from "react";
import { cn } from "../lib/utils";
import { Avatar, AvatarImage } from "./ui/avatar";
import { Button } from "./ui/button";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check } from "lucide-react";
import * as Tooltip from "@radix-ui/react-tooltip";

const MessageItem = ({ message }) => {
  const isUser = message.role === "user";
  const [showCopy, setShowCopy] = useState(false);
  const [copied, setCopied] = useState(false);

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
        <div
          className={cn(
            "flex flex-col gap-2 rounded-lg px-4 py-3",
            isUser 
              ? "bg-[#2a2a2a] text-[#d1cfc0] border border-[#d1cfc0]/10" 
              : "bg-[#1a1a1a] text-[#d1cfc0] border border-[#d1cfc0]/10"
          )}
        >
          {isUser ? (
            <p className="text-base break-words whitespace-pre-wrap">
              {message.content}
            </p>
          ) : (
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  p: ({ children }) => (
                    <p className="text-base mb-4 last:mb-0 break-words">
                      {children}
                    </p>
                  ),
                  code: ({ inline, children, ...props }) =>
                    inline ? (
                      <code
                        className="bg-[#2a2a2a] rounded px-1 py-0.5 break-words text-base"
                        {...props}
                      >
                        {children}
                      </code>
                    ) : (
                      <pre className="!mt-0 max-w-full overflow-x-auto">
                        <code
                          className="block bg-[#2a2a2a] rounded p-1 my-2 break-words whitespace-pre-wrap text-base"
                          {...props}
                        >
                          {children}
                        </code>
                      </pre>
                    ),
                  ul: ({ children }) => (
                    <ul className="list-disc ml-4 mb-4 last:mb-0 text-base">
                      {children}
                    </ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="list-decimal ml-4 mb-4 last:mb-0 text-base">
                      {children}
                    </ol>
                  ),
                  li: ({ children }) => (
                    <li className="mb-1 last:mb-0 text-base">{children}</li>
                  ),
                  a: ({ children, href }) => (
                    <a
                      href={href}
                      className="text-[#d1cfc0] hover:underline break-words text-base"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {children}
                    </a>
                  ),
                  h1: ({ children }) => (
                    <h1 className="text-xl font-bold mb-4 break-words">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-lg font-bold mb-3 break-words">
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-base font-bold mb-2 break-words">
                      {children}
                    </h3>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-4 border-[#d1cfc0]/20 pl-4 my-4 italic break-words text-base">
                      {children}
                    </blockquote>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>
        {showCopy && !isUser && (
          <Tooltip.Provider>
            <Tooltip.Root>
              <Tooltip.Trigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute -right-1 -bottom-1 h-6 w-6 bg-[#2a2a2a] hover:bg-[#333333] rounded-sm opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={handleCopy}
                >
                  {copied ? (
                    <Check className="h-3 w-3 text-[#d1cfc0]" />
                  ) : (
                    <Copy className="h-3 w-3 text-[#d1cfc0]" />
                  )}
                </Button>
              </Tooltip.Trigger>
              <Tooltip.Portal>
                <Tooltip.Content
                  className="bg-[#1a1a1a] text-[#d1cfc0] text-xs px-2 py-1 rounded border border-[#d1cfc0]/10"
                  sideOffset={5}
                >
                  {copied ? "Copied!" : "Copy to clipboard"}
                  <Tooltip.Arrow className="fill-[#1a1a1a]" />
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
