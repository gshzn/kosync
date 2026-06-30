package main

import (
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
)

type KoboDevice struct {
	Name      string `json:"name"`
	MountPath string `json:"mountPath"`
}

type mountPoint struct {
	path string
	name string
}

func kobosFromMounts(mounts []mountPoint) []KoboDevice {
	devices := []KoboDevice{}
	for _, m := range mounts {
		if _, err := os.Stat(filepath.Join(m.path, ".kobo")); err == nil {
			devices = append(devices, KoboDevice{
				Name:      m.name,
				MountPath: m.path,
			})
		}
	}
	return devices
}

func getMountsDarwin() []mountPoint {
	entries, err := os.ReadDir("/Volumes")
	if err != nil {
		return nil
	}
	var mounts []mountPoint
	for _, e := range entries {
		if e.IsDir() || e.Type()&os.ModeSymlink != 0 {
			mounts = append(mounts, mountPoint{
				path: filepath.Join("/Volumes", e.Name()),
				name: e.Name(),
			})
		}
	}
	return mounts
}

func parseWindowsMounts(out string) []mountPoint {
	var mounts []mountPoint
	for _, line := range strings.Split(out, "\n") {
		line = strings.TrimSpace(line)
		fields := strings.Fields(line)
		if len(fields) == 0 {
			continue
		}
		first := fields[0]
		if len(first) == 2 && first[1] == ':' && first[0] >= 'A' && first[0] <= 'Z' {
			name := first
			if len(fields) >= 2 {
				name = fields[1]
			}
			mounts = append(mounts, mountPoint{
				path: first + `\`,
				name: name,
			})
		}
	}
	return mounts
}

func getMountsWindows() []mountPoint {
	cmd := exec.Command(
		"powershell", "-NoProfile", "-Command",
		`Get-WmiObject Win32_LogicalDisk | Where-Object { $_.DriveType -eq 2 } | Select-Object DeviceID, VolumeName`,
	)
	setSysProcAttr(cmd)
	out, err := cmd.Output()
	if err != nil {
		return nil
	}
	return parseWindowsMounts(string(out))
}

func getRemovableMounts() []mountPoint {
	switch runtime.GOOS {
	case "darwin":
		return getMountsDarwin()
	case "windows":
		return getMountsWindows()
	default:
		return nil
	}
}

func (a *App) ListKoboDevices() []KoboDevice {
	return kobosFromMounts(getRemovableMounts())
}
