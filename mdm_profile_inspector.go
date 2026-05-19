// mdm_profile_inspector.go -- Parse and inspect iOS MDM profiles
// Compile: go build -o mdm_inspector mdm_profile_inspector.go
// Usage: ./mdm_inspector profile.mobileconfig

package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"os"
	"strings"
)

func main() {
	flag.Parse()
	if flag.NArg() < 1 {
		fmt.Println("Usage: mdm_inspector <profile.mobileconfig>")
		os.Exit(1)
	}

	file := flag.Arg(0)
	data, err := ioutil.ReadFile(file)
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		os.Exit(1)
	}

	content := string(data)
	fmt.Println("\n📋 MDM Profile Inspector\n")

	// Extract key fields
	inspectField := func(label, key string) {
		if idx := strings.Index(content, key); idx != -1 {
			start := idx + len(key)
			end := strings.Index(content[start:], "</string>")
			if end > 0 {
				val := strings.TrimSpace(content[start : start+end])
				fmt.Printf("  %-25s %s\n", label+":", val)
			}
		}
	}

	inspectField("Organization", "<key>OrganizationInfo</key>")
	inspectField("MDM Server", "<key>ServerURL</key>")
	inspectField("Device Name", "<key>DeviceName</key>")
	inspectField("Identity", "<key>PayloadIdentifier</key>")

	if strings.Contains(content, "MDMServerURL") {
		fmt.Println("\n⚠️  MDM Enrollment Detected")
		fmt.Println("   Profile enforces device management via remote server.")
	}

	if strings.Contains(content, "RestrictedSSIDs") {
		fmt.Println("⚠️  WiFi Restrictions Applied")
	}

	if strings.Contains(content, "ManagedApplicationList") {
		fmt.Println("⚠️  App Whitelisting Active")
	}

	fmt.Println()
}
