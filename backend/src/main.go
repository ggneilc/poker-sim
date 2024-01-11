//Starts the HTTP server
package main

import (
	"log"

	"github.com/ggneilc/poker-sim/src/controller"
	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Static("/", "../../frontend")

	controller.SetupRoutes(app)

	log.Fatal(app.Listen(":3000"))
}
