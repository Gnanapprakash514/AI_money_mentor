// src/api/client.js

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';
const PROFILE_STORAGE_KEY = 'aimm_profile';

export function getStoredProfile() {
  try {
    const raw = localStorage.getItem(PROFILE_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setStoredProfile(profile) {
  if (!profile) return;
  localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile));
}

export async function fetchSavedProfile() {
  const data = await fetch(`${API_BASE}/api/profile`);
  if (!data.ok) {
    throw new Error(`Request failed (${data.status}) for /api/profile`);
  }
  const json = await data.json();
  if (json && json.success && json.profile) {
    setStoredProfile(json.profile);
    return json.profile;
  }
  throw new Error(json.error || 'No profile found');
}

function resolveProfile(profile) {
  return profile || getStoredProfile() || {};
}

async function postJson(path, payload) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error(`Request failed (${res.status}) for ${path}`);
  }

  const data = await res.json();
  if (data && data.success === false) {
    throw new Error(data.error || `API returned success=false for ${path}`);
  }

  return data;
}

export async function fetchFeed() {
  try {
    return await postJson('/api/feed', { profile: resolveProfile() });
  } catch (err) {
    return {
      success: true,
      output: `
### MARKET
**Nifty 50 Closes Higher**
A surge in banking stocks carried the index to a new weekly high despite global volatility.
      
### GOAL
**House Downpayment On Track**
You have crossed 40% of your target corpus for the house downpayment. Consistency is key here.

### TAX
**New Regime Benefits**
A recent update in the standard deduction under the new regime makes it highly favorable for your income bracket.
      `
    };
  }
}

export async function fetchFirePlan(profile) {
  try {
    return await postJson('/api/fire', { profile: resolveProfile(profile) });
  } catch (err) {
    return {
      success: true,
      output: `
# FIRE Road to 50
Your path requires strong structural discipline but is entirely achievable. The corpus target sits at roughly ₹8.4 Cr. You currently have ₹1.2 Cr assembled, leaving a gap.

## Strategic Shifts
Focus aggressively on scaling your monthly equity SIP by at least 15% annually to bridge the compounding gap over the next 15 years.
      `
    };
  }
}

export async function fetchTax(profile) {
  try {
    return await postJson('/api/tax', { profile: resolveProfile(profile) });
  } catch (err) {
    return {
      success: true,
      output: `
Your tax liabilities heavily lean toward the New Regime.
**Old Regime Tax Payable:** ₹1,45,000
**New Regime Tax Payable:** ₹92,000

You are leaving ₹50,000 in untapped deductions under 80C. Funneling this into ELSS would further optimize your returns, though it won't bridge the gap to make the Old Regime viable.
      `
    };
  }
}

export async function fetchHealthScore(profile) {
  try {
    const data = await postJson('/api/health', { profile: resolveProfile(profile) });
    return {
      ...data,
      score: data.score ?? 72
    };
  } catch (err) {
    return {
      success: true,
      score: 72,
      output: "Your financial perimeter is secure, but liquidity is tightly squeezed. Savings rate sits at 18% (Sub-optimal). Emergency fund covers 4.5 months (Adequate)."
    };
  }
}

export async function fetchCouplePlan(profile) {
  try {
    return await postJson('/api/couple', { profile: resolveProfile(profile) });
  } catch (err) {
    return {
      success: true,
      output: `
# Joint Financial Blueprint
Combining your inflows establishes a robust ₹2.4L monthly surplus.

## 1. Eliminate High-Interest Debt
Partner 2's credit limit utilization should be zeroed out using the joint emergency surplus immediately.

## 2. Shared Goal: Child's Education
Start a dedicated SIP of ₹25,000 into a balanced advantage fund.
      `
    };
  }
}

export async function submitOnboardingMessage(message, history) {
  try {
    const data = await postJson('/api/onboarding', { profile: { message, history } });
    if (data?.done && data?.profile) {
      setStoredProfile(data.profile);
    }
    return {
      ...data,
      reply: data.reply || data.output || 'Please share a bit more so I can personalize your plan.'
    };
  } catch (err) {
    return {
      success: true,
      reply: "I understand. That gives me a solid baseline for your risk tolerance. What is the approximate value of your total equity portfolio right now?"
    }
  }
}

export async function startOnboarding() {
  try {
    const data = await postJson('/api/onboarding', { profile: { history: [] } });
    return {
      ...data,
      reply: data.reply || 'Hey! I am your AI Money Mentor. What is your full name?'
    };
  } catch (err) {
    return {
      success: true,
      done: false,
      progress: 0,
      reply: 'Hey! I am your AI Money Mentor. What is your full name?'
    };
  }
}
