"use client";

import React, { useState, useEffect } from "react";
import {
    Box,
    Typography,
    Paper,
    TextField,
    Button,
    Card,
    CardContent,
    IconButton,
    Chip,
    Divider,
    Container
} from "@mui/material";
import {
    Lock,
    Security,
    Gavel,
    LocalHospital,
    CheckCircle,
    Cancel,
    PlayArrow
} from "@mui/icons-material";
import {
    getDashboardStats,
    getAdminRequests,
    updateRequestStatus,
    triggerAgent
} from "../../lib/api";

export default function AdminPage() {
    const [locked, setLocked] = useState(true);
    const [password, setPassword] = useState("");
    const [stats, setStats] = useState<any>(null);
    const [requests, setRequests] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);

    // Mock Password Check
    const handleUnlock = () => {
        if (password === "admin123") {
            setLocked(false);
            fetchData();
        } else {
            alert("Access Denied");
        }
    };

    const fetchData = async () => {
        setLoading(true);
        try {
            const s = await getDashboardStats();
            const r = await getAdminRequests();
            setStats(s);
            setRequests(r);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const handleAction = async (index: number, status: string) => {
        await updateRequestStatus(index, status);
        fetchData(); // Refresh
    };

    const handleTrigger = async (agent: string) => {
        const payload = { manual_trigger: true, timestamp: new Date().toISOString() };
        alert(`Triggering ${agent}...`);
        await triggerAgent(agent, payload);
        alert(`${agent} Triggered!`);
    };

    if (locked) {
        return (
            <Box sx={{
                height: "100vh",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                bgcolor: "#000",
                color: "#fff"
            }}>
                <Paper sx={{ p: 4, textAlign: "center", width: 300 }}>
                    <Lock sx={{ fontSize: 40, mb: 2, color: "red" }} />
                    <Typography variant="h5" gutterBottom>Restricted Area</Typography>
                    <TextField
                        type="password"
                        fullWidth
                        placeholder="Enter Passkey"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        sx={{ mb: 2 }}
                    />
                    <Button variant="contained" color="error" fullWidth onClick={handleUnlock}>
                        Unlock
                    </Button>
                </Paper>
            </Box>
        );
    }

    return (
        <Box sx={{ minHeight: "100vh", bgcolor: "#f5f5f5", p: 4 }}>
            <Container maxWidth="xl">
                <Box sx={{ display: "flex", justifyContent: "space-between", mb: 4 }}>
                    <Typography variant="h4" fontWeight="bold">
                        🔐 God Mode Dashboard
                    </Typography>
                    <Button variant="outlined" onClick={() => setLocked(true)}>Lock System</Button>
                </Box>

                {/* Stats Row */}
                <Box sx={{ display: "flex", gap: 3, mb: 4, flexWrap: "wrap" }}>
                    <Card sx={{ flex: 1, minWidth: 200 }}>
                        <CardContent>
                            <Typography color="text.secondary">Total Policies</Typography>
                            <Typography variant="h3">{stats?.metrics?.total_policies_analyzed || 0}</Typography>
                        </CardContent>
                    </Card>
                    <Card sx={{ flex: 1, minWidth: 200 }}>
                        <CardContent>
                            <Typography color="text.secondary">Risk Zone</Typography>
                            <Typography variant="h4" color="error">{stats?.metrics?.top_risk_zip || "N/A"}</Typography>
                        </CardContent>
                    </Card>
                    <Card sx={{ flex: 1, minWidth: 200 }}>
                        <CardContent>
                            <Typography color="text.secondary">Active Agents</Typography>
                            <Typography variant="h3">5</Typography>
                        </CardContent>
                    </Card>
                    <Card sx={{ flex: 1, minWidth: 200 }}>
                        <CardContent>
                            <Typography color="text.secondary">Pending Actions</Typography>
                            <Typography variant="h3" color="warning.main">{requests.filter((r: any) => r.status === "PENDING").length}</Typography>
                        </CardContent>
                    </Card>
                </Box>

                <Box sx={{ display: "flex", gap: 4, flexDirection: { xs: "column", md: "row" } }}>
                    {/* Left Col: Requests */}
                    <Box sx={{ flex: 2 }}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>🛑 Genesis Action Requests</Typography>
                            <Divider sx={{ mb: 2 }} />

                            {requests.length === 0 ? (
                                <Typography>No pending requests.</Typography>
                            ) : (
                                requests.map((req, idx) => (
                                    <Box key={idx} sx={{
                                        mb: 2, p: 2,
                                        border: "1px solid #eee",
                                        borderRadius: 2,
                                        display: "flex",
                                        justifyContent: "space-between",
                                        alignItems: "center"
                                    }}>
                                        <Box>
                                            <Typography variant="subtitle2" color="text.secondary">
                                                {req.timestamp} • {req.tool}
                                            </Typography>
                                            <Typography variant="body1">{req.message}</Typography>
                                            <Chip
                                                label={req.status}
                                                size="small"
                                                color={req.status === "APPROVED" ? "success" : req.status === "DENIED" ? "error" : "warning"}
                                                sx={{ mt: 1 }}
                                            />
                                        </Box>

                                        {req.status === "PENDING" && (
                                            <Box>
                                                <IconButton color="success" onClick={() => handleAction(idx, "APPROVED")}>
                                                    <CheckCircle />
                                                </IconButton>
                                                <IconButton color="error" onClick={() => handleAction(idx, "DENIED")}>
                                                    <Cancel />
                                                </IconButton>
                                            </Box>
                                        )}
                                    </Box>
                                ))
                            )}
                        </Paper>
                    </Box>

                    {/* Right Col: God Mode Controls */}
                    <Box sx={{ flex: 1 }}>
                        <Paper sx={{ p: 3, bgcolor: "#1a237e", color: "white" }}>
                            <Typography variant="h6" gutterBottom>⚡ God Mode Triggers</Typography>
                            <Typography variant="body2" sx={{ mb: 3, opacity: 0.7 }}>
                                Manually force-start specific agents regardless of user input.
                            </Typography>

                            <Button
                                variant="contained"
                                fullWidth
                                startIcon={<Security />}
                                sx={{ mb: 2, bgcolor: "rgba(255,255,255,0.1)" }}
                                onClick={() => handleTrigger("AUDITOR")}
                            >
                                Force Audit Policy
                            </Button>

                            <Button
                                variant="contained"
                                fullWidth
                                startIcon={<Gavel />}
                                sx={{ mb: 2, bgcolor: "rgba(255,255,255,0.1)" }}
                                onClick={() => handleTrigger("COURTROOM")}
                            >
                                Summon Courtroom
                            </Button>

                            <Button
                                variant="contained"
                                fullWidth
                                startIcon={<LocalHospital />}
                                sx={{ mb: 2, bgcolor: "rgba(255,255,255,0.1)" }}
                                onClick={() => handleTrigger("MEDICAL")}
                            >
                                Medical Override
                            </Button>

                            <Button
                                variant="contained"
                                fullWidth
                                startIcon={<PlayArrow />}
                                color="warning"
                                onClick={() => handleTrigger("GENESIS")}
                            >
                                Reboot Genesis Core
                            </Button>
                        </Paper>
                    </Box>
                </Box>
            </Container>
        </Box>
    );
}
