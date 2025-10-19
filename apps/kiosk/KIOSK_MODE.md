# Kiosk Mode Documentation

## Overview

The Chrona Kiosk application includes a fullscreen kiosk mode designed for deployment on dedicated tablet devices. This mode provides enhanced security and user experience for time tracking kiosks.

## Features

### 1. Fullscreen Mode
- Native browser fullscreen API support
- Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- Automatic fullscreen on kiosk mode activation

### 2. Security Features
- **Prevent text selection**: Users cannot select and copy text
- **Disable context menu**: Right-click menu is disabled
- **Block keyboard shortcuts**: Common browser shortcuts are blocked
- **Prevent navigation**: Back/forward gestures disabled
- **Hide UI controls**: Optional hiding of exit buttons

### 3. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+F` | Toggle fullscreen mode |
| `Ctrl+Shift+K` | Toggle exit button visibility |

**Note**: In kiosk mode, `F11` and `Esc` are blocked to prevent users from exiting fullscreen.

## Configuration

### Environment Variables

Add these variables to your `.env` file:

```bash
# Auto-enter kiosk mode on startup (true/false)
VITE_AUTO_KIOSK_MODE=false
```

### Auto-Kiosk Mode

Set `VITE_AUTO_KIOSK_MODE=true` to automatically enter kiosk mode when the application loads. This is useful for dedicated kiosk devices.

## Usage

### Manual Activation

1. Load the kiosk application
2. Click the "Activer mode kiosque" button in the top-right corner
3. The application will enter fullscreen and kiosk mode

### Exiting Kiosk Mode

**Method 1: Exit Button**
- Click the "Quitter mode kiosque" button (if visible)

**Method 2: Keyboard Shortcut**
- Press `Ctrl+Shift+K` to toggle exit button visibility
- Click the exit button

**Method 3: Browser Controls**
- Force exit with browser-specific shortcuts (not recommended for production)

## Deployment Recommendations

### For Dedicated Kiosk Tablets

1. **Enable auto-kiosk mode**:
   ```bash
   VITE_AUTO_KIOSK_MODE=true
   ```

2. **Hide exit button** using keyboard shortcut after setup:
   - Press `Ctrl+Shift+K` to hide the exit button
   - Button remains hidden until toggled again

3. **Configure kiosk device settings**:
   - Disable device sleep/screen timeout
   - Set application as default on boot
   - Restrict access to device settings

### Browser Kiosk Mode (Recommended)

For maximum security, use browser kiosk mode in addition to the application kiosk mode:

**Chrome Kiosk Mode**:
```bash
chrome --kiosk --app=http://localhost:5174
```

**Firefox Kiosk Mode**:
```bash
firefox --kiosk http://localhost:5174
```

### Android Kiosk Mode

For Android tablets, use Android's built-in kiosk features:

1. **Enable Guided Access** (Samsung) or **Screen Pinning**
2. Configure tablet in **Single App Mode**
3. Use **Mobile Device Management (MDM)** for enterprise deployments

## Security Considerations

### What Kiosk Mode Prevents

✅ Text selection and copying
✅ Right-click context menu
✅ Common keyboard shortcuts (F11, Ctrl+W, etc.)
✅ Accidental navigation away from the app
✅ Screenshot capabilities (via browser)

### What Kiosk Mode Does NOT Prevent

❌ Physical device tampering
❌ Network attacks
❌ Operating system level access
❌ Force restart/shutdown

**Recommendation**: Combine application kiosk mode with:
- Physical device security (locked enclosure)
- Operating system kiosk mode
- Network security (firewall, VPN)
- Regular security audits

## Troubleshooting

### Fullscreen not working

**Issue**: Fullscreen mode doesn't activate

**Solutions**:
1. Check browser permissions (some browsers block fullscreen)
2. Ensure user interaction triggered fullscreen (required by browsers)
3. Try different browser (Chrome recommended)

### Exit button not visible

**Issue**: Cannot exit kiosk mode

**Solution**:
1. Press `Ctrl+Shift+K` to toggle exit button visibility
2. If keyboard doesn't work, restart the browser

### Auto-kiosk mode not working

**Issue**: Application doesn't auto-enter kiosk mode

**Solutions**:
1. Check `.env` file: `VITE_AUTO_KIOSK_MODE=true`
2. Clear browser cache and reload
3. Ensure environment variable is loaded (check browser console)

## Development vs Production

### Development Mode
- Auto-kiosk mode: `false`
- Exit button: visible
- Developer tools: accessible

### Production Mode
- Auto-kiosk mode: `true`
- Exit button: hidden (toggle with `Ctrl+Shift+K`)
- Browser kiosk mode enabled
- Physical device secured

## Technical Implementation

The kiosk mode uses React hooks:

- `useFullscreen`: Manages fullscreen API with cross-browser support
- `useKioskMode`: Orchestrates kiosk features (fullscreen, event blocking, UI controls)

Key technologies:
- Fullscreen API
- Event listeners (keyboard, mouse)
- CSS user-select prevention
- React state management

## Browser Compatibility

| Browser | Fullscreen | Keyboard Block | Context Menu Block |
|---------|------------|----------------|-------------------|
| Chrome 71+ | ✅ | ✅ | ✅ |
| Firefox 64+ | ✅ | ✅ | ✅ |
| Safari 13+ | ✅ | ✅ | ✅ |
| Edge 79+ | ✅ | ✅ | ✅ |

## Support

For issues or questions about kiosk mode:
1. Check this documentation
2. Review browser console for errors
3. Test in different browsers
4. Contact support with device/browser details
