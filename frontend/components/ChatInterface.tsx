"use client";

import React, { useState, useRef, useEffect } from "react";
import {
    Box,
    TextField,
    IconButton,
    Paper,
    Typography,
    CircularProgress,
    Avatar
} from "@mui/material";
import { Send, SmartToy, Person } from "@mui/icons-material";
import ReactMarkdown from "react-markdown";
import { chatWithGenesis } from "../lib/api";

interface Message {
    role: "user" | "assistant";
    content: string;
}

export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<null | HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = { role: "user", content: input };
        setMessages((prev) => [...prev, userMsg]);
        setInput("");
        setLoading(true);

        try {
            const response = await chatWithGenesis(input);
            const aiMsg: Message = { role: "assistant", content: response.response };
            setMessages((prev) => [...prev, aiMsg]);
        } catch (error) {
            console.error("Chat error:", error);
            const errorMsg: Message = { role: "assistant", content: "⚠️ Error connecting to Genesis." };
            setMessages((prev) => [...prev, errorMsg]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box sx={{
            display: "flex",
            flexDirection: "column",
            height: "90vh",
            maxWidth: "900px",
            margin: "0 auto",
            p: 2
        }}>
            {/* Header */}
            <Box sx={{ mb: 4, textAlign: "center" }}>
                <Typography variant="h4" sx={{
                    background: "linear-gradient(90deg, #4b90ff, #ff5546)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                    fontWeight: "bold"
                }}>
                    Hello, User
                </Typography>
                <Typography variant="h6" color="text.secondary">
                    How can I help you today?
                </Typography>
            </Box>

            {/* Chat Area */}
            <Paper elevation={0} sx={{
                flex: 1,
                overflowY: "auto",
                mb: 2,
                p: 2,
                bgcolor: "transparent"
            }}>
                {messages.map((msg, index) => (
                    <Box key={index} sx={{
                        display: "flex",
                        mb: 3,
                        justifyContent: msg.role === "user" ? "flex-end" : "flex-start"
                    }}>
                        {msg.role === "assistant" && (
                            <Avatar sx={{ bgcolor: "transparent", mr: 2 }}>
                                <SmartToy sx={{ color: "#4b90ff" }} />
                            </Avatar>
                        )}

                        <Paper elevation={1} sx={{
                            p: 2,
                            maxWidth: "70%",
                            borderRadius: 4,
                            bgcolor: msg.role === "user" ? "#e3f2fd" : "#f5f5f5",
                            color: "text.primary"
                        }}>
                            {msg.role === "assistant" ? (
                                <ReactMarkdown>{msg.content}</ReactMarkdown>
                            ) : (
                                <Typography>{msg.content}</Typography>
                            )}
                        </Paper>

                        {msg.role === "user" && (
                            <Avatar sx={{ bgcolor: "#1976d2", ml: 2 }}>
                                <Person />
                            </Avatar>
                        )}
                    </Box>
                ))}
                {loading && (
                    <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
                        <CircularProgress size={24} />
                    </Box>
                )}
                <div ref={messagesEndRef} />
            </Paper>

            {/* Input Area */}
            <Paper elevation={3} sx={{
                p: "2px 4px",
                display: "flex",
                alignItems: "center",
                borderRadius: 8,
                bgcolor: "#f0f4f9"
            }}>
                <TextField
                    sx={{ ml: 2, flex: 1 }}
                    placeholder="Ask Gemini..."
                    variant="standard"
                    InputProps={{ disableUnderline: true }}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && handleSend()}
                    disabled={loading}
                />
                <IconButton color="primary" sx={{ p: "10px" }} onClick={handleSend} disabled={loading}>
                    <Send />
                </IconButton>
            </Paper>
        </Box>
    );
}
