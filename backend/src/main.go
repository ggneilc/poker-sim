//Starts the HTTP server
package main

import (
	"log"

	"github.com/ggneilc/poker-sim/src/controller"
	"github.com/gofiber/contrib/websocket"
	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Use("/ws", func(c *fiber.Ctx) error {
		// IsWebSocketUpgrade returns true if the client
		// requested upgrade to the WebSocket protocol.
		if websocket.IsWebSocketUpgrade(c) {
			c.Locals("allowed", true)
			return c.Next()
		}
		return fiber.ErrUpgradeRequired
	})

	app.Static("/", "../../frontend")

	controller.SetupRoutes(app)

	log.Fatal(app.Listen(":3000"))
}
