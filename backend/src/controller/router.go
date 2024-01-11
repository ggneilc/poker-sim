//handles the api endpoint routing
package controller

import (
	"github.com/gofiber/fiber/v2"
)

func SetupRoutes(app *fiber.App) {

	app.Get("/home", displayHome)

}

func displayHome(c *fiber.Ctx) error {
	return c.SendFile("../public/home.html", false)
}
