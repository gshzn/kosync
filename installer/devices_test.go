package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestKobosFromPaths_empty(t *testing.T) {
	got := kobosFromPaths([]string{})
	if len(got) != 0 {
		t.Errorf("expected empty slice, got %v", got)
	}
}

func TestKobosFromPaths_noKoboDir(t *testing.T) {
	dir := t.TempDir()
	got := kobosFromPaths([]string{dir})
	if len(got) != 0 {
		t.Errorf("expected empty slice, got %v", got)
	}
}

func TestKobosFromPaths_withKoboDir(t *testing.T) {
	dir := t.TempDir()
	if err := os.Mkdir(filepath.Join(dir, ".kobo"), 0755); err != nil {
		t.Fatal(err)
	}
	got := kobosFromPaths([]string{dir})
	if len(got) != 1 {
		t.Fatalf("expected 1 device, got %d", len(got))
	}
	if got[0].MountPath != dir {
		t.Errorf("MountPath: want %q, got %q", dir, got[0].MountPath)
	}
	if got[0].Name != filepath.Base(dir) {
		t.Errorf("Name: want %q, got %q", filepath.Base(dir), got[0].Name)
	}
}
