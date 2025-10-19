package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

type Config struct {
	Token          string
	Endpoint       string
	BooksDirectory string
}

func LoadConfig(rootDir string) (*Config, error) {
	configPath := fmt.Sprintf("%s/.kosyncConfig.json", strings.TrimRight(rootDir, "/"))
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		defaultData, err := defaultConfigFile()
		if err != nil {
			return nil, err
		}

		err = os.MkdirAll(rootDir, 0744)
		if err != nil {
			return nil, err
		}

		err = os.WriteFile(configPath, defaultData, 0744)
		if err != nil {
			return nil, err
		}
	}

	configString, err := os.ReadFile(configPath)
	if err != nil {
		return nil, err
	}

	var config Config
	err = json.Unmarshal(configString, &config)
	if err != nil {
		return nil, err
	}

	return &config, nil
}

func defaultConfigFile() ([]byte, error) {
	return json.Marshal(Config{
		Token:          "foo",
		Endpoint:       "https://books.guus.tech/",
		BooksDirectory: "/mnt/onboard/kosync",
	})
}
