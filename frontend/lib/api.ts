const API_BASE_URL = "http://localhost:8000";

export async function chatWithGenesis(message: string, context: string = "") {
  const res = await fetch(`${API_BASE_URL}/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, context }),
  });
  if (!res.ok) throw new Error("Failed to fetch response");
  return res.json();
}

export async function auditPolicy(policyText: string) {
  const res = await fetch(`${API_BASE_URL}/audit/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ policy_text: policyText }),
  });
  if (!res.ok) throw new Error("Failed to audit policy");
  return res.json();
}

export async function getDashboardStats() {
  const res = await fetch(`${API_BASE_URL}/admin/dashboard-stats`);
  if (!res.ok) throw new Error("Failed to fetch dashboard stats");
  return res.json();
}

export async function getAdminRequests() {
  const res = await fetch(`${API_BASE_URL}/admin/requests`);
  if (!res.ok) throw new Error("Failed to fetch requests");
  return res.json();
}

export async function updateRequestStatus(index: number, status: string) {
  const res = await fetch(`${API_BASE_URL}/admin/requests/${index}/status`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error("Failed to update status");
  return res.json();
}

export async function triggerAgent(agentName: string, payload: any) {
  const res = await fetch(`${API_BASE_URL}/admin/trigger-agent`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ agent_name: agentName, payload }),
  });
  if (!res.ok) throw new Error("Failed to trigger agent");
  return res.json();
}

export async function simulateCourtroomTurn(caseDetails: string, history: any[] = []) {
  const res = await fetch(`${API_BASE_URL}/courtroom/simulate-turn`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ context: caseDetails, history }),
  });
  if (!res.ok) throw new Error("Failed to simulate courtroom turn");
  return res.json();
}
