import { useState } from "react";
import { chat } from "./services/api";
import { streamChat } from "./services/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function App() {
  const [messages, setMessages] = useState([]);

  const [input, setInput] = useState("");

  function formatMarkdown(text) {
    if (!text) return "";

    return (
      text
        // Ensure proper spacing before headings
        .replace(/\n(#+\s)/g, "\n\n$1")
        .replace(/^(#+\s)/gm, "\n$1")

        // Add spacing after headings
        .replace(/(#+\s[^\n]+)\n([^\n#-])/g, "$1\n\n$2")

        // Format unordered lists - ensure newline before dash
        .replace(/\n- /g, "\n- ")
        .replace(/^- /gm, "- ")

        // Format numbered lists
        .replace(/\n(\d+\.\s)/g, "\n$1")
        .replace(/([^\n])(\d+\.\s)/g, "$1\n$2")

        // Ensure spacing around code blocks
        .replace(/\n```/g, "\n\n```")
        .replace(/```\n/g, "```\n\n")
        .replace(/```(\w+)/g, "```$1")

        // Inline code formatting
        .replace(/`([^`]+)`/g, "`$1`")

        // Bold text spacing
        .replace(/\*\*([^\*]+)\*\*/g, "**$1**")
        .replace(/(\*\*[^\*]+\*\*)([^\s\n])/g, "$1 $2")

        // Italic spacing
        .replace(/\*([^\*]+)\*/g, "*$1*")

        // Links formatting
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, "[$1]($2)")

        // Blockquotes
        .replace(/\n> /g, "\n> ")
        .replace(/^> /gm, "> ")

        // Tables - ensure they're on their own lines
        .replace(/(\|[^\n]+\|)\n([^\n|])/g, "$1\n\n$2")
        .replace(/([^\n|])\n(\|[^\n]+\|)/g, "$1\n\n$2")

        // Horizontal rules
        .replace(/\n---\n/g, "\n\n---\n\n")
        .replace(/^---$/gm, "\n---\n")

        // Paragraph spacing - max 2 newlines
        .replace(/\n{3,}/g, "\n\n")

        .trim()
    );
  }

  async function handleSend() {
    if (!input.trim()) return;

    const userMessage = {
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);

    const currentInput = input;
    setInput("");

    const aiMessage = {
      role: "assistant",
      content: "",
      streaming: true,
    };

    setMessages((prev) => [...prev, aiMessage]);

    try {
      const response = await streamChat(currentInput);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let done = false;
      let fullText = "";

      while (!done) {
        const result = await reader.read();
        done = result.done;

        const chunk = decoder.decode(result.value || new Uint8Array());
        const lines = chunk.split("\n");

        for (const line of lines) {
          // Parse SSE data lines
          if (line.startsWith("data: ")) {
            const text = line.replace("data: ", "");
            if (text) {
              fullText += text;
            }
          }
        }

        // Update UI with streaming content in real-time
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: fullText,
            streaming: !done,
          };
          return updated;
        });
      }
    } catch (error) {
      console.error("Streaming error:", error);
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: `Error: ${error.message}`,
          streaming: false,
        };
        return updated;
      });
    }
  }

  return (
    <div className="h-screen bg-black text-white flex flex-col">
      <div className="border-b border-zinc-800 p-4">
        <h1 className="text-2xl font-bold">AI Web Search Agent</h1>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div key={index}>
            {message.role === "user" ? (
              // --------------------------------
              // USER MESSAGE
              // --------------------------------

              <div className="flex justify-end">
                <div
                  className="
            bg-blue-600
            px-4
            py-3
            rounded-2xl
            max-w-xl
          "
                >
                  {message.content}
                </div>
              </div>
            ) : (
              <div className="w-full px-4 py-3 max-w-none">
                <div
                  className="prose prose-invert prose-sm max-w-none
                  prose-headings:mt-4 prose-headings:mb-3 prose-headings:text-white
                  prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg
                  prose-p:my-2 prose-p:leading-relaxed
                  prose-li:my-1 prose-ul:my-3 prose-ol:my-3
                  prose-code:bg-zinc-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-yellow-200
                  prose-pre:bg-zinc-800 prose-pre:p-4 prose-pre:rounded-lg
                  prose-table:border-collapse prose-table:w-full
                  prose-th:border prose-th:border-zinc-600 prose-th:px-3 prose-th:py-2 prose-th:bg-zinc-900
                  prose-td:border prose-td:border-zinc-600 prose-td:px-3 prose-td:py-2
                  prose-blockquote:border-l-4 prose-blockquote:border-blue-500 prose-blockquote:pl-4 prose-blockquote:italic
                  prose-a:text-blue-400 prose-a:underline hover:prose-a:text-blue-300
                  prose-strong:text-white prose-strong:font-semibold
                  prose-em:text-gray-300
                "
                >
                  {message.streaming ? (
                    <div className="whitespace-pre-wrap leading-relaxed">
                      {message.content}
                      <span className="animate-pulse">▌</span>
                    </div>
                  ) : (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {formatMarkdown(message.content)}
                    </ReactMarkdown>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="border-t border-zinc-800 p-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask something..."
          disabled={
            messages.length > 0 && messages[messages.length - 1]?.streaming
          }
          className="
            flex-1
            bg-zinc-900
            border
            border-zinc-700
            rounded-xl
            px-4
            py-3
            outline-none
            disabled:opacity-50
            disabled:cursor-not-allowed
          "
        />

        <button
          onClick={handleSend}
          disabled={
            messages.length > 0 && messages[messages.length - 1]?.streaming
          }
          className="
            bg-blue-600
            hover:bg-blue-700
            disabled:bg-zinc-600
            disabled:cursor-not-allowed
            px-6
            rounded-xl
            font-semibold
          "
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default App;
