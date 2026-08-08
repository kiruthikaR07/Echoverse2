import React, { useState, useRef, useEffect } from "react";
import { Message, Candidate } from "../types";
import { Send, Bot, User, Sparkles, CornerDownLeft, Loader2 } from "lucide-react";

interface InterviewChatProps {
  messages: Message[];
  onSendMessage: (text: string) => void;
  isLoading: boolean;
  candidate: Candidate;
  isComplete: boolean;
}

export const InterviewChat: React.FC<InterviewChatProps> = ({
  messages,
  onSendMessage,
  isLoading,
  candidate,
  isComplete,
}) => {
  const [input, setInput] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading || isComplete) return;
    onSendMessage(input.trim());
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] max-w-4xl mx-auto w-full p-4">
      {/* Messages Transcript Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-6 pr-2 pb-4">
        {messages.map((msg, index) => {
          const isAssistant = msg.role === "assistant";
          return (
            <div
              key={index}
              className={`flex items-start gap-3 ${
                isAssistant ? "justify-start" : "justify-end"
              }`}
            >
              {isAssistant && (
                <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center shrink-0 shadow-xs mt-1">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-2xl rounded-2xl px-5 py-4 text-sm leading-relaxed shadow-xs ${
                  isAssistant
                    ? "bg-white border border-slate-200 text-slate-800"
                    : "bg-indigo-600 text-white"
                }`}
              >
                {/* Assistant Metadata Badges */}
                {isAssistant && msg.topic && (
                  <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-100 text-xs text-slate-500 font-medium">
                    <span className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 font-semibold">
                      {msg.topic}
                    </span>
                    {msg.day && <span>Day {msg.day}</span>}
                    {msg.difficulty && (
                      <span className="text-slate-400">Diff: {msg.difficulty}/5</span>
                    )}
                  </div>
                )}

                <div className="whitespace-pre-wrap font-sans">{msg.content}</div>

                <div
                  className={`mt-2 text-[10px] text-right font-mono ${
                    isAssistant ? "text-slate-400" : "text-indigo-200"
                  }`}
                >
                  {msg.timestamp || "Just now"}
                </div>
              </div>

              {!isAssistant && (
                <div className="w-8 h-8 rounded-full bg-slate-800 text-white flex items-center justify-center shrink-0 shadow-xs mt-1">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          );
        })}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex items-start gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center shrink-0 shadow-xs">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl px-5 py-4 text-sm text-slate-500 flex items-center gap-3 shadow-xs">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
              <span className="italic">Evaluating answer, adapting difficulty, & preparing next technical question...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Answer Composition Box */}
      {!isComplete && (
        <form onSubmit={handleSubmit} className="mt-2 bg-white border border-slate-200 rounded-2xl p-3 shadow-md">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your technical answer here... (Press Cmd+Enter to submit)"
            rows={3}
            disabled={isLoading}
            className="w-full text-sm border-0 focus:ring-0 resize-none outline-none text-slate-800 placeholder-slate-400"
          />

          <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs text-slate-500">
            <div className="flex items-center gap-1.5 text-slate-400">
              <CornerDownLeft className="w-3.5 h-3.5" />
              <span>Use <kbd className="px-1.5 py-0.5 rounded bg-slate-100 border text-[10px]">Cmd/Ctrl + Enter</kbd> to send</span>
            </div>

            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 text-white font-medium rounded-xl transition-all flex items-center gap-1.5 text-xs shadow-xs cursor-pointer"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" /> Evaluating
                </>
              ) : (
                <>
                  Submit Answer <Send className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
