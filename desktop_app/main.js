/**
 * System3 Ultra Desktop Application
 * Electron Main Process
 * Auto-starts backend, embeds React UI, manages lifecycle
 */
const { app, BrowserWindow, Tray, Menu, ipcMain, Notification, dialog } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const fs = require('fs')
const os = require('os')

// Detect if running from installation or development
const isPackaged = app.isPackaged || process.mainModule.filename.indexOf('app.asar') !== -1

// Paths - different for development vs installed
let BACKEND_DIR, FRONTEND_DIST, AGENT_MEMORY_DIR, PYTHON_EXE

if (isPackaged) {
  // Installed app - resources are in app.asar.unpacked or extraResources
  const resourcesPath = process.resourcesPath
  BACKEND_DIR = path.join(resourcesPath, 'backend')
  FRONTEND_DIST = path.join(resourcesPath, 'frontend')
  AGENT_MEMORY_DIR = path.join(resourcesPath, 'agent_memory')
  
  // Try to find Python in common locations
  const pythonPaths = [
    'C:\\Python314\\python.exe',
    'C:\\Python313\\python.exe',
    'C:\\Python312\\python.exe',
    'C:\\Python311\\python.exe',
    'C:\\Python310\\python.exe',
    path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python314', 'python.exe'),
    path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python313', 'python.exe'),
    'python'  // Fallback to PATH
  ]
  
  // Find first existing Python
  PYTHON_EXE = pythonPaths.find(p => {
    try {
      return fs.existsSync(p)
    } catch {
      return false
    }
  }) || 'python'
  
  console.log(`[Installed Mode] Using Python: ${PYTHON_EXE}`)
} else {
  // Development mode - use relative paths
  BACKEND_DIR = path.join(__dirname, '..', 'dashboard', 'backend')
  FRONTEND_DIST = path.join(__dirname, '..', 'dashboard', 'frontend', 'dist')
  AGENT_MEMORY_DIR = path.join(__dirname, '..', 'agent_memory')
  PYTHON_EXE = process.env.PYTHON_PATH || 'python'
  
  console.log('[Development Mode] Using relative paths')
}

// Global references
let mainWindow = null
let backendProcess = null
let tray = null
let isBackendRunning = false

// Backend port
const BACKEND_PORT = 8000

/**
 * Load agent memory to resume work
 */
function loadAgentMemory() {
  try {
    const tasksFile = path.join(AGENT_MEMORY_DIR, 'tasks.json')
    if (fs.existsSync(tasksFile)) {
      const tasks = JSON.parse(fs.readFileSync(tasksFile, 'utf-8'))
      console.log(`[Agent Memory] Loaded ${tasks.tasks.length} tasks`)
      return tasks
    }
  } catch (error) {
    console.error('[Agent Memory] Error loading:', error)
  }
  return null
}

/**
 * Save agent memory
 */
function saveAgentMemory(tasks) {
  try {
    const tasksFile = path.join(AGENT_MEMORY_DIR, 'tasks.json')
    tasks.last_updated = new Date().toISOString()
    fs.writeFileSync(tasksFile, JSON.stringify(tasks, null, 2))
  } catch (error) {
    console.error('[Agent Memory] Error saving:', error)
  }
}

/**
 * Start backend service
 */
