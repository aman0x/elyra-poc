const http = require('http');
const { URL } = require('url');

const AIRFLOW_BASE_URL = 'http://localhost:8083';
const PROXY_PORT = 8081;

const server = http.createServer((req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Create the target URL
  const targetUrl = new URL(req.url, AIRFLOW_BASE_URL);
  
  console.log(`Proxying: ${req.method} ${req.url} -> ${targetUrl}`);

  // Create request to Airflow
  const proxyReq = http.request(targetUrl, {
    method: req.method,
    headers: {
      ...req.headers,
      'Authorization': 'Basic ' + Buffer.from('admin:admin').toString('base64'),
      'host': 'localhost:8083'
    }
  }, (proxyRes) => {
    console.log(`Response: ${proxyRes.statusCode} ${proxyRes.statusMessage}`);
    
    // Handle specific error cases
    if (proxyRes.statusCode === 403) {
      console.error('🚨 Authentication failed! Check Airflow experimental API auth configuration.');
      console.error('💡 You may need to set auth_backend = airflow.api.auth.backend.basic_auth in airflow.cfg');
    }
    
    if (proxyRes.statusCode === 404) {
      console.error('🚨 Endpoint not found! This might be expected for experimental API limitations.');
    }
    
    // Copy headers from Airflow response
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    
    // Pipe the response
    proxyRes.pipe(res);
  });

  // Handle errors
  proxyReq.on('error', (err) => {
    console.error('Proxy request error:', err);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      error: 'Proxy Error: ' + err.message,
      help: 'Make sure Airflow is running on port 8083'
    }));
  });

  // Pipe the request
  req.pipe(proxyReq);
});

server.listen(PROXY_PORT, () => {
  console.log(`🚀 CORS Proxy server running on http://localhost:${PROXY_PORT}`);
  console.log(`📡 Forwarding requests to: ${AIRFLOW_BASE_URL}`);
  console.log(`✅ Update your .env: REACT_APP_AIRFLOW_BASE_URL=http://localhost:${PROXY_PORT}`);
  console.log('');
  console.log('📋 IMPORTANT NOTES:');
  console.log('   1. Make sure Airflow is running on port 8083');
  console.log('   2. Airflow 1.10.15 experimental API may need auth configuration');
  console.log('   3. If you get 403 errors, check your airflow.cfg:');
  console.log('      [api]');
  console.log('      auth_backend = airflow.api.auth.backend.basic_auth');
});