//Starts the HTTP server
package main

import (
	"log"

	"github.com/ggneilc/poker-sim/src/controller"
	"github.com/gofiber/contrib/websocket"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/template/html/v2"
)

func main() {
	// Create a new view engine
	engine := html.New("../views", ".html")

	app := fiber.New(fiber.Config{
		Views: engine,
	})

	app.Use("/ws", func(c *fiber.Ctx) error {
		// IsWebSocketUpgrade returns true if the client
		// requested upgrade to the WebSocket protocol.
		if websocket.IsWebSocketUpgrade(c) {
			c.Locals("allowed", true)
			return c.Next()
		}
		return fiber.ErrUpgradeRequired
	})

	//serve static files at index/ & game/ (SSR & styles/script)
	app.Static("/", "../views")
	app.Static("/game", "../views")

	controller.SetupRoutes(app)

	log.Fatal(app.Listen(":3000"))
}