function startBackend() {
  if (isBackendRunning) {
    console.log('[Backend] Already running')
    return
  }

  console.log('[Backend] Starting...')
  console.log(`[Backend] Directory: ${BACKEND_DIR}`)
  console.log(`[Backend] Python: ${PYTHON_EXE}`)

  // Check if backend directory exists
  if (!fs.existsSync(BACKEND_DIR)) {
    console.error(`[Backend] Directory does not exist: ${BACKEND_DIR}`)
    if (mainWindow) {
      mainWindow.webContents.send('backend-error', { 
        error: `Backend directory not found: ${BACKEND_DIR}` 
      })
    }
    return
  }
  
  // Check if app.py exists
  const appPyPath = path.join(BACKEND_DIR, 'app.py')
  if (!fs.existsSync(appPyPath)) {
    console.error(`[Backend] app.py not found: ${appPyPath}`)
    if (mainWindow) {
      mainWindow.webContents.send('backend-error', { 
        error: `app.py not found: ${appPyPath}` 
      })
    }
    return
  }
  
  console.log(`[Backend] App file exists: ${appPyPath}`)
  
  // Setup environment for installed mode
  const env = { ...process.env }
  if (isPackaged) {
    // Add resources directory to PYTHONPATH so imports work
    const resourcesPath = process.resourcesPath
    const currentPythonPath = env.PYTHONPATH || ''
    env.PYTHONPATH = `${resourcesPath}${path.delimiter}${currentPythonPath}`
    console.log(`[Backend] PYTHONPATH set to: ${env.PYTHONPATH}`)
  }
  
  // Start uvicorn from backend directory
  console.log(`[Backend] Starting uvicorn from: ${BACKEND_DIR}`)
  backendProcess = spawn(PYTHON_EXE, [
    '-m', 'uvicorn',
    'app:app',
    '--host', '0.0.0.0',
    '--port', BACKEND_PORT.toString(),
    ...(isPackaged ? [] : ['--reload'])  // No reload in production
  ], {
    cwd: BACKEND_DIR,
    shell: true,
    stdio: ['ignore', 'pipe', 'pipe'],
    env: env
  })

  backendProcess.stdout.on('data', (data) => {
    const output = data.toString()
    console.log(`[Backend] ${output}`)
    
    // Check if backend started successfully
    if (output.includes('Uvicorn running')) {
      isBackendRunning = true
      updateTrayMenu()
      if (mainWindow) {
        mainWindow.webContents.send('backend-status', { running: true })
      }
    }
  })

  backendProcess.stderr.on('data', (data) => {
    const error = data.toString()
    console.error(`[Backend Error] ${error}`)
    if (mainWindow) {
      mainWindow.webContents.send('backend-error', { error })
    }
  })

  backendProcess.on('exit', (code) => {
    console.log(`[Backend] Process exited with code ${code}`)
    isBackendRunning = false
    updateTrayMenu()
    if (mainWindow) {
      mainWindow.webContents.send('backend-status', { running: false })
    }
    
    // Auto-restart if not manually stopped
    if (code !== 0 && !app.isQuitting) {
      console.log('[Backend] Auto-restarting in 3 seconds...')
      setTimeout(() => {
        if (!app.isQuitting) {
          startBackend()
        }
      }, 3000)
    }
  })

  // Wait a bit for backend to start
  setTimeout(() => {
    if (!isBackendRunning) {
      console.log('[Backend] Checking if started...')
      // Try to ping backend
      const http = require('http')
      const req = http.get(`http://localhost:${BACKEND_PORT}/api/health`, (res) => {
        if (res.statusCode === 200) {
          isBackendRunning = true
          updateTrayMenu()
          if (mainWindow) {
            mainWindow.webContents.send('backend-status', { running: true })
          }
        }
      })
      req.on('error', () => {
        console.log('[Backend] Not responding yet, will retry...')
      })
    }
  }, 5000)
}

/**
 * Stop backend service
 */
function stopBackend() {
  if (backendProcess) {
    console.log('[Backend] Stopping...')
    isBackendRunning = false
    backendProcess.kill()
    backendProcess = null
    updateTrayMenu()
    if (mainWindow) {
      mainWindow.webContents.send('backend-status', { running: false })
    }
  }
}

/**
 * Create main window
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    },
    // icon: path.join(__dirname, 'assets', 'icon.png'),  // Commented out - add icon later
    show: false
  })

  // Load frontend
  const indexPath = path.join(FRONTEND_DIST, 'index.html')
  console.log('[Frontend] Loading from:', indexPath)
  console.log('[Frontend] Path exists:', fs.existsSync(indexPath))
  
  if (fs.existsSync(indexPath)) {
    // Use file:// protocol for Electron
    const fileUrl = `file://${indexPath.replace(/\\/g, '/')}`
    console.log('[Frontend] Loading URL:', fileUrl)
    mainWindow.loadURL(fileUrl)
  } else {
    console.log('[Frontend] Index.html not found, trying dev server...')
    // Development mode - load from Vite dev server
    mainWindow.loadURL('http://localhost:3000')
  }
  
  // Enable DevTools for debugging
  // Enable DevTools for debugging (only in development or if DEBUG env var is set)
  if (!isPackaged || process.env.DEBUG === '1') {
    mainWindow.webContents.openDevTools()
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
    
    // Start backend after window is ready
    setTimeout(() => {
      startBackend()
    }, 1000)
  })

  // Handle window close
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault()
      mainWindow.hide()
      
      // Show notification
      if (Notification.isSupported()) {
        new Notification({
          title: 'System3 Ultra',
          body: 'Application is running in the background. Click tray icon to restore.'
          // icon: path.join(__dirname, 'assets', 'icon.png')  // Commented out - add icon later
        }).show()
      }
    }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

/**
 * Create system tray
 */
