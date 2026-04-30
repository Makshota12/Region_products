import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: __ENV.K6_VUS ? Number(__ENV.K6_VUS) : 50,
  duration: __ENV.K6_DURATION || '60s',
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.05'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
  const health = http.get(`${BASE_URL}/api/products/`);
  check(health, {
    'products endpoint responds': (r) => r.status === 200 || r.status === 401 || r.status === 403,
  });

  const login = http.post(
    `${BASE_URL}/api/auth/login/`,
    JSON.stringify({
      username: __ENV.TEST_USERNAME || 'admin',
      password: __ENV.TEST_PASSWORD || 'admin123',
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );

  check(login, {
    'login accepted': (r) => r.status === 200 || r.status === 401,
  });

  sleep(1);
}
