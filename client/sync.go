package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/google/uuid"
)

type BookToDownload struct {
	Id, Url string
}

func GatherSyncedBooks(directory string) ([]string, error) {
	entries, err := os.ReadDir(directory)
	if err != nil {
		return nil, err
	}

	var fileNames []string

	for _, file := range entries {
		if fileName, err := uuid.Parse(file.Name()); err == nil {
			fileNames = append(fileNames, strings.TrimRight(fileName.String(), ".epub"))
		}
	}
	return fileNames, nil
}

// Synchronises the local state with what's on the server.
// Returns the amount of books synced, or an error.
func Synchronise(httpClient http.Client, config *Config) (int, error) {
	localFiles, err := GatherSyncedBooks(config.BooksDirectory)
	if err != nil {
		return -1, err
	}

	jsonBody, err := json.Marshal(localFiles)
	if err != nil {
		return -1, err
	}

	request, err := http.NewRequest(
		"POST",
		fmt.Sprintf("%s/api/v1/sync/", strings.TrimRight(config.Endpoint, "/")),
		bytes.NewReader(jsonBody),
	)
	if err != nil {
		return -1, err
	}

	request.Header.Add("Authorization", fmt.Sprintf("Bearer %s", config.Token))

	response, err := httpClient.Do(request)
	if err != nil {
		return -1, err
	}

	responseBody, err := io.ReadAll(response.Body)
	if err != nil {
		return -1, errors.New("error reading response body")
	}

	if response.StatusCode != 200 {
		return -1, fmt.Errorf("received non-success statuscode %d from server with error %s", response.StatusCode, responseBody)
	}

	var booksToDownload []BookToDownload
	if err = json.Unmarshal(responseBody, &booksToDownload); err != nil {
		return -1, err
	}

	for _, book := range booksToDownload {
		DownloadFile(&httpClient, book, fmt.Sprintf("%s/%s.epub", config.BooksDirectory, book.Id), config.Token)
	}

	return len(booksToDownload), nil
}

func DownloadFile(httpClient *http.Client, book BookToDownload, pathOnDisk string, accessToken string) error {
	outputFile, err := os.Create(pathOnDisk)
	if err != nil {
		return err
	}
	defer outputFile.Close()

	log.Printf("Getting file at %s", book.Url)

	request, err := http.NewRequest(
		"GET", book.Url, nil,
	)
	if err != nil {
		return err
	}

	request.Header.Add("Authorization", fmt.Sprintf("Bearer %s", accessToken))

	resp, err := httpClient.Do(request)
	if err != nil {
		return err
	}

	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return fmt.Errorf("invalid response from server: %d", resp.StatusCode)
	}

	io.Copy(outputFile, resp.Body)

	return nil
}
