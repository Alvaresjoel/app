const URL = (
  (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) ||
  (typeof process !== 'undefined' && process.env && (process.env.REACT_APP_API_URL || process.env.API_URL)) ||
  "http://localhost:8000/"
);

async function authFetch(path, options = {}) {
  const accessToken = localStorage.getItem('token');
  const refreshToken = localStorage.getItem('refresh-token');
  const headers = {
    ...(options.headers || {}),
    'Content-Type': 'application/json',
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
  const doFetch = async () => fetch(`${URL}${path}`, { ...options, headers });

  let response = await doFetch();
  if (response.status !== 401) return response;

  if (!refreshToken) return response;
  const refreshRes = await fetch(`${URL}auth/refresh`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${refreshToken}`,
    },
  });
  const refreshJson = await refreshRes.json().catch(() => ({}));
  if (!refreshRes.ok || !refreshJson?.data?.access_token) return response;

  localStorage.setItem('token', refreshJson.data.access_token);
  if (refreshJson.data.refresh_token) {
    localStorage.setItem('refresh-token', refreshJson.data.refresh_token);
  }

  const retryHeaders = {
    ...headers,
    Authorization: `Bearer ${refreshJson.data.access_token}`,
  };
  response = await fetch(`${URL}${path}`, { ...options, headers: retryHeaders });
  return response;
}

export async function login({ accountid, username, password }) {
  try {
    const response = await fetch(`${URL}user/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        account_id: accountid,
        username,
        password,
      }),
    });

    const result = await response.json();

    if (!response.ok || !result.success) {
      return {
        success: false,
        message: result.message || "Login failed",
        data: null,
      };
    }

    return result;
  } catch (err) {
    return {
      success: false,
      message: err.message || "An unknown error occurred",
      data: null,
    };
  }
}

export async function startTime({ user_id, ace_task_id }) {
  try {
    const response = await authFetch(`tasks/start`, {
      method: "POST",
      body: JSON.stringify({ user_id, ace_task_id }),
    });
    return await response.json();
  } catch (err) {
    return { success: false, message: err.message || "Failed to start time" };
  }
}

export async function stopTime(stopData) {
  try {
    const { log_id, status, comment, duration } = stopData || {};
    const response = await authFetch(`tasks/stop`, {
      method: "POST",
      body: JSON.stringify({
        log_id,
        status,
        comment,
        duration: typeof duration === 'number' ? duration : Number(duration ?? 0),
      }),
    });
    return await response.json();
  } catch (err) {
    return { success: false, message: err.message || "Failed to stop time" };
  }
}

export async function fetchTasks(ace_user_id) {
  try {
    const response = await authFetch(`tasks/${ace_user_id}`);
    return await response.json();
  } catch (err) {
    return { success: false, message: err.message || "Failed to fetch tasks" };
  }
}

export async function pauseTime(pauseData) {
  try {
    const response = await authFetch(`tasks/pause`, {
      method: "POST",
      body: JSON.stringify({ ...pauseData }),
    });
    return await response.json();
  } catch (err) {
    return { success: false, message: err.message || "Failed to pause time" };
  }
}

export async function getDuration(log_id) {
  try {
    const response = await authFetch(`tasks/duration/${log_id}`);
    return await response.json();
  } catch (err) {
    return { success: false, message: err.message || "Failed to get duration" };
  }
}

// Chat Page

export async function getLatestLog({ user_id, task_id }) {
  try {
    const response = await authFetch(`tasks/latest-log/?user_id=${user_id}&task_id=${task_id}`);
    return await response.json();
  } catch (err) {
    return { log_id: null, duration: 0, message: err.message || "Failed to fetch latest log" };
  }
}

export async function startConversation(user_id) {
  try {
    const response = await authFetch(`chat/start`, {
      method: "POST",
      body: JSON.stringify({ user_id }),
    });
    const result = await response.json();
    return result.data?.conversation_id;
  } catch (err) {
    return null;
  }
}

export async function getConversation(conversationId) {
  try {
    const response = await authFetch(`chat/conversation/${conversationId}`);
    const result = await response.json();
    return result.data;
  } catch (err) {
    return null;
  }
}

export async function postMessage(conversationId, sender, text) {
  try {
    const response = await authFetch(`chat/message`, {
      method: "POST",
      body: JSON.stringify({
        conversation_id: conversationId,
        sender,
        text,
      }),
    });
    const result = await response.json();
    return result.data;
  } catch (err) {
    return null;
  }
}

// GenAI
export async function askQuestion({ user_id, question }) {
  try {
    console.log(user_id)
    const response = await authFetch(`agent/ask`, {
      method: "POST",
      body: JSON.stringify({ user_id, question }),
    });
    const result = await response.json();
    if (!response.ok) {
      return { success: false, message: result?.detail || "Failed to get answer", data: null };
    }
    // backend returns { answer }
    return { success: true, data: { answer: result.answer } };
  } catch (err) {
    return { success: false, message: err.message || "Failed to get answer", data: null };
  }
}