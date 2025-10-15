import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files in development
if (process.env.NODE_ENV === 'development') {
  // In development, serve the public folder if it exists
  const publicPath = join(__dirname, '..', 'public');
  if (existsSync(publicPath)) {
    app.use(express.static(publicPath));
  }
}

// Basic API routes
app.get('/api/health', (req, res) => {
  res.json({
    status: 'Running',
    service: 'AI Task Manager',
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Basic task API (stubbed for now)
app.get('/api/tasks', (req, res) => {
  res.json({
    success: true,
    tasks: [],
    message: 'Task API is working - connect your database to see real data'
  });
});

app.post('/api/tasks', (req, res) => {
  res.json({
    success: true,
    task: { id: 'demo-task', ...req.body },
    message: 'Task would be created - connect your database for persistence'
  });
});

// Catch-all for SPA routing in development
app.get('*', (req, res) => {
  if (req.path.startsWith('/api')) {
    res.status(404).json({ error: 'API endpoint not found' });
  } else {
    // In production, you'd serve your built frontend here
    res.json({
      message: 'AI Task Manager API',
      frontend: 'Add your frontend build here or serve from a separate process'
    });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 AI Task Manager running on port ${PORT}`);
  console.log(`📍 Health check: http://localhost:${PORT}/api/health`);
  console.log(`📋 Tasks API: http://localhost:${PORT}/api/tasks`);
  console.log(`🔧 Environment: ${process.env.NODE_ENV || 'development'}`);
});

export default app;