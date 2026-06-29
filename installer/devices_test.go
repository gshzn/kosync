package main

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func TestParseWindowsMounts(t *testing.T) {
	input := `
DeviceID VolumeName
-------- ----------
E:       KOBOeReader
`
	got := parseWindowsMounts(input)
	want := []mountPoint{{path: `E:\`, name: "KOBOeReader"}}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("want %v, got %v", want, got)
	}
}

func TestParseWindowsMounts_multiDrive(t *testing.T) {
	input := `
DeviceID VolumeName
-------- ----------
D:       USB_DRIVE
E:       KOBOeReader
`
	got := parseWindowsMounts(input)
	want := []mountPoint{
		{path: `D:\`, name: "USB_DRIVE"},
		{path: `E:\`, name: "KOBOeReader"},
	}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("want %v, got %v", want, got)
	}
}

func TestParseWindowsMounts_noVolumeName(t *testing.T) {
	input := `
DeviceID VolumeName
-------- ----------
E:
`
	got := parseWindowsMounts(input)
	want := []mountPoint{{path: `E:\`, name: "E:"}}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("want %v, got %v", want, got)
	}
}

func TestParseWindowsMounts_empty(t *testing.T) {
	input := `
DeviceID VolumeName
-------- ----------
`
	got := parseWindowsMounts(input)
	if len(got) != 0 {
		t.Errorf("expected empty, got %v", got)
	}
}

func TestKobosFromMounts_empty(t *testing.T) {
	got := kobosFromMounts([]mountPoint{})
	if len(got) != 0 {
		t.Errorf("expected empty slice, got %v", got)
	}
}

func TestKobosFromMounts_noKoboDir(t *testing.T) {
	dir := t.TempDir()
	got := kobosFromMounts([]mountPoint{{path: dir, name: "TestDrive"}})
	if len(got) != 0 {
		t.Errorf("expected empty slice, got %v", got)
	}
}

func TestKobosFromMounts_withKoboDir(t *testing.T) {
	dir := t.TempDir()
	if err := os.Mkdir(filepath.Join(dir, ".kobo"), 0755); err != nil {
		t.Fatal(err)
	}
	got := kobosFromMounts([]mountPoint{{path: dir, name: "KOBOeReader"}})
	if len(got) != 1 {
		t.Fatalf("expected 1 device, got %d", len(got))
	}
	if got[0].MountPath != dir {
		t.Errorf("MountPath: want %q, got %q", dir, got[0].MountPath)
	}
	if got[0].Name != "KOBOeReader" {
		t.Errorf("Name: want %q, got %q", "KOBOeReader", got[0].Name)
	}
}
