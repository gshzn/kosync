package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
)

var apiURL = "https://api.kosync.app"

func installKoSync(mountPath, accessToken, baseURL string) (bool, error) {
	req, err := http.NewRequest(http.MethodGet, baseURL+"/api/v1/download", nil)
	if err != nil {
		return false, err
	}
	req.Header.Set("Authorization", "Bearer "+accessToken)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return false, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return false, fmt.Errorf("download failed with status %d", resp.StatusCode)
	}

	dest := filepath.Join(mountPath, ".kobo", "KoboRoot.tgz")
	f, err := os.Create(dest)
	if err != nil {
		return false, err
	}
	defer f.Close()

	if _, err := io.Copy(f, resp.Body); err != nil {
		return false, err
	}

	if err := f.Close(); err != nil {
		return false, err
	}

	return true, nil
}

func (a *App) InstallKoSync(mountPath, accessToken string) (bool, error) {
	return installKoSync(mountPath, accessToken, apiURL)
}
