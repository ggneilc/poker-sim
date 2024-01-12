# poker-sim

Poker Simulator website designed to provide an absolute random experience, and not prioritize flashy moments or favoritism

---

## Design Goal

- Have a proof of randomness to achieve a completely authentic table-top poker experience on the web
- Anyone can play, no matter their pc specs & internet connection -> runs fast & anywhere, with minimal memory footprint
- Sleek material design instead of the typical p0rn-ad looking online casino games
- Optionally create an account to track your games and see your player stats

We want this game to feel just as fair as when you shuffle the deck of cards in your own home. Once we have the code working, we will also house a mathematical proof of randomness to put any doubters to rest that you win or lose completely fair and square.

---

## Tech Stack

The goal of this app is to have it be *simple*. Logan McDonald and I have little experience when it comes to the complete full stack development, having a working knowledge of reactjs and barebones html/css/js. I could center a div, but that's about it (and not without google).

The plan is to create a Web 1.0 application using the MPA architecture, but use the htmx library to not have to sacrifice on user experience, increase performance, and reduce memory.

To supplement htmx on the frontend, we will also be using **golang**, specifically the _gofiber_ framework that builds on the fasthttp go library to have further increased performance and speed, also supporting the use of websockets, templating, and server side rendering.

Lastly, we will more than likely use a simple MySQL database, but that feature is still up for discussion.
