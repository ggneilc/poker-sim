//Starts the HTTP server
package main

import (
	"github.com/ggneilc/poker-sim/src/controller"
	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Static("/", "../../frontend")

	controller.SetupRoutes(app)

	app.Listen(":3000")
}
