package main

import (
	"errors"
	"log"

	"github.com/godbus/dbus/v5"
)

const DBUS_DESTINATION string = "com.github.shermp.nickeldbus"
const DBUS_PATH string = "/nickeldbus"

func DbusObject(connection *dbus.Conn) (dbus.BusObject, error) {
	var dbusConnection *dbus.Conn
	if connection == nil {
		dbusConnection, err := dbus.ConnectSystemBus()
		if err != nil {
			return nil, err
		}

		defer dbusConnection.Close()
	} else {
		dbusConnection = connection
	}

	dbusObj := dbusConnection.Object(DBUS_DESTINATION, dbus.ObjectPath(DBUS_PATH))

	return dbusObj, nil
}

func ShowDialog(title string, body string, acceptBtnText string) error {
	dbusConnection, err := dbus.ConnectSystemBus()
	if err != nil {
		return err
	}

	defer dbusConnection.Close()

	dbusObject, err := DbusObject(dbusConnection)
	if err != nil {
		return err
	}

	dbusObject.Call("com.github.shermp.nickeldbus.dlgConfirmCreate", dbus.FlagNoReplyExpected, false)

	dbusObject.Call("com.github.shermp.nickeldbus.dlgConfirmSetModal", dbus.FlagNoReplyExpected, true)
	dbusObject.Call("com.github.shermp.nickeldbus.dlgConfirmSetAccept", dbus.FlagNoReplyExpected, acceptBtnText)
	dbusObject.Call("com.github.shermp.nickeldbus.dlgConfirmSetBody", dbus.FlagNoReplyExpected, body)
	dbusObject.Call("com.github.shermp.nickeldbus.dlgConfirmSetTitle", dbus.FlagNoReplyExpected, title)

	dbusObject.Call("com.github.shermp.nickeldbus.dlgConfirmShow", dbus.FlagNoReplyExpected)

	log.Println("Called all dbus methods")

	if err = dbusConnection.AddMatchSignal(
		dbus.WithMatchInterface(DBUS_DESTINATION),
		dbus.WithMatchObjectPath(dbus.ObjectPath(DBUS_PATH)),
	); err != nil {
		return err
	}

	channel := make(chan *dbus.Signal, 1)
	dbusConnection.Signal(channel)
	defer dbusConnection.RemoveSignal(channel)
	for msg := range channel {
		if msg.Name == "com.github.shermp.nickeldbus.dlgConfirmResult" {
			return nil
		}
	}

	return errors.New("unable to handle dialog confirm click")
}
