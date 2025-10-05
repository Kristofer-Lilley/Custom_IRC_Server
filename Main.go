package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"net"
)

type MessageStruct struct {
	Timestamp string `json:"Timestamp"`
	Name      string `json:"Name"`
	Content   string `json:"Content"`
}

type ClientStruct struct {
	Conn net.Conn
	Addr string
}

var storageSlice []MessageStruct

//TODO Send storage Slice to new clients on connection

var connSlice []ClientStruct

func main() {
	//Listen for incoming connections on port 8080
	ln, err := net.Listen("tcp", ":8080")
	if err != nil {
		fmt.Println(err)
		return
	}

	//Handle connections
	for {
		conn, err := ln.Accept()
		if err != nil {
			fmt.Println(err)
			continue
		}
		go handleConnection(conn)
	}
}

func handleConnection(conn net.Conn) {
	defer conn.Close()
	remoteAddr := conn.RemoteAddr().String()
	connSlice = append(connSlice, ClientStruct{Conn: conn, Addr: remoteAddr})

	fmt.Println("New connection from", remoteAddr)

	reader := bufio.NewReader(conn)
	for {
		line, err := reader.ReadBytes('\n')
		if err != nil {
			if err != io.EOF {
				fmt.Println("Error reading:", err)
			}
			break
		}
		var msg MessageStruct
		err = json.Unmarshal(line, &msg)
		if err != nil {
			fmt.Println("Error decoding JSON:", err)
			continue
		}
		storeMessages(msg)
		fmt.Printf("Received: %+v\n", msg)
	}
}

func storeMessages(msg MessageStruct) {
	storageSlice = append(storageSlice, msg)
	if len(storageSlice) > 100 {
		storageSlice = storageSlice[1:] // Remove oldest
	}
	distributeNewMessage(msg)
}

func distributeNewMessage(msg MessageStruct) {
	// Placeholder for distributing the new message to all connected clients
	// This could involve iterating over a list of client connections and sending the message
}
