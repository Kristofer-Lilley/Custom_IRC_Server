package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"sync"
)

type MessageStruct struct {
	Timestamp string `json:"Timestamp"`
	Name      string `json:"Name"`
	Content   string `json:"Content"`
}

type ChannelStruct struct {
	ChannelNames []string `json:"ChannelNames"`
}

type ClientStruct struct {
	Conn       net.Conn
	Addr       string
	WriteMutex sync.Mutex
}

// var channelSlice []ChannelStruct = make([]ChannelStruct, 0, 5) // Preallocate capacity for 5 channels
var channelSlice []ChannelStruct = []ChannelStruct{
	{ChannelNames: []string{"#general", "#random", "#help"}},
	// add more ChannelStruct entries here if you want grouped lists
}

var storageSlice []MessageStruct = make([]MessageStruct, 0, 100) // Preallocate capacity for 100 messages

//TODO Send storage Slice to new clients on connection

var connSlice []*ClientStruct
var connSliceMutex sync.RWMutex

func main() {
	//Listen for incoming connections on port 8080
	ln, err := net.Listen("tcp", ":9090")
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
	client := &ClientStruct{Conn: conn, Addr: remoteAddr}
	connSliceMutex.Lock()
	connSlice = append(connSlice, client)
	connSliceMutex.Unlock()

	client.WriteMutex.Lock()
	encoder := json.NewEncoder(client.Conn)
	if err := encoder.Encode(channelSlice); err != nil {
		fmt.Printf("Error sending channels to %s: %v\n", remoteAddr, err)
	}
	client.WriteMutex.Unlock()
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
		handleMessages(msg)
		fmt.Printf("Received: %+v\n", msg)
	}
}

func handleMessages(msg MessageStruct) {

	if len(storageSlice) >= 100 {
		storageSlice = storageSlice[1:] // Remove oldest
	}
	storageSlice = append(storageSlice, msg)
	distributeNewMessage(msg)
}

func distributeNewMessage(msg MessageStruct) {
	connSliceMutex.RLock()
	clients := make([]*ClientStruct, len(connSlice))
	copy(clients, connSlice)
	connSliceMutex.RUnlock()

	for _, client := range clients {
		client.WriteMutex.Lock()
		encoder := json.NewEncoder(client.Conn)
		err := encoder.Encode(msg)
		client.WriteMutex.Unlock()
		if err != nil {
			fmt.Printf("Error sending message to %s: %v\n", client.Addr, err)
		}
	}
}
