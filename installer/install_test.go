package main

import (
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func makeFakeTgz() []byte {
	// minimal valid gzip stream (empty archive)
	return []byte{
		0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0xff, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00,
	}
}

func TestInstallKoSync_writesFileToKoboDir(t *testing.T) {
	body := makeFakeTgz()
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/octet-stream")
		w.WriteHeader(http.StatusOK)
		w.Write(body)
	}))
	defer srv.Close()

	dir := t.TempDir()
	if err := os.Mkdir(filepath.Join(dir, ".kobo"), 0755); err != nil {
		t.Fatal(err)
	}

	ok, err := installKoSync(dir, "test-token", srv.URL)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !ok {
		t.Fatal("expected true, got false")
	}

	dest := filepath.Join(dir, ".kobo", "KoboRoot.tgz")
	got, err := os.ReadFile(dest)
	if err != nil {
		t.Fatalf("file not written: %v", err)
	}
	if string(got) != string(body) {
		t.Errorf("file contents mismatch: want %v bytes, got %v bytes", len(body), len(got))
	}
}

func TestInstallKoSync_sendsAuthHeader(t *testing.T) {
	var gotHeader string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotHeader = r.Header.Get("Authorization")
		w.Write(makeFakeTgz())
	}))
	defer srv.Close()

	dir := t.TempDir()
	os.Mkdir(filepath.Join(dir, ".kobo"), 0755)

	installKoSync(dir, "my-secret-token", srv.URL)

	want := "Bearer my-secret-token"
	if gotHeader != want {
		t.Errorf("Authorization header: want %q, got %q", want, gotHeader)
	}
}

func TestInstallKoSync_serverError(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "internal server error", http.StatusInternalServerError)
	}))
	defer srv.Close()

	dir := t.TempDir()
	os.Mkdir(filepath.Join(dir, ".kobo"), 0755)

	ok, err := installKoSync(dir, "token", srv.URL)
	if err == nil {
		t.Fatal("expected error, got nil")
	}
	if ok {
		t.Fatal("expected false on server error")
	}
	if !strings.Contains(err.Error(), "500") {
		t.Errorf("error should mention status code, got: %v", err)
	}
}
