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
	testFiles := []string{"29CE38BB-EBB5-457C-93A8-D50480CCAFC7.epub", "0FF7C8FB-D51D-4C63-ACEC-B3AA5402165B.epub", "C3DDB812-0289-4B6F-A282-A6F10B117DFD.epub"}
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

	var expectedFiles []string
	for _, f := range testFiles {
		expectedFiles = append(expectedFiles, strings.TrimSuffix(f, ".epub"))
	}

	assert.ElementsMatch(t, expectedFiles, files)

	os.RemoveAll(tempDir)
}

const TEST_BOOK = "test_fixtures/01980fd0-c9b1-4f75-beb7-7cd5e847482c.epub"

func TestDownloadNewFiles(t *testing.T) {
	httpmock.Activate(t)

	var url = "http://localhost:8000/api/v1/books/66243753-4F8C-4330-9F9E-6B9EF2F0974E"

	httpmock.RegisterMatcherResponder("POST", "http://kosync.test/api/v1/sync/", httpmock.HeaderExists("Authorization"),
		httpmock.NewStringResponder(200, fmt.Sprintf(`[
			{
				"id": "66243753-4F8C-4330-9F9E-6B9EF2F0974E",
				"url": "%s"
			}
		]`, url)).Once(),
	)

	httpmock.RegisterMatcherResponder("GET", url, httpmock.HeaderExists("Authorization"),
		httpmock.NewBytesResponder(200, httpmock.File(TEST_BOOK).Bytes()).Once(),
	)

	tempDir := t.TempDir()

	Synchronise(*http.DefaultClient, &Config{
		BooksDirectory: tempDir,
		Token:          "foo",
		Endpoint:       "http://kosync.test/",
	})

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

	httpmock.RegisterResponder("POST", "/api/v1/sync/",
		httpmock.NewStringResponder(200, `[]`).Once(),
	)

	tempDir := t.TempDir()
	copyFile(TEST_BOOK, fmt.Sprintf("%s/%s", tempDir, strings.Split(TEST_BOOK, "/")[1]))

	Synchronise(*http.DefaultClient, &Config{
		BooksDirectory: tempDir,
	})

	assert.Equal(t, 1, httpmock.GetTotalCallCount())

	entries, err := os.ReadDir(tempDir)
	if err != nil {
		panic(err)
	}

	assert.Equal(t, 1, len(entries))
}
