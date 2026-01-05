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
	certPool, err := x509.SystemCertPool()
	if err != nil {
		return nil, err
	}

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
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIDqDCCAy6gAwIBAgISBkCdvKVt29LL8nXywIgmAvUxMAoGCCqGSM49BAMDMDIx
CzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MQswCQYDVQQDEwJF
NzAeFw0yNjAxMDUxMzM3MTRaFw0yNjA0MDUxMzM3MTNaMBUxEzARBgNVBAMTCmtv
c3luYy5hcHAwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAAQMsZGddfRlAMPZpKOz
qgiNeOy+hNniq938wJdNSFdipgrglkJSacUJ+4TB5O7SUrw4D8PfvVcZBXO1XNAW
6WTDo4ICPzCCAjswDgYDVR0PAQH/BAQDAgeAMB0GA1UdJQQWMBQGCCsGAQUFBwMB
BggrBgEFBQcDAjAMBgNVHRMBAf8EAjAAMB0GA1UdDgQWBBSPQp4zqOD22j7kfA19
f7RHilV/0DAfBgNVHSMEGDAWgBSuSJ7chx1EoG/aouVgdAR4wpwAgDAyBggrBgEF
BQcBAQQmMCQwIgYIKwYBBQUHMAKGFmh0dHA6Ly9lNy5pLmxlbmNyLm9yZy8wNQYD
VR0RBC4wLIIOYXBpLmtvc3luYy5hcHCCDmFwcC5rb3N5bmMuYXBwggprb3N5bmMu
YXBwMBMGA1UdIAQMMAowCAYGZ4EMAQIBMC0GA1UdHwQmMCQwIqAgoB6GHGh0dHA6
Ly9lNy5jLmxlbmNyLm9yZy81MC5jcmwwggELBgorBgEEAdZ5AgQCBIH8BIH5APcA
dQDRbqmlaAd+ZjWgPzel3bwDpTxBEhTUiBj16TGzI8uVBAAAAZuOld2oAAAEAwBG
MEQCIGQsDPwvD1SsScVLZeuCJSqUu+t1Ke73DdgqYFb3sW/iAiBAwWJkrg33uZbS
fKbpmXGWMCnknbgETSX2+ZBLTldmwgB+AOMjjfKNoojgquCs8PqQyYXwtr/10qUn
sAH8HERYxLboAAABm46V3/QACAAABQAuWZmSBAMARzBFAiEAtKeXlCxvBeKDwHGU
hqge9L5X20UwXSWUzd1dpwFTGdwCICWYcs0/Y3vnLOmjLRugAjGX9v5vkQOZ1PYS
ZHwTV7erMAoGCCqGSM49BAMDA2gAMGUCMD0FSS1BgErN5d4zp/8PCnjkwtar8/FT
l1WP+1LYOWi+WpbYF3DQKkKtDsBzZP+FCAIxAMGjSvtovzFh1MKPTK5d4WOylqCh
sIKtmigwDKSp0Sgl1bRgx2yV5EWrIzda6lgvRQ==
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
