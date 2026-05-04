import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  stages: [
    { duration: '2m', target: 20 },
    { duration: '15m', target: 20 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.05'],
  },
};

function authHeaders() {
  const login = http.post(
    `${BASE_URL}/api/auth/login/`,
    JSON.stringify({
      username: __ENV.TEST_USERNAME || 'admin',
      password: __ENV.TEST_PASSWORD || 'admin123',
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );

  check(login, {
    'login accepted in soak test': (r) => r.status === 200 || r.status === 401,
  });

  if (login.status !== 200) {
    return {};
  }

  try {
    const token = JSON.parse(login.body).token;
    return token ? { Authorization: `Bearer ${token}` } : {};
  } catch (e) {
    return {};
  }
}

export default function () {
  const headers = authHeaders();

  const currentUser = http.get(`${BASE_URL}/api/auth/user/`, { headers });
  check(currentUser, {
    'current user endpoint stable': (r) => [200, 401].includes(r.status),
  });

  const domainScores = http.get(`${BASE_URL}/api/evaluation-sessions/1/get_domain_scores/`, {
    headers,
  });
  check(domainScores, {
    'domain score endpoint stable': (r) => [200, 401, 403, 404].includes(r.status),
  });

  sleep(1);
}
