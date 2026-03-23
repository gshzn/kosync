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
MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwHhcNMTUwNjA0MTEwNDM4
WhcNMzUwNjA0MTEwNDM4WjBPMQswCQYDVQQGEwJVUzEpMCcGA1UEChMgSW50ZXJu
ZXQgU2VjdXJpdHkgUmVzZWFyY2ggR3JvdXAxFTATBgNVBAMTDElTUkcgUm9vdCBY
MTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAK3oJHP0FDfzm54rVygc
h77ct984kIxuPOZXoHj3dcKi/vVqbvYATyjb3miGbESTtrFj/RQSa78f0uoxmyF+
0TM8ukj13Xnfs7j/EvEhmkvBioZxaUpmZmyPfjxwv60pIgbz5MDmgK7iS4+3mX6U
A5/TR5d8mUgjU+g4rk8Kb4Mu0UlXjIB0ttov0DiNewNwIRt18jA8+o+u3dpjq+sW
T8KOEUt+zwvo/7V3LvSye0rgTBIlDHCNAymg4VMk7BPZ7hm/ELNKjD+Jo2FR3qyH
B5T0Y3HsLuJvW5iB4YlcNHlsdu87kGJ55tukmi8mxdAQ4Q7e2RCOFvu396j3x+UC
B5iPNgiV5+I3lg02dZ77DnKxHZu8A/lJBdiB3QW0KtZB6awBdpUKD9jf1b0SHzUv
KBds0pjBqAlkd25HN7rOrFleaJ1/ctaJxQZBKT5ZPt0m9STJEadao0xAH0ahmbWn
OlFuhjuefXKnEgV4We0+UXgVCwOPjdAvBbI+e0ocS3MFEvzG6uBQE3xDk3SzynTn
jh8BCNAw1FtxNrQHusEwMFxIt4I7mKZ9YIqioymCzLq9gwQbooMDQaHWBfEbwrbw
qHyGO0aoSCqI3Haadr8faqU9GY/rOPNk3sgrDQoo//fb4hVC1CLQJ13hef4Y53CI
rU7m2Ys6xt0nUW7/vGT1M0NPAgMBAAGjQjBAMA4GA1UdDwEB/wQEAwIBBjAPBgNV
HRMBAf8EBTADAQH/MB0GA1UdDgQWBBR5tFnme7bl5AFzgAiIyBpY9umbbjANBgkq
hkiG9w0BAQsFAAOCAgEAVR9YqbyyqFDQDLHYGmkgJykIrGF1XIpu+ILlaS/V9lZL
ubhzEFnTIZd+50xx+7LSYK05qAvqFyFWhfFQDlnrzuBZ6brJFe+GnY+EgPbk6ZGQ
3BebYhtF8GaV0nxvwuo77x/Py9auJ/GpsMiu/X1+mvoiBOv/2X/qkSsisRcOj/KK
NFtY2PwByVS5uCbMiogziUwthDyC3+6WVwW6LLv3xLfHTjuCvjHIInNzktHCgKQ5
ORAzI4JMPJ+GslWYHb4phowim57iaztXOoJwTdwJx4nLCgdNbOhdjsnvzqvHu7Ur
TkXWStAmzOVyyghqpZXjFaH3pO3JLF+l+/+sKAIuvtd7u+Nxe5AW0wdeRlN8NwdC
jNPElpzVmbUq4JUagEiuTDkHzsxHpFKVK7q4+63SM1N95R1NbdWhscdCb+ZAJzVc
oyi3B43njTOQ5yOf+1CceWxG1bQVs5ZufpsMljq4Ui0/1lvh+wjChP4kqKOJ2qxq
4RgqsahDYVvTH9w7jXbyLeiNdd8XM2w9U/t7y0Ff/9yi0GE44Za4rF2LN9d11TPA
mRGunUHBcnWEvgJBQl9nJEiU0Zsnvgc/ubhPgXRR4Xq37Z0j4r7g1SgEEzwxA57d
emyPxgcYxn/eR44/KJ4EBs+lVDR3veyJm+kXQ99b21/+jh5Xos1AnX5iItreGCc=
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
