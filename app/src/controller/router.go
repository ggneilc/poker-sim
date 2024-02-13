//handles the api endpoint routing
package controller

import (
	"github.com/gofiber/contrib/websocket"
	"github.com/gofiber/fiber/v2"
)

var testUser User

func SetupRoutes(app *fiber.App) {

	app.Get("/home", displayHome)
	app.Post("/home", displayHome)

	app.Get("/new", generateGame)
	app.Get("/ws/:id", websocket.New(establishWebsocket))
}

