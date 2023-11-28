package main

import (
	"fmt"
	"math/rand"
)

const (
	ics   = 50
	mgrs  = 10
	teams = 10
)

var (
	pmfIC  = []int{1, 1, 1, 1, 1, 1, 1, 1, 1, 2}
	pmfMgr = []int{4, 4, 4, 5, 5}
)

func main() {
	teamSlice := make([]int, teams)
	for i := 1; i <= teams; i++ {
		teamSlice[i-1] = i
	}

	fmt.Println("individual,team")

	for i := 1; i <= ics; i++ {
		n := pmfIC[rand.Intn(len(pmfIC))]
		for _, t := range choose(n, teamSlice) {
			fmt.Printf("ic%02d,%02d\n", i, t)
		}
	}

	for i := 1; i <= mgrs; i++ {
		n := pmfMgr[rand.Intn(len(pmfMgr))]
		for _, t := range choose(n, teamSlice) {
			fmt.Printf("mgr%02d,%02d\n", i, t)
		}
	}
}

func choose(n int, t []int) []int {
	rand.Shuffle(len(t), func(i, j int) {
		t[i], t[j] = t[j], t[i]
	})

	choices := make([]int, n)
	copy(choices, t)
	return choices
}
