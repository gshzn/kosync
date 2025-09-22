package main

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestSynchroniseGatherFiles(t *testing.T) {
	// Create a temporary directory for testing
	tempDir := t.TempDir()

	// Create some test files
	testFiles := []string{"file1.txt", "file2.txt", "file3.txt"}
	for _, file := range testFiles {
		err := os.WriteFile(tempDir+"/"+file, []byte("test content"), 0644)
		if err != nil {
			t.Fatalf("Failed to create test file: %v", err)
		}
	}

	// Test GatherLocalFiles
	files, err := GatherLocalFiles(tempDir)
	if err != nil {
		t.Fatalf("GatherLocalFiles failed: %v", err)
	}

	assert.Equal(t, testFiles, files)

	os.RemoveAll(tempDir)
}

func TestDownloadNewFiles(t *testing.T) {
	// test to issue requests to download new files and store the response on disk
	// ultimately it should trigger a call to trigger reload

}
