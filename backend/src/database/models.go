//Define Objects that exist in Database
package database

import (
	"gorm.io/gorm"
)

type User struct {
	ID uint `gorm:primaryKey`

	Username string
	Password string
	Email    string

	Wins        uint
	Winnings    int
	CurrentGame GameRoom
}

type GameRoom struct {
	gorm.Model

	Status  uint
	Players []User
}

/**
type Game struct {
	ID uint  `gorm:primaryKey`

	Winnings 		int

	HandsDealt 		uint
	HandsPlayed 	uint
	HandsWon 		uint
}
*/