function createTray() {
  // Tray disabled for now - requires icon file
  // TODO: Add icon.png to assets folder and uncomment below
  /*
  const iconPath = path.join(__dirname, 'assets', 'icon.png')
  tray = new Tray(iconPath)
  
  updateTrayMenu()
  
  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide()
      } else {
        mainWindow.show()
        mainWindow.focus()
      }
    }
  })
  */
}

/**
 * Update tray menu
 */
function updateTrayMenu() {
  if (!tray) return  // Skip if tray not created
  
  const menu = Menu.buildFromTemplate([
    {
      label: 'System3 Ultra',
      enabled: false
    },
    { type: 'separator' },
    {
      label: isBackendRunning ? 'Backend: Running' : 'Backend: Stopped',
      enabled: false
    },
    {
      label: isBackendRunning ? 'Stop Backend' : 'Start Backend',
      click: () => {
        if (isBackendRunning) {
          stopBackend()
        } else {
          startBackend()
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Show Dashboard',
      click: () => {
        if (mainWindow) {
          mainWindow.show()
          mainWindow.focus()
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.isQuitting = true
        stopBackend()
        app.quit()
      }
    }
  ])
  
  tray.setContextMenu(menu)
  tray.setToolTip('System3 Ultra Dashboard')
}

/**
 * IPC Handlers
 */
function setupIpcHandlers() {
  // Get backend status
  ipcMain.handle('get-backend-status', () => {
    return { running: isBackendRunning, port: BACKEND_PORT }
  })

  // Start/Stop backend
  ipcMain.handle('control-backend', (event, action) => {
    if (action === 'start') {
      startBackend()
      return { success: true }
    } else if (action === 'stop') {
      stopBackend()
      return { success: true }
    }
    return { success: false, error: 'Invalid action' }
  })

  // Get agent memory
  ipcMain.handle('get-agent-memory', () => {
    return loadAgentMemory()
  })

  // Save agent memory
  ipcMain.handle('save-agent-memory', (event, tasks) => {
    saveAgentMemory(tasks)
    return { success: true }
  })

  // Show notification
  ipcMain.handle('show-notification', (event, { title, body }) => {
    if (Notification.isSupported()) {
      new Notification({ title, body }).show()
      return { success: true }
    }
    return { success: false }
  })

  // Download proof pack
  ipcMain.handle('download-proof-pack', async () => {
    const { dialog } = require('electron')
    const result = await dialog.showSaveDialog(mainWindow, {
      title: 'Save Proof Pack',
      defaultPath: 'proof_pack.zip',
      filters: [{ name: 'ZIP Files', extensions: ['zip'] }]
    })
    
    if (!result.canceled) {
      // Generate proof pack (will be implemented in backend)
      return { success: true, path: result.filePath }
    }
    return { success: false, canceled: true }
  })
}

/**
 * App lifecycle
 */
app.whenReady().then(() => {
  // Load agent memory
  const memory = loadAgentMemory()
  if (memory) {
    console.log(`[Agent] Resuming from memory: ${memory.run_id}`)
  }

  createTray()
  createWindow()
  setupIpcHandlers()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  // Don't quit on Windows - keep running in tray
  if (process.platform !== 'darwin') {
    // Keep app running
  }
})

app.on('before-quit', () => {
  app.isQuitting = true
  stopBackend()
})

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  console.error('[Uncaught Exception]', error)
  // Don't crash - log and continue
})

process.on('unhandledRejection', (reason, promise) => {
  console.error('[Unhandled Rejection]', reason)
  // Don't crash - log and continue
})
