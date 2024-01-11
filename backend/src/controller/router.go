//handles the api endpoint routing
package controller

import (
	"math/rand"
	"time"

	"github.com/gofiber/fiber/v2"
)

func SetupRoutes(app *fiber.App) {

	app.Get("/home", displayHome)
	app.Get("/new", generateGame)

}

func displayHome(c *fiber.Ctx) error {
	return c.SendFile("../public/home.html", false)
}

func generateGame(c *fiber.Ctx) error {
	s1 := rand.NewSource(time.Now().UnixNano())
	r1 := rand.New(s1)

	upper := [26]string{"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"}
	lower := [26]string{"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"}
	nums := [10]string{"1", "2", "3", "4", "5", "6", "7", "8", "9", "0"}

	gameId := ""

	for i := 0; i < 5; i++ {
		gameId = gameId + upper[r1.Intn(25)]
		gameId = gameId + lower[r1.Intn(25)]
		gameId = gameId + nums[r1.Intn(9)]
	}

	return c.SendFile("../../frontend/game.html", false)

}
