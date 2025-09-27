import { FormEvent, useState } from "react";
import { inferTabIntent, postCopilotPrompt } from "../api";

type Message = {
  role: "user" | "assistant";
  content: string;
};

function Copilot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!input.trim()) {
      return;
    }

    const intent = inferTabIntent(input);
    const newMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");

    const response = await postCopilotPrompt({ prompt: newMessage.content, intent });
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: response.message ?? "Copilot response pending integration."
      }
    ]);
  };

  return (
    <div>
      <h1>Risk Copilot</h1>
      <p>Ask natural language questions about posture, compliance, and narratives.</p>
      <div>
        {messages.map((message, index) => (
          <p key={index}>
            <strong>{message.role === "user" ? "You" : "Copilot"}:</strong> {" "}
            {message.content}
          </p>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <label htmlFor="prompt">Prompt</label>
        <textarea
          id="prompt"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          rows={3}
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default Copilot;
