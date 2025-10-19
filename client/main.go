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

func ShowErrorAndExit(err error) {
	ShowDialog(
		"Oops",
		fmt.Sprintf("An error occured while trying to synchronise: %s", err),
		"OK",
	)

	os.Exit(1)
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

	currentExecutable, err := os.Executable()
	if err != nil {
		ShowErrorAndExit(err)
	}

	config, err := LoadConfig(filepath.Dir(currentExecutable))
	if err != nil {
		if !notRunningOnKobo {
			ShowErrorAndExit(err)
		} else {
			panic(err)
		}
	}

	if !notRunningOnKobo {
		err := ShowDialog("Starting synchronisation", "This might take a while, please press OK to confirm.", "OK")
		if err != nil {
			ShowErrorAndExit(err)
		}
	}

	err = os.MkdirAll(config.BooksDirectory, 0744)
	if err != nil {
		if !notRunningOnKobo {
			ShowErrorAndExit(err)
		} else {
			panic(err)
		}
	}

	var httpClient = http.Client{
		Timeout: time.Duration(15) * time.Second,
	}

	log.Println("Starting synchronisation...")
	booksSynced, err := Synchronise(httpClient, config)

	if err != nil {
		if !notRunningOnKobo {
			ShowErrorAndExit(err)
		} else {
			panic(err)
		}
	}

	if !notRunningOnKobo {
		if booksSynced > 0 {
			err = ShowDialog(
				"Complete!",
				fmt.Sprintf("We synchronised %d new book(s). Press OK to reload.", booksSynced),
				"OK",
			)

			if err != nil {
				ShowErrorAndExit(err)
			}

			TriggerReload()

			log.Println("Triggered reload")
		} else {
			ShowDialog("Complete!", "Nothing new found to synchronise.", "OK")
		}
	}
}
