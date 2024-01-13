//function code for api endpoints
package controller

import (
	"fmt"
	"log"
	"math/rand"
	"time"

	"github.com/gofiber/contrib/websocket"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/session"
)

type User struct {
	ID       string
	Username string
	Money    int
}

type Room struct {
	ID      string
	status  string
	players []User
}

var Rooms = make(map[string]Room)
var store = session.New()

func createNewUser() User {
	userID := genRandomId()
	return User{
		ID:       userID,
		Username: "Guest" + userID, // Default username, can be customized later
		Money:    1000,             // Initial amount of money
	}
}

func findUserByID(userID string, players []User) (User, bool) {
	for _, player := range players {
		if player.ID == userID {
			return player, true
		}
	}
	return User{}, false
}

//	---------------------- Websockets ----------------------  //
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

//	---------------------- Index Page ----------------------  //
//display home screen for authenticated user -> /home
func displayHome(c *fiber.Ctx) error {

	username := c.FormValue("username")

	return c.Render("home", fiber.Map{
		"Username": username,
	})
}

//	---------------------- Generate Game Room ----------------------  //
//Generate unique room ID & create room -> /new
func generateGame(c *fiber.Ctx) error {
	roomID := genRandomId()

	//create new room
	newRoom := Room{
		ID:      roomID,
		status:  "open",
		players: []User{},
	}

	//store room in map
	Rooms[roomID] = newRoom

	return c.Redirect("/game/" + roomID)
}

// Display game for the user -> /game/:roomId
func displayGame(c *fiber.Ctx) error {
	//retrieve room
	roomID := c.Params("roomID")
	room, ok := Rooms[roomID]
	if !ok {
		fmt.Println("can't find room")
		return c.SendStatus(fiber.StatusNotFound)
	}

	//retrieve current session
	sess, err := store.Get(c)
	if err != nil {
		return err
	}

	userID := sess.Get("userID")
	if userID == nil {
		// Create a new user for the person joining the room
		newUser := createNewUser()

		// Add the new user to the room's list of players
		room.players = append(room.players, newUser)

		// Update the room in the global rooms map
		Rooms[roomID] = room

		// Save the user's ID in the session
		sess.Set("userID", newUser.ID)
		if err := sess.Save(); err != nil {
			return err
		}

		return c.Render("game", fiber.Map{
			"Username":    newUser.Username,
			"playerCount": len(room.players),
			"Money":       newUser.Money,
			"roomID":      roomID,
		})

	} else {
		user, found := findUserByID(userID.(string), room.players)
		if !found {
			return c.SendStatus(fiber.StatusNotFound)
		}

		return c.Render("game", fiber.Map{
			"Username":    user.Username,
			"playerCount": len(room.players),
			"Money":       user.Money,
			"roomID":      roomID,
		})
	}
}

func genRandomId() string {
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
	return gameId
}
