"use client";

import React, { useState, useRef, useEffect } from "react";
import {
    Box,
    Typography,
    Paper,
    TextField,
    Button,
    Container,
    Avatar,
    Chip,
    CircularProgress,
    Card,
    CardContent
} from "@mui/material";
import {
    Gavel,
    Person,
    Business,
    Balance,
    Send
} from "@mui/icons-material";
import { simulateCourtroomTurn } from "../../lib/api";

interface Turn {
    speaker: "Policyholder" | "Insurer" | "Judge";
    argument: string;
}

export default function CourtroomPage() {
    const [context, setContext] = useState("");
    const [history, setHistory] = useState<Turn[]>([]);
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [history]);

    const handleStart = async () => {
        if (!context.trim()) return;
        setHistory([]);
        await nextTurn();
    };

    const nextTurn = async () => {
        setLoading(true);
        try {
            // The backend expects the full history to decide who speaks next
            const response = await simulateCourtroomTurn(context, history);

            // Assuming response is { speaker: "...", argument: "..." }
            // Adjust based on actual Agent output structure. 
            // If agent returns a string, we might need to parse it or the backend should return structured dict.
            // For now, let's assume the backend returns the Turn object directly.

            if (response && response.speaker && response.argument) {
                setHistory(prev => [...prev, response]);
            } else {
                // Fallback if response is just text or different format
                console.warn("Unexpected response format", response);
            }
        } catch (error) {
            console.error("Simulation failed", error);
            alert("Courtroom simulation error. Check console.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box sx={{ minHeight: "100vh", bgcolor: "#f0f2f5", py: 4 }}>
            <Container maxWidth="lg">
                <Box sx={{ textAlign: "center", mb: 5 }}>
                    <Typography variant="h3" fontWeight="bold" sx={{
                        background: "linear-gradient(45deg, #1a237e, #b71c1c)",
                        WebkitBackgroundClip: "text",
                        WebkitTextFillColor: "transparent",
                        mb: 1
                    }}>
                        Courtroom Simulator
                    </Typography>
                    <Typography variant="h6" color="text.secondary">
                        AI-Powered Debate: Policyholder vs. Insurer
                    </Typography>
                </Box>

                <Box sx={{ display: "flex", gap: 4, flexDirection: { xs: "column", md: "row" } }}>
                    {/* Left Panel: Case Input */}
                    <Paper sx={{ flex: 1, p: 3, height: "fit-content" }}>
                        <Typography variant="h6" gutterBottom sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                            <Balance /> Case Details
                        </Typography>
                        <TextField
                            multiline
                            rows={6}
                            fullWidth
                            placeholder="Describe the claim dispute (e.g., 'Claim rejected due to pre-existing condition...')"
                            value={context}
                            onChange={(e) => setContext(e.target.value)}
                            variant="outlined"
                            sx={{ mb: 2, bgcolor: "#fff" }}
                        />
                        <Button
                            variant="contained"
                            size="large"
                            fullWidth
                            onClick={handleStart}
                            disabled={loading || !context}
                            startIcon={<Gavel />}
                            sx={{ bgcolor: "#1a237e" }}
                        >
                            Start Session
                        </Button>
                    </Paper>

                    {/* Right Panel: Debate Stream */}
                    <Paper sx={{ flex: 2, p: 3, minHeight: "60vh", display: "flex", flexDirection: "column" }}>
                        <Typography variant="h6" gutterBottom>Live Proceedings</Typography>

                        <Box sx={{ flex: 1, overflowY: "auto", mb: 2, px: 1 }}>
                            {history.length === 0 && (
                                <Box sx={{ textAlign: "center", mt: 10, opacity: 0.5 }}>
                                    <Gavel sx={{ fontSize: 60, mb: 2 }} />
                                    <Typography>Court is in recess. Submit a case to begin.</Typography>
                                </Box>
                            )}

                            {history.map((turn, idx) => (
                                <Box key={idx} sx={{
                                    display: "flex",
                                    mb: 3,
                                    justifyContent: turn.speaker === "Policyholder" ? "flex-start" : "flex-end"
                                }}>
                                    {turn.speaker === "Policyholder" && (
                                        <Avatar sx={{ bgcolor: "#1976d2", mr: 2 }}><Person /></Avatar>
                                    )}

                                    <Card sx={{
                                        maxWidth: "80%",
                                        bgcolor: turn.speaker === "Policyholder" ? "#e3f2fd" : "#ffebee",
                                        borderRadius: 4
                                    }}>
                                        <CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
                                            <Typography variant="subtitle2" fontWeight="bold" color={turn.speaker === "Policyholder" ? "primary" : "error"}>
                                                {turn.speaker}
                                            </Typography>
                                            <Typography variant="body1">{turn.argument}</Typography>
                                        </CardContent>
                                    </Card>

                                    {turn.speaker === "Insurer" && (
                                        <Avatar sx={{ bgcolor: "#d32f2f", ml: 2 }}><Business /></Avatar>
                                    )}
                                </Box>
                            ))}
                            <div ref={scrollRef} />
                        </Box>

                        {history.length > 0 && (
                            <Button
                                variant="outlined"
                                fullWidth
                                onClick={nextTurn}
                                disabled={loading}
                                endIcon={loading ? <CircularProgress size={20} /> : <Send />}
                            >
                                {loading ? "Deliberating..." : "Next Argument"}
                            </Button>
                        )}
                    </Paper>
                </Box>
            </Container>
        </Box>
    );
}
