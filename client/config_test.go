package main

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

// Test to parse config file
func TestReadConfigFile(t *testing.T) {
	tmpDir := "/tmp/kosyncTests/"

	defer os.RemoveAll(tmpDir)

	result, err := LoadConfig(tmpDir)
	if err != nil {
		t.Fatal(err)
	}

	assert.Equal(t, &Config{
		Token:          "foo",
		Endpoint:       "https://books.guus.tech/",
		BooksDirectory: "/mnt/onboard/kosync",
	}, result)
}

// Test to handle error reading file
