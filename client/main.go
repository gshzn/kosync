package main

import (
	"crypto/tls"
	"crypto/x509"
	"errors"
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

func getHttpClient() (*http.Client, error) {
	// certPool, err := x509.SystemCertPool()
	certPool := x509.NewCertPool()
	// if err != nil {
	// 	return nil, err
	// }

	ok := certPool.AppendCertsFromPEM([]byte(
		`-----BEGIN CERTIFICATE-----
MIIDlDCCAxqgAwIBAgISBWLqEu/CMUgbX8N6Y0nRAI80MAoGCCqGSM49BAMDMDIx
CzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MQswCQYDVQQDEwJF
ODAeFw0yNTEyMTUxMTMyMjNaFw0yNjAzMTUxMTMyMjJaMBsxGTAXBgNVBAMTEGtv
c3luYy5ndXVzLnRlY2gwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAAS/A9FSXqjf
4GzMEdwoohFcYyU6QUK2mRHl/0mKjjlTCjqrBtdkcFl86WUlnBg8u1mcJQkH9SeB
PZ9QmPZpMMlHo4ICJTCCAiEwDgYDVR0PAQH/BAQDAgeAMB0GA1UdJQQWMBQGCCsG
AQUFBwMBBggrBgEFBQcDAjAMBgNVHRMBAf8EAjAAMB0GA1UdDgQWBBQeQtbIAzgU
A5uQA9KP3frklQncUDAfBgNVHSMEGDAWgBSPDROi9i5+0VBsMxg4XVmOI3KRyjAy
BggrBgEFBQcBAQQmMCQwIgYIKwYBBQUHMAKGFmh0dHA6Ly9lOC5pLmxlbmNyLm9y
Zy8wGwYDVR0RBBQwEoIQa29zeW5jLmd1dXMudGVjaDATBgNVHSAEDDAKMAgGBmeB
DAECATAtBgNVHR8EJjAkMCKgIKAehhxodHRwOi8vZTguYy5sZW5jci5vcmcvNTMu
Y3JsMIIBCwYKKwYBBAHWeQIEAgSB/ASB+QD3AHUAZBHEbKQS7KeJHKICLgC8q08o
B9QeNSer6v7VA8l9zfAAAAGbIf4C/QAABAMARjBEAiAMcK+oBXUUaGEDSVb6KCay
RrKJul6bsT7mbpzl5Aj0NQIgf5K4jlAQOFVCbnvvmKfYTSi9JN2yHbfgitGdbXkg
9TwAfgBxfpXzwjiKbbHjhEk9MeFaqWIIdi1CAOAFDNBntaZh4gAAAZsh/gPUAAgA
AAUABDdQbQQDAEcwRQIhAIQRwEXgQsSZecRi7eeJKUpTCY52pkzgDWpJ3SvQkIyd
AiB42uTVuOjezysmu8MbU8L5nguyvvcYUCJMKMHUQoIKazAKBggqhkjOPQQDAwNo
ADBlAjEAqwCzlWmhHtiEgXWgqHydLD31eQg5KaFc2Nt6PswqNtGsm2EO9Fsu22dL
9pKXJTG1AjAHrOY6abLoR/xVwpX1vL5DmKv0DJUByWObCdqzoQJRl/UA2TrJJnKF
wkakcjHKyHU=
-----END CERTIFICATE-----`,
	))
	if !ok {
		return nil, errors.New("unable to trust KoSync certificate")
	}

	return &http.Client{
		Timeout: time.Duration(15) * time.Second,
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{
				RootCAs: certPool,
			},
		},
	}, nil

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
	httpClient, err := getHttpClient()
	if err != nil {
		if !notRunningOnKobo {
			ShowErrorAndExit(err)
		} else {
			panic(err)
		}
	}

	log.Println("Starting synchronisation...")
	booksSynced, err := Synchronise(*httpClient, config)

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
