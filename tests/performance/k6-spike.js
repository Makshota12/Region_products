import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '30s', target: 150 },
    { duration: '1m', target: 150 },
    { duration: '30s', target: 20 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<4000'],
    http_req_failed: ['rate<0.1'],
  },
};

function loginAndGetToken() {
  const response = http.post(
    `${BASE_URL}/api/auth/login/`,
    JSON.stringify({
      username: __ENV.TEST_USERNAME || 'admin',
      password: __ENV.TEST_PASSWORD || 'admin123',
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );

  const ok = check(response, {
    'login status is 200 or 401': (r) => r.status === 200 || r.status === 401,
  });

  if (!ok || response.status !== 200) {
    return null;
  }

  try {
    const body = JSON.parse(response.body);
    return body.token || null;
  } catch (e) {
    return null;
  }
}

export default function () {
  const token = loginAndGetToken();

  const headers = token
    ? { Authorization: `Bearer ${token}` }
    : {};

  const products = http.get(`${BASE_URL}/api/products/`, { headers });
  check(products, {
    'products endpoint survives spike': (r) => [200, 401, 403].includes(r.status),
  });

  const sessions = http.get(`${BASE_URL}/api/evaluation-sessions/`, { headers });
  check(sessions, {
    'sessions endpoint survives spike': (r) => [200, 401, 403].includes(r.status),
  });

  sleep(0.5);
}
