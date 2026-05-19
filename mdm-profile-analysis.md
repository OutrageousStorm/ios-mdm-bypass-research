# iOS MDM Profile Analysis

Understanding Mobile Device Management on iOS and known bypass vectors.

## MDM Architecture

iOS MDM uses two channels:
1. **APNs (Apple Push Notification service)** — push certificates
2. **Device Management Profile** — installed as a config profile

## Profile Structure

MDM profiles are .mobileconfig XML files containing:
```xml
<key>PayloadType</key>
<string>com.apple.mdm</string>
<key>MagicBytes</key>
<string>MDM_MAGIC</string>
```

Key fields:
- `ServerURL` — MDM server endpoint
- `AccessRights` — what MDM can control (0xFFFF = full)
- `CheckOutWhenRemoved` — if true, device reports to server when uninstalled
- `SignMessage` — if true, requires signed commands

## Bypass Vectors (Historical/Research Only)

### 1. Profile Removal During Setup
- Interrupt setup process mid-enrollment
- Some iOS versions had race conditions during profile installation
- Modern iOS validates profile signature before completion

### 2. Airplane Mode Tricks
- Enroll while on Airplane Mode to prevent server contact
- Device stores profile locally but can't receive MDM commands
- Doesn't persist across reboot on recent iOS

### 3. iCloud Activation Lock Bypass
- Separate from MDM but often enforced together
- Requires physical device + valid Apple ID or bypass tokens
- `iforgot.apple.com` brute force historically possible (now hardened)

### 4. USB Restricted Mode
- iOS 15+: USB port locks after 1 hour without unlock
- Prevents MDM extraction via USB forensics
- Mitigated by jailbreak + USB daemon hooks

### 5. Certificate Pinning Bypass
- Some MDM servers use pinned certificates
- Network proxy + SSL interception can reveal enrollment requests
- AppleID + 2FA enrollment more resistant than username/password

## Detection Methods

### On Device
```bash
# Check if MDM enrolled (via Settings > General > Device Management)
# or via:
profiles list  # Simulator
```

### In Code
```swift
import DeviceCheck

// Check MDM status
if let token = try? DeviceCheck.shared.generateToken() {
    // Device in managed context
}
```

### Server-Side
```bash
# MDM server receives:
POST /mdm/checkin
{
    "UDID": "device-udid",
    "Topic": "com.apple.mgmt.External.UDID",
    "EnrollmentUserID": "user@company.com"
}
```

## Modern Protections

- **Cryptographic enrollment** — certificate pinning by default
- **Notarization checks** — apps signed/notarized by Apple
- **Transparency reports** — forced MDM visibility to users
- **Scheduled resets** — periodic profile re-verification
- **Attestation** — device integrity checks via Secure Enclave

## Research Notes

This is for security research and authorized testing only. Unauthorized MDM bypass or profile removal is illegal in most jurisdictions.

For legitimate MDM management:
- Use Apple Configurator 2
- Enroll via official corporate enrollment
- Use `mdm-enrollment` command (macOS)
