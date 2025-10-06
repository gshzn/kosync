package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"testing"

	"github.com/jarcoal/httpmock"
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
	files, err := GatherSyncedBooks(tempDir)
	if err != nil {
		t.Fatalf("GatherLocalFiles failed: %v", err)
	}

	assert.Equal(t, testFiles, files)

	os.RemoveAll(tempDir)
}

const TEST_BOOK = "test_fixtures/01980fd0-c9b1-4f75-beb7-7cd5e847482c.epub"

func TestDownloadNewFiles(t *testing.T) {
	httpmock.Activate(t)

	var url = "http://localhost:8000/api/v1/books/66243753-4F8C-4330-9F9E-6B9EF2F0974E"

	httpmock.RegisterResponder("POST", "/api/v1/sync",
		httpmock.NewStringResponder(200, fmt.Sprintf(`[
			{
				"id": "66243753-4F8C-4330-9F9E-6B9EF2F0974E",
				"url": "%s"
			}
		]`, url)).Once(),
	)

	httpmock.RegisterResponder("GET", url,
		httpmock.NewBytesResponder(200, httpmock.File(TEST_BOOK).Bytes()).Once(),
	)

	tempDir := t.TempDir()

	Synchronise(*http.DefaultClient, tempDir)

	assert.Equal(t, 2, httpmock.GetTotalCallCount())

	entries, err := os.ReadDir(tempDir)
	if err != nil {
		panic(err)
	}

	assert.Equal(t, 1, len(entries))
}

func copyFile(sourceFile string, dest string) error {
	destWriter, err := os.OpenFile(dest, os.O_CREATE|os.O_WRONLY, 0666)

	if err != nil {
		panic(err)
	}

	sourceReader, err := os.Open(sourceFile)
	if err != nil {
		return err
	}

	if _, err := io.Copy(destWriter, sourceReader); err != nil {
		return err
	}

	return nil
}

func TestSynchroniseNothingNew(t *testing.T) {
	httpmock.Activate(t)

	httpmock.RegisterResponder("POST", "/api/v1/sync",
		httpmock.NewStringResponder(200, `[]`).Once(),
	)

	tempDir := t.TempDir()
	copyFile(TEST_BOOK, fmt.Sprintf("%s/%s", tempDir, strings.Split(TEST_BOOK, "/")[1]))

	Synchronise(*http.DefaultClient, tempDir)

	assert.Equal(t, 1, httpmock.GetTotalCallCount())

	entries, err := os.ReadDir(tempDir)
	if err != nil {
		panic(err)
	}

	assert.Equal(t, 1, len(entries))
}
