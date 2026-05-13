const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain, dialog, shell } = require('electron')
const path = require('path')
const fs = require('fs')

let mainWindow = null
let tray = null
let focusWindow = null
let chatWindow = null

const DRINK_INTERVAL = 30 * 60 * 1000
let drinkTimer = null

function createPetWindow() {
  mainWindow = new BrowserWindow({
    width: 200,
    height: 200,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  })

  mainWindow.loadFile('pet.html')
  mainWindow.setIgnoreMouseEvents(false)

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  startDrinkReminder()
}

function createFocusWindow() {
  if (focusWindow) {
    focusWindow.focus()
    return
  }

  focusWindow = new BrowserWindow({
    width: 150,
    height: 150,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  })

  focusWindow.loadFile('focus.html')
  focusWindow.on('closed', () => {
    focusWindow = null
  })
}

function createChatWindow() {
  if (chatWindow) {
    chatWindow.focus()
    return
  }

  chatWindow = new BrowserWindow({
    width: 400,
    height: 600,
    frame: true,
    alwaysOnTop: true,
    resizable: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  })

  chatWindow.loadFile('chat.html')
  chatWindow.on('closed', () => {
    chatWindow = null
  })
}

let currentDrinkInterval = DRINK_INTERVAL

function setDrinkInterval(interval) {
  currentDrinkInterval = interval
  startDrinkReminder()
}

function startDrinkReminder() {
  if (drinkTimer) clearInterval(drinkTimer)
  drinkTimer = setInterval(() => {
    if (mainWindow) {
      mainWindow.webContents.send('drink-reminder')
    }
  }, currentDrinkInterval)
}

function createTray() {
  const iconPath = path.join(__dirname, 'assets', 'tray-icon.png')
  let icon
  if (fs.existsSync(iconPath)) {
    icon = nativeImage.createFromPath(iconPath)
  } else {
    icon = nativeImage.createEmpty()
  }

  tray = new Tray(icon)

  let drinkRadio15 = { label: '15分钟', type: 'radio', click: () => setDrinkInterval(15 * 60 * 1000) }
  let drinkRadio30 = { label: '30分钟', type: 'radio', checked: true, click: () => setDrinkInterval(30 * 60 * 1000) }
  let drinkRadio60 = { label: '60分钟', type: 'radio', click: () => setDrinkInterval(60 * 60 * 1000) }

  const contextMenu = Menu.buildFromTemplate([
    { label: '显示宠物', click: () => mainWindow && mainWindow.show() },
    { label: '专注模式', click: () => createFocusWindow() },
    { label: '聊天', click: () => createChatWindow() },
    { type: 'separator' },
    { label: '喝水提醒设置', submenu: [
      drinkRadio15,
      drinkRadio30,
      drinkRadio60,
    ]},
    { type: 'separator' },
    { label: '退出', click: () => {
      if (drinkTimer) clearInterval(drinkTimer)
      app.quit()
    }},
  ])

  tray.setToolTip('小星星桌面宠物')
  tray.setContextMenu(contextMenu)

  tray.on('double-click', () => {
    if (mainWindow) mainWindow.show()
  })
}

app.whenReady().then(() => {
  createPetWindow()
  createTray()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createPetWindow()
  }
})

ipcMain.on('delete-file', async (event, filePath) => {
  if (!filePath) return

  try {
    await shell.trashItem(filePath)
    event.reply('delete-file-result', { success: true })
  } catch (error) {
    event.reply('delete-file-result', { success: false, error: error.message })
  }
})

ipcMain.on('open-chat', () => {
  createChatWindow()
})

ipcMain.on('open-focus-mode', () => {
  createFocusWindow()
})

ipcMain.on('show-context-menu', (event) => {
  const menu = Menu.buildFromTemplate([
    { label: '专注模式', click: () => createFocusWindow() },
    { label: '聊天', click: () => createChatWindow() },
    { type: 'separator' },
    { label: '移动', enabled: false },
    { label: '关闭', click: () => mainWindow && mainWindow.hide() },
  ])
  menu.popup(BrowserWindow.fromWebContents(event.sender))
})