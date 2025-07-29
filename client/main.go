package main

import (
	"crypto/tls"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"

	"github.com/godbus/dbus/v5"
)

func main() {
	log.Println("Starting")

	if os.Args[0] == "reload" {
		TriggerReload()

		return
	}

	currentExecutable, err := os.Executable()
	if err != nil {
		panic(err)
	}

	currentDirectory := filepath.Dir(currentExecutable)

	log.Println("Downloading file...")
	err = DownloadFile("http://vm.guus.tech/book.epub", fmt.Sprintf("%s/new.epub", currentDirectory))
	if err != nil {
		panic(err)
	}

	TriggerReload()

	log.Println("Triggered reload")
}

func DownloadFile(url string, pathOnDisk string) error {
	outputFile, err := os.Create(pathOnDisk)
	if err != nil {
		return err
	}
	defer outputFile.Close()

	httpClient := &http.Client{
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		},
	}

	resp, err := httpClient.Get(url)

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

func TriggerReload() {
	conn, err := dbus.ConnectSystemBus()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Failed to connect to session bus:", err)
		os.Exit(1)
	}

	obj := conn.Object("com.github.shermp.nickeldbus", "/nickeldbus")
	obj.Call("com.github.shermp.nickeldbus.pfmRescanBooks", 0)

	if err != nil {
		panic(err)
	}

	conn.Close()
}
