//handles the api endpoint routing
package controller

import (
	"log"
	"math/rand"
	"time"

	"github.com/gofiber/contrib/websocket"
	"github.com/gofiber/fiber/v2"
)

func SetupRoutes(app *fiber.App) {

	app.Get("/home", displayHome)
	app.Post("/home", displayHome)

	app.Get("/new", generateGame)
	app.Get("/ws/:id", websocket.New(establishWebsocket))
}

//how tf does this actually work -> to create game state
func establishWebsocket(c *websocket.Conn) {
	// c.Locals is added to the *websocket.Conn
	log.Println(c.Locals("allowed"))  // true
	log.Println(c.Params("id"))       // 123
	log.Println(c.Query("v"))         // 1.0
	log.Println(c.Cookies("session")) // ""

	// websocket.Conn bindings https://pkg.go.dev/github.com/fasthttp/websocket?tab=doc#pkg-index
	var (
		mt  int
		msg []byte
		err error
	)
	for {
		if mt, msg, err = c.ReadMessage(); err != nil {
			log.Println("read:", err)
			break
		}
		log.Printf("recv: %s", msg)

		if err = c.WriteMessage(mt, msg); err != nil {
			log.Println("write:", err)
			break
		}
	}
}

func displayHome(c *fiber.Ctx) error {

	username := c.FormValue("username")

	return c.Render("home", fiber.Map{
		"Username": username,
	})
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
