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

func kobosFromPaths(paths []string) []KoboDevice {
	devices := []KoboDevice{}
	for _, p := range paths {
		if _, err := os.Stat(filepath.Join(p, ".kobo")); err == nil {
			devices = append(devices, KoboDevice{
				Name:      filepath.Base(p),
				MountPath: p,
			})
		}
	}
	return devices
}

func getMountPathsDarwin() []string {
	entries, err := os.ReadDir("/Volumes")
	if err != nil {
		return nil
	}
	var paths []string
	for _, e := range entries {
		if e.IsDir() || e.Type()&os.ModeSymlink != 0 {
			paths = append(paths, filepath.Join("/Volumes", e.Name()))
		}
	}
	return paths
}

func getMountPathsWindows() []string {
	out, err := exec.Command(
		"wmic", "logicaldisk", "where", "DriveType=2", "get", "DeviceID",
	).Output()
	if err != nil {
		return nil
	}
	var paths []string
	for _, line := range strings.Split(string(out), "\n") {
		line = strings.TrimSpace(line)
		if len(line) == 2 && line[1] == ':' {
			paths = append(paths, line+`\`)
		}
	}
	return paths
}

func getRemovableMountPaths() []string {
	switch runtime.GOOS {
	case "darwin":
		return getMountPathsDarwin()
	case "windows":
		return getMountPathsWindows()
	default:
		return nil
	}
}

func (a *App) ListKoboDevices() []KoboDevice {
	return kobosFromPaths(getRemovableMountPaths())
}
