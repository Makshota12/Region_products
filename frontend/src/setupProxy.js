const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  const proxyTarget = process.env.API_PROXY_TARGET || 'http://localhost:8000';

  app.use(
    '/api',
    createProxyMiddleware({
      target: proxyTarget,
      changeOrigin: true,
    })
  );
};

