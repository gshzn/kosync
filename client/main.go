package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
)

func main() {
	log.Println("Starting")

	if os.Args[0] == "reload" {
		TriggerReload()

		return
	}

	var runningOnKobo bool
	flag.BoolVar(&runningOnKobo, "non-kobo", false, "Run without connecting to DBus")

	if runningOnKobo {
		err := ShowDialog("Starting synchronisation", "This might take a while, please press OK to confirm.", "OK")
		if err != nil {
			panic(err)
		}
	}

	currentExecutable, err := os.Executable()
	if err != nil {
		panic(err)
	}

	currentDirectory := fmt.Sprintf("%s/books", filepath.Dir(currentExecutable))
	os.MkdirAll(currentDirectory, 0744)

	log.Println("Downloading file...")
	err = Synchronise(*http.DefaultClient, currentDirectory)

	if err != nil {
		panic(err)
	}

	if runningOnKobo {
		err = ShowDialog("Complete!", "We synchronised 1 new book. Press OK to reload.", "OK")
		if err != nil {
			panic(err)
		}
		TriggerReload()
	}

	log.Println("Triggered reload")
}
