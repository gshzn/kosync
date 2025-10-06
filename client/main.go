package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"time"
)

func ShowError(err error) error {
	return ShowDialog(
		"Oops",
		fmt.Sprintf("An error occured while trying to synchronise: %s", err),
		"OK",
	)
}

func main() {
	log.Println("Starting")

	if os.Args[0] == "reload" {
		TriggerReload()

		return
	}

	var notRunningOnKobo bool
	flag.BoolVar(&notRunningOnKobo, "non-kobo", false, "Run without connecting to DBus")

	flag.Parse()

	if !notRunningOnKobo {
		err := ShowDialog("Starting synchronisation", "This might take a while, please press OK to confirm.", "OK")
		if err != nil {
			ShowError(err)
			return
		}
	}

	currentExecutable, err := os.Executable()
	if err != nil {
		panic(err)
	}

	currentDirectory := fmt.Sprintf("%s/books", filepath.Dir(currentExecutable))
	os.MkdirAll(currentDirectory, 0744)

	var httpClient = http.Client{
		Timeout: time.Duration(15) * time.Second,
	}

	log.Println("Starting synchronisation...")
	booksSynced, err := Synchronise(httpClient, currentDirectory)

	if err != nil {
		ShowError(err)
		return
	}

	if !notRunningOnKobo {
		if booksSynced > 0 {
			err = ShowDialog(
				"Complete!",
				fmt.Sprintf("We synchronised %d new book. Press OK to reload.", booksSynced),
				"OK",
			)

			if err != nil {
				ShowError(err)
				return
			}

			TriggerReload()

			log.Println("Triggered reload")
		} else {
			ShowDialog("Complete!", "Nothing new found to synchronise.", "OK")
		}
	}
}
