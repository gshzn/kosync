package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
)

type BookToDownload struct {
	Id, Url string
}

func GatherLocalFiles(directory string) ([]string, error) {
	entries, err := os.ReadDir(directory)
	if err != nil {
		return nil, err
	}

	var fileNames []string

	for _, file := range entries {
		fileNames = append(fileNames, file.Name())
	}
	return fileNames, nil
}

func Synchronise(httpClient http.Client, directory string) error {
	localFiles, err := GatherLocalFiles(directory)
	if err != nil {
		return err
	}

	jsonBody, err := json.Marshal(localFiles)
	if err != nil {
		return err
	}

	request, err := http.NewRequest("POST", "http://192.168.50.215:8000/api/v1/sync", bytes.NewReader(jsonBody))
	if err != nil {
		return err
	}

	response, err := httpClient.Do(request)
	if err != nil {
		return err
	}

	responseBody, err := io.ReadAll(response.Body)
	if err != nil {
		return errors.New("error reading response body")
	}

	if response.StatusCode != 200 {
		return fmt.Errorf("received non-success statuscode %d from server with error %s", response.StatusCode, responseBody)
	}

	var booksToDownload []BookToDownload
	if err = json.Unmarshal(responseBody, &booksToDownload); err != nil {
		return err
	}

	for _, book := range booksToDownload {
		DownloadFile(&httpClient, book, fmt.Sprintf("%s/%s.epub", directory, book.Id))
	}

	return nil
}

func DownloadFile(httpClient *http.Client, book BookToDownload, pathOnDisk string) error {
	outputFile, err := os.Create(pathOnDisk)
	if err != nil {
		return err
	}
	defer outputFile.Close()

	resp, err := httpClient.Get(book.Url)
	if err != nil {
		return err
	}

	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return errors.New(fmt.Sprintf("invalid response from server: %d", resp.StatusCode))
	}

	io.Copy(outputFile, resp.Body)

	return nil
}
