# Airflow DAG Manager

A modern React TypeScript application for monitoring and managing Apache Airflow DAGs with real-time updates and file management capabilities. This stateless single-page application allows you to view DAG information, monitor runs, trigger new DAG executions, and manage related files in MinIO S3 storage.

## 🚀 Features

### Core DAG Management
- **📊 DAG Overview**: View all available DAGs with status, description, and metadata
- **🔄 Real-time Monitoring**: Live DAG run status updates with smart polling
- **⚡ DAG Execution**: Trigger new DAG runs directly from the interface
- **📈 Run History**: View detailed DAG run history with visual status indicators

### Real-time Updates & Polling
- **🔴 Smart Polling**: Automatic refresh with intelligent intervals
  - 5 seconds when DAGs are active/running
  - 30 seconds when all DAGs are idle
- **⏯️ Polling Controls**: Start/stop auto-refresh with visual indicators
- **⏱️ Configurable Intervals**: Choose from 5s, 10s, 30s, 1m, 5m refresh rates
- **🟢 Live Status**: Pulsing indicator shows real-time polling status
- **⏰ Last Updated**: Always know when data was last refreshed

### File Management
- **📁 MinIO Integration**: View and manage DAG-related files in S3-compatible storage
- **🎯 Drag & Drop Upload**: Easy file uploads with drag and drop support
- **📊 Progress Tracking**: Real-time upload progress with visual progress bars
- **📂 Smart Organization**: Files automatically organized by DAG ID
- **✅ File Validation**: Type and size validation with user-friendly error messages
- **📋 Multiple Uploads**: Upload multiple files simultaneously

### User Experience
- **🔔 Smart Notifications**: Success/error messages with auto-dismiss
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices
- **🎨 Modern Interface**: Clean, intuitive design with status-based color coding
- **⚡ Fast Performance**: Optimized rendering and efficient data fetching
- **🌐 Containerized**: Ready for Docker and Kubernetes deployment

## Prerequisites

- Node.js 18+
- Apache Airflow 1.10.15+ (uses experimental API)
- MinIO or S3-compatible storage
- Docker (for containerization)
- Kubernetes cluster (for K8s deployment)

## Quick Start

### 1. Clone and Install

```bash
git clone <repository-url>
cd airflow-dag-manager
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Airflow and MinIO credentials
```

### 3. Set Up CORS Proxy (Required for Airflow 1.10.15)

Since Airflow 1.10.15 experimental API doesn't support CORS, start the included proxy server:

```bash
# In terminal 1
node proxy-server.js
```

### 4. Run Development Server

```bash
# In terminal 2
npm start
```

The application will be available at `http://localhost:3000`

## Configuration

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `REACT_APP_AIRFLOW_BASE_URL` | Airflow webserver URL (via proxy) | `http://localhost:8081` | `http://localhost:8081` |
| `REACT_APP_AIRFLOW_USERNAME` | Airflow username | `admin` | `admin` |
| `REACT_APP_AIRFLOW_PASSWORD` | Airflow password | `admin` | `admin` |
| `REACT_APP_MINIO_ENDPOINT` | MinIO endpoint | `localhost:9000` | `minio.example.com:9000` |
| `REACT_APP_MINIO_ACCESS_KEY` | MinIO access key | `minioadmin` | `your-access-key` |
| `REACT_APP_MINIO_SECRET_KEY` | MinIO secret key | `minioadmin` | `your-secret-key` |
| `REACT_APP_MINIO_BUCKET_NAME` | MinIO bucket name | `airflow-dags` | `my-dag-files` |
| `REACT_APP_MINIO_USE_SSL` | Use SSL for MinIO | `false` | `true` |
| `REACT_APP_API_TIMEOUT` | API request timeout (ms) | `10000` | `15000` |
| `REACT_APP_POLLING_INTERVAL` | Default polling interval (ms) | `30000` | `60000` |

### Airflow Configuration

For Airflow 1.10.15, you may need to configure the experimental API authentication:

```ini
# In your airflow.cfg
[api]
auth_backend = airflow.api.auth.backend.basic_auth
```

### Real-time Polling Configuration

The application uses smart polling intervals:
- **Active DAGs**: 5 seconds (when DAGs are running)
- **Idle State**: 30 seconds (when all DAGs are paused)
- **Manual Override**: User can select 5s, 10s, 30s, 1m, or 5m intervals

## File Upload Features

### Supported File Types
- Python files (`.py`) - DAG definitions
- SQL files (`.sql`) - Query templates  
- Configuration files (`.json`, `.yaml`, `.yml`)
- Documentation (`.txt`, `.md`)

### Upload Specifications
- **Max File Size**: 50MB per file
- **Multiple Uploads**: Support for simultaneous uploads
- **Progress Tracking**: Real-time progress bars
- **File Organization**: Automatic organization by DAG ID
- **Naming Convention**: `{dag-id}/filename_timestamp.extension`

### Drag & Drop Support
- Drag files directly onto the upload zone
- Visual feedback during drag operations
- Batch upload multiple files at once

## Docker Deployment

### Build and Run

```bash
# Build the Docker image
npm run docker:build

# Run the container
npm run docker:run
```

Or manually:

```bash
docker build -t airflow-dag-manager .
docker run -p 3000:80 airflow-dag-manager
```

## Kubernetes Deployment

### 1. Configure Secrets

