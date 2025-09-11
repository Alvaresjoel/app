import { useContext, useEffect, useRef, useState } from "react";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import { startConversation, getConversation, postMessage, askQuestion } from "../services/api";
import { UserContext } from "../store/user-context";
import ReactMarkdown from "react-markdown";
import Papa from "papaparse";

function isCSV(text) {
    // Simple check: CSV usually has commas and newlines, and at least two lines
    return typeof text === "string" && text.includes(",") && text.split("\n").length > 1;
}

function CSVTable({ csv }) {
    const { data } = Papa.parse(csv.trim());
    if (!data || data.length === 0) return null;
    return (
        <div className="overflow-x-auto">
            <table className="min-w-full border border-gray-300 bg-white text-sm">
                <thead>
                    <tr>
                        {data[0].map((cell, i) => (
                            <th key={i} className="border px-2 py-1 bg-gray-200">{cell}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.slice(1).map((row, i) => (
                        <tr key={i}>
                            {row.map((cell, j) => (
                                <td key={j} className="border px-2 py-1">{cell}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default function ChatPage() {
    const [conversationId, setConversationId] = useState(null);
    const [history, setHistory] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const { user } = useContext(UserContext);
    const userId = user?.user_id;
    const chatEndRef = useRef(null);

    useEffect(() => {
        async function initConversation() {
            if (!userId) return;
            const convId = await startConversation(userId);
            setConversationId(convId);
            const messages = await getConversation(convId);
            console.log("Fetched messages:", messages);
            setHistory(messages || []);
        }
        initConversation();
    }, [userId]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [history, loading]);

    async function handleSend(e) {
        e.preventDefault();
        if (!input.trim() || !conversationId || !userId) return;

        const userMessage = await postMessage(conversationId, "user", input.trim());
        setHistory((prev) => [...prev, userMessage]);
        setInput("");
        setLoading(true);

        // Fetch AI answer via api service
        const { success, data, message } = await askQuestion({ user_id: userId, question: input.trim() });
        const answerText = success ? data?.answer : (message || "Sorry, something went wrong.");
        const assistantMessage = await postMessage(conversationId, "assistant", answerText);
        setHistory((prev) => [...prev, assistantMessage]);
        setLoading(false);
    }

    function renderMessage(entry) {
        if (entry.sender === "assistant" && isCSV(entry.text)) {
            return <CSVTable csv={entry.text} />;
        }
        if (entry.sender === "assistant") {
            return <ReactMarkdown>{entry.text}</ReactMarkdown>;
        }
        return <span>{entry.text}</span>;
    }

    return (
        <div className="flex flex-col bg-gray-50 w-full">
            <div className="flex-1 overflow-y-auto p-6 pt-6 pb-24">
                {history?.map((entry, idx) => (
                    <div
                        key={idx}
                        className={`flex mb-4 ${entry.sender === "user" ? "justify-end" : "justify-start"}`}
                    >
                        {entry.sender === "assistant" && (
                            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-400 text-white flex items-center justify-center mr-2">
                                <span>AI</span>
                            </div>
                        )}
                        <div
                            className={`max-w-xl p-4 rounded-lg shadow ${
                                entry.sender === "user"
                                    ? "bg-blue-500 text-white rounded-br-none"
                                    : "bg-white text-gray-900 rounded-bl-none"
                            }`}
                        >
                            {renderMessage(entry)}
                        </div>
                        {entry.sender === "user" && (
                            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-400 text-white flex items-center justify-center ml-2">
                                <span>U</span>
                            </div>
                        )}
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start mb-4">
                        <div className="w-8 h-8 rounded-full bg-green-400 text-white flex items-center justify-center mr-2">
                            <span>AI</span>
                        </div>
                        <div className="max-w-xl p-4 rounded-lg shadow bg-white text-gray-900 rounded-bl-none italic opacity-70">
                            Thinking...
                        </div>
                    </div>
                )}
                <div ref={chatEndRef} />
            </div>
            <form onSubmit={handleSend} className="p-4 flex gap-2 border-b bg-white sticky bottom-0 z-10">
                <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask a question..."
                />
                <Button type="submit" disabled={loading}>Send</Button>
            </form>
        </div>
    );
}