```bash
# Create secret from template
cp k8s/secret.yaml.template k8s/secret.yaml
# Edit k8s/secret.yaml with your base64-encoded credentials

# Or create using kubectl
kubectl create secret generic airflow-dag-manager-secret \
  --from-literal=AIRFLOW_USERNAME=your-username \
  --from-literal=AIRFLOW_PASSWORD=your-password \
  --from-literal=MINIO_ACCESS_KEY=your-access-key \
  --from-literal=MINIO_SECRET_KEY=your-secret-key
```

### 2. Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 3. Access the Application

```bash
# Via NodePort (if using NodePort service)
http://your-cluster-ip:30080

# Via port-forward
kubectl port-forward service/airflow-dag-manager-service 3000:80
http://localhost:3000
```

## Development

### Project Structure

```
airflow-dag-manager/
├── src/
│   ├── components/          # React components
│   ├── services/           # API services
│   ├── types/              # TypeScript types
│   ├── utils/              # Utility functions
│   ├── App.tsx             # Main App component
│   └── index.tsx           # Entry point
├── public/                 # Static assets
├── k8s/                    # Kubernetes manifests
├── Dockerfile              # Docker configuration
├── nginx.conf              # Nginx configuration
└── package.json            # Dependencies and scripts
```

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run docker:build` - Build Docker image
- `npm run docker:run` - Run Docker container

## API Compatibility

This application is designed to work with **Apache Airflow 1.10.15** using the experimental REST API. Key endpoints used:

### Airflow Experimental API
- `GET /api/experimental/latest_runs` - Get latest DAG runs (used to extract DAG list)
- `GET /api/experimental/dags/{dag_id}/dag_runs` - Get DAG run history
- `POST /api/experimental/dags/{dag_id}/dag_runs` - Trigger new DAG run
- `GET /api/experimental/test` - Health check endpoint

### MinIO S3 API
- `ListObjectsV2` - List files in bucket
- `GetObject` - Download file content  
- `PutObject` - Upload files with progress tracking
- `HeadObject` - Check file existence
- `DeleteObject` - Remove files

**Note**: The experimental API has limitations compared to modern Airflow versions. Some DAG metadata may not be available through the latest_runs endpoint.

## Troubleshooting

### Common Issues

#### CORS Errors
**Problem**: Browser blocks requests to Airflow API
**Solution**: Use the included proxy server:
```bash
node proxy-server.js
# Set REACT_APP_AIRFLOW_BASE_URL=http://localhost:8081
```

#### Authentication Failures (403 Forbidden)
**Problem**: Airflow experimental API denies requests
**Solution**: Configure Airflow authentication:
```ini
# In airflow.cfg
[api]
auth_backend = airflow.api.auth.backend.basic_auth
```

#### MinIO Connection Issues
**Problem**: Cannot connect to MinIO/S3
**Solutions**:
- Verify MinIO endpoint and credentials
- Check network connectivity
- Ensure bucket exists and is accessible
- Verify SSL/TLS configuration

#### File Upload Failures
**Problem**: Files fail to upload to MinIO
**Solutions**:
- Check file size limits (default: 50MB)
- Verify file type restrictions
- Ensure MinIO credentials have write permissions
- Check browser console for detailed error messages

#### Polling Not Working
**Problem**: DAG list doesn't update automatically
**Solutions**:
- Check if auto-refresh is enabled (green pulsing dot)
- Verify Airflow connection through proxy
- Check browser network tab for failed requests
- Try manual refresh to test connectivity

#### Docker Network Issues
**Problem**: Services can't communicate in Docker
**Solution**: Use proper network configuration:
```bash
# Use host networking or custom bridge network
docker run --network host airflow-dag-manager
```

### Debugging

#### Enable Debug Mode
Set environment variable for detailed logging:
```bash
REACT_APP_DEBUG=true npm start
```

#### Check Proxy Server
Verify the proxy server is forwarding requests correctly:
```bash
# Test proxy directly
curl http://localhost:8081/api/experimental/test
# Should return: "OK"
```

#### Verify Airflow API
Test Airflow experimental API directly:
```bash
# Direct API test
curl -u admin:admin http://localhost:8083/api/experimental/test
# Should return: "OK"
```

#### MinIO Connection Test
Test MinIO connectivity:
```bash
# Using MinIO client
mc ls your-minio-alias/your-bucket
```

### Performance Optimization

#### Polling Intervals
- Use longer intervals (1-5 minutes) for stable environments
- Use shorter intervals (5-30 seconds) for active development
- Smart polling automatically adjusts based on DAG activity

#### File Upload Performance
- Upload smaller files (< 10MB) for better user experience
- Use batch uploads for multiple small files
- Monitor upload progress and cancel if needed

## Advanced Features

### Real-time Notifications
- Success/error notifications with auto-dismiss
- Upload progress tracking with visual feedback
- DAG trigger confirmations

### Smart Polling Logic
```typescript
// Automatically adjusts polling based on DAG states
const interval = hasRunningDAGs ? 5000 : 30000; // 5s vs 30s
```

### File Organization
```
bucket/
├── dag_id_1/
│   ├── data_processing_2025-05-26T10-30-45.py
│   └── config_2025-05-26T10-35-12.json
└── dag_id_2/
    └── query_template_2025-05-26T11-00-00.sql
```

### Development Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/your-username/airflow-dag-manager.git
cd airflow-dag-manager
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up development environment**
```bash
cp .env.example .env
# Configure your local Airflow and MinIO instances
```

4. **Start development servers**
```bash
# Terminal 1: Proxy server
node proxy-server.js

# Terminal 2: React app  
npm start
```
