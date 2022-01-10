import tkinter
import random


def extractor_images(cards_images: list, card_number: str, suit: str,
                     extension: str = "png") -> None:
    """Extract playing card image from a folder.

    Extract image from a folder and appending them to a list
    containing a pair of number/face of card and tkinter.Photoimage
    object as tuple."""
    name = f"cards_png/{card_number}_{suit}.{extension}"
    image = tkinter.PhotoImage(file=name)
    cards_images.append((card_number, image))


def load_images(cards_images: list) -> None:
    suits = ["heart", "club", "diamond", "spade"]
    face_cards = ["jack", "queen", "king"]

    # extension = "png"
    # if tkinter.TkVersion >= 8.6:
    #     extension = "png"
    # else:
    #     extension = "ppm"

    for suit in suits:
        # cards from 1 to 10
        for card_number in range(1, 11):
            extractor_images(cards_images, str(card_number), suit)
        # face cards extraction:
        for face_of_card in face_cards:
            extractor_images(cards_images, 10, suit)


def deal_card(frame):
    next_card = deck.pop(0)
    tkinter.Label(frame, image=next_card[1], relief="raised").pack(side="left")
    return int(next_card[0])


def deal_dealer():
    global dealer_cards_frame
    global dealer_hand

    dealer_score = score_hand(dealer_hand)

    try:
        player_highest_score = get_players_highest_score()
        while dealer_score < player_highest_score:
            dealer_hand.append(deal_card(dealer_cards_frame))
            dealer_score = score_hand(dealer_hand)
            dealer_score_label.set(dealer_score)
        if dealer_score > 21:
            result_text.set("Players wins")
            game_over(dealer_cards_frame)
    except NameError:  # if it is the first run
        dealer_hand.append(deal_card(dealer_cards_frame))
        dealer_score = score_hand(dealer_hand)
        dealer_score_label.set(dealer_score)


def get_players_highest_score() -> int:
    """Gets the player with the highest score """
    global all_players
    player_left = get_players_left_in_game()

    current_highest_score = 0

    for each_player in player_left:
        current_player_score = all_players[each_player]["score_label"]
        current_player_score = current_player_score.get()
        if current_highest_score < current_player_score < 22:
            current_highest_score = current_player_score

    return current_highest_score


def score_hand(hand: list) -> int:
    ace_in_hand = False
    score = 0
    for card_value in hand:
        if card_value == 1 and not ace_in_hand:
            card_value = 11
            ace_in_hand = True
        score += card_value
        if score > 21 and ace_in_hand:
            score -= 10
            ace_in_hand = False
    return score


def deal_player(player_number: int):
    global players_hand

    player_data = all_players[player_number]
    player_hand = players_hand[player_number]  # list
    player_card_frame = player_data["player_cards_frame"]
    players_hand[player_number].append(deal_card(player_card_frame))
    score = score_hand(player_hand)
    player_score_label = player_data["score_label"]
    player_score_label.set(score)
    if score >= get_players_highest_score():
        turn_on_stay_button(player_number)
    if score > 21:
        destroy_current_player(player_number)


def draw_player_frames(number: int) -> dict:
    """Takes the number of players and creates tkFrames for every player

    It uses global variable named `card_frame`, where it creates new
    entries also uses another global variable named `button_frame` for
    adding new button for each new player.

    :return dict with players numbers `(int)` as keys
    and nested dict for each player with keys as `str` :
    `"score_label"`, `"player_cards_frame"`, `"button"`, `"button2"`,
    `"buttons_frame"` containing corresponding tk.object."""
    global card_frame
    global button_frame

    players = {}
    label_row_counter = 2
    row_counter = 2

    for player_number in range(1, number + 1):
        current_player = f"player{player_number}"
        score_label = tkinter.IntVar()
        # generating label rows
        tkinter.Label(card_frame, text=current_player, background="green",
                      fg="white").grid(row=label_row_counter, column=0)
        label_row_counter += 1

        tkinter.Label(
            card_frame, textvariable=score_label, background="green",
            fg="white").grid(row=label_row_counter, column=0)
        label_row_counter += 1

        # generating frame for cards
        player_cards_frame = tkinter.Frame(card_frame, background="green")
        player_cards_frame.grid(row=row_counter, column=1, sticky="ew",
                                rowspan=2)
        row_counter += 2
        # buttons frame
        current_player_button_frame = tkinter.Frame(button_frame)
        current_player_button_frame.grid(row=0, column=player_number)
        # generating buttons
        button = tkinter.Button(current_player_button_frame, text="Hit",
                                command=lambda a=player_number: deal_player(a),
                                )
        button.grid(row=0, column=0, sticky="ew")
        button2 = tkinter.Button(
            current_player_button_frame, text="Stay",
            command=lambda a=player_number: turn_off_player_buttons(a))

        button2.grid(row=1, column=0, sticky="ew")
        player_cards_frame.configure(width=width_of_cards,
                                     height=height_of_cards)
        button3_var = tkinter.BooleanVar()
        button3_var.set(False)

        button3 = tkinter.Button(
            current_player_button_frame,
            text="Ready",
            command=lambda a=player_number: player_ready(a)
        )
        button3.grid(row=2, column=0)

        players[player_number] = {
            "score_label": score_label,
            "player_cards_frame": player_cards_frame,
            "button": button,
            "button2": button2,
            "button3": [button3, False],
            "buttons_frame": current_player_button_frame
        }
    return players


def player_ready(current_player: int):
    """When this function is called it changes the button3
    text value to True
    """
    global all_players
    all_players[current_player]["button3"][1] = True  # ready button var
    disable_all_buttons_for_current_player(current_player)
    next_player = get_next_available_player(current_player)
    turn_on_player_buttons(next_player)


def get_players_that_are_ready() -> set:
    """Get set of players that clicked ready"""
    global all_players
    players_that_are_ready = set()
    for player in all_players:
        button3_var = all_players[player]["button3"][1]
        if button3_var:
            players_that_are_ready.add(player)
    return players_that_are_ready


def build_popup():
    popup = tkinter.Toplevel()
    popup.title("Player count")
    popup.geometry("260x200+250+200")
    tkinter.Label(popup, text="How much players are going to play?").grid(
        row=0, column=0)
    n = tkinter.IntVar()
    number_of_players = tkinter.Spinbox(popup, from_=1, to=7, textvariable=n,
                                        width=4)
    number_of_players.grid(row=1, column=0)

    submit_button = tkinter.Button(popup, text="Submit", command=lambda n=n: find_players_count(n))
    submit_button.grid(row=2, column=0)

    return popup


def get_dealer_score() -> int:
    return dealer_score_label.get()


def find_players_count(number) -> None:
    global players_count
    players_count = number.get()
    popup.destroy()


def clear_frame(frame):
    # destroy all widgets from frame
    for widget in frame.winfo_children():
        widget.destroy()


def game_over(player_cards_frame) -> None:
    global game_over_pic
    clear_frame(player_cards_frame)
    tkinter.Label(player_cards_frame, image=game_over_pic,
                  relief="raised", background="black").pack(side="left")


def disable_all_buttons(players_info: dict):
    """Disables all buttons"""
    players = list(players_info)
    for player in players:
        button = players_info[player]["button"]
        button2 = players_info[player]["button2"]
        button3 = players_info[player]["button3"][0]
        button["state"] = "disabled"
        button2["state"] = "disabled"
        button3["state"] = "disabled"


def disable_all_buttons_for_current_player(current_player: int):
    global all_players
    button = all_players[current_player]["button"]
    button2 = all_players[current_player]["button2"]
    button3 = all_players[current_player]["button3"][0]
    button["state"] = "disabled"
    button2["state"] = "disabled"
    button3["state"] = "disabled"


def get_players_left_in_game() -> list:
    """returns a list with all players left in game.

    It uses global var all_players"""
    global all_players
    left_players_in_game = list(all_players)
    return left_players_in_game


def turn_off_only_stay_button(current_player: int):
    global all_players
    button2 = all_players[current_player]["button2"]
    button2["state"] = "disabled"


def turn_on_stay_button(current_player: int):
    """Turns on only stay button if player reaches 21"""
    global all_players
    score = all_players[current_player]["score_label"]
    score = score.get()
    if score == 21:
        button2 = all_players[current_player]["button2"]
        button2["state"] = "active"


def player_riches_21() -> bool:
    global all_players
    global reached_21
    players_left = get_players_left_in_game()
    for player in players_left:
        player_score = all_players[player]["score_label"]
        player_score = player_score.get()
        if player_score == 21:
            reached_21 = True
            return True
    return False


def destroy_current_player(current_player) -> None:
    """Checks if player has more then 21 points and destroy buttons

    if player have more then 21 points it destroys his buttons and
    deletes him from all_players dict. This function uses global
    all_player variable."""
    global all_players

    current_player_info = all_players[current_player]
    player_button1 = current_player_info["button"]
    player_button2 = current_player_info["button2"]
    player_button3 = current_player_info["button3"][0]
    player_card_frame = current_player_info["player_cards_frame"]
    game_over(player_card_frame)
    player_button1["state"] = "disabled"
    player_button2["state"] = "disabled"
    player_button3["state"] = "disabled"
    next_available_player = get_next_available_player(current_player)
    del all_players[current_player]
    turn_on_player_buttons(next_available_player)


def destroy_dealer():
    global dealer_cards_frame
    game_over(dealer_cards_frame)


def disable_ready_button(button3):
    button3["state"] = "disabled"


# def stop_program():
#     main_window.destroy()


# def new_game(popup):
#     global players_hand
#     global all_players
#     global cards
#     global deck
#     global dealer_hand
#     popup.destroy()
#
#     deck = cards.copy()
#     random.shuffle(deck)
#
#     dealer_hand.clear()
#     all_players.clear()
#     players_hand.clear()
#     popup = build_popup()
#     build_player_count_and_frames()


# def new_game_popup():
#     new_game_window = tkinter.Toplevel(main_window)
#     new_game_window.title("New Game")
#     new_game_window.geometry("180x50+250+200")
#     tkinter.Label(new_game_window, text="Do you want a new game?").grid(
#         row=0, column=0)
#     yes_no_button_frame = tkinter.Frame(new_game_window)
#     yes_no_button_frame.grid(row=1, column=0, rowspan=2)
#
#     yes_button = tkinter.Button(yes_no_button_frame, text="Yes!",
#                                 command=lambda a=new_game_window: new_game(a))
#     yes_button.grid(row=0, column=0, sticky="w")
#     no_button = tkinter.Button(yes_no_button_frame, text="No!", command=stop_program)
#     no_button.grid(row=0, column=1, sticky="w")


def get_result():
    global all_players
    global result_text

    players_score = {}
    dealer_score = dealer_score_label.get()
    if not all_players and dealer_score < 22:  # Empty
        result_text.set("Dealer Wins")
    else:
        for current_player in all_players:
            current_player_score = all_players[current_player]["score_label"]
            current_player_score = current_player_score.get()
            players_score[current_player] = current_player_score
        winners = []
        highest_score = get_players_highest_score()
        if dealer_score == highest_score:
            winners.append("Dealer")
        for current_player, score in players_score.items():
            if score == highest_score:
                winners.append(f"Player{current_player}")
        if len(winners) == 1:
            result_text.set(winners[0])
        else:
            winners = ", ".join(winners)
            result_text.set(f"draw: {winners}")

    # new_game_popup()


def get_next_available_player(current_player) -> int:
    """Get next not burned player with score below 22

    Uses global var `all_players`"""
    global all_players

    available_players = get_players_left_in_game()  # list

    ready_players = get_players_that_are_ready()

    # Players left in game - Ready players
    players_left = set(available_players)
    players_left = players_left.difference(ready_players)
    players_left = sorted(list(players_left))
    next_player = None
    # get next player
    current_player_index = available_players.index(current_player)

    if ready_players:  # if set not empty - True
        available_players = available_players[current_player_index + 1:]
        for player in available_players:
            if player in players_left:
                next_player = player
                break
        else:
            try:
                next_player = players_left[0]
                deal_dealer()
            except IndexError:
                if dealer_score_label.get() < get_players_highest_score():
                    deal_dealer()
                get_result()
    else:  # if set is empty - False
        if current_player_index == len(available_players) - 1:
            next_player = available_players[0]
            deal_dealer()
        else:
            next_player = current_player + 1

    return next_player


def turn_on_player_buttons(current_player=1):
    try:
        all_players[current_player]
    except KeyError:
        get_result()
        return None
    next_player_button = all_players[current_player]["button"]
    next_player_button2 = all_players[current_player]["button2"]
    next_player_button3 = all_players[current_player]["button3"][0]
    player_score = all_players[current_player]["score_label"]
    player_score = player_score.get()
    # hit button
    if player_score == 21:
        pass  # hit continues to be disabled
    else:
        next_player_button["state"] = "active"

    # stay button
    # If somebody reached 21 and the current player doesn't have 21
    if reached_21 and player_score != 21:
        pass  # stay disabled
    else:
        next_player_button2["state"] = "active"
        turn_on_stay_button(current_player)
    button3_value = all_players[current_player]["button3"][1]
    if not button3_value:  # True or false
        next_player_button3["state"] = "active"


def turn_off_player_buttons(current_player):
    current_player_button = all_players[current_player]["button"]
    current_player_button2 = all_players[current_player]["button2"]
    current_player_button["state"] = "disable"
    current_player_button2["state"] = "disable"
    next_available_player = get_next_available_player(current_player)
    turn_on_player_buttons(next_available_player)


def turns(players_info: dict) -> None:
    still_playing_players = list(players_info)
    disable_all_buttons(players_info)
    turn_on_player_buttons()


def create_card_frame():
    card_frame = tkinter.Frame(
        main_window, background="green", relief="sunken", borderwidth=1)
    card_frame.grid(row=1, column=0, columnspan=3, rowspan=2, sticky="ew")
    return card_frame


def build_player_count_and_frames():
    global all_players
    for player in range(1, players_count + 1):
        players_hand[player] = []
    all_players = draw_player_frames(players_count)


main_window = tkinter.Tk()
# Set up the screen and frames for the dealer and player
main_window.geometry("640x600")
main_window.title("Black Jack")
main_window.configure(bg="green")
result_text = tkinter.StringVar()
result = tkinter.Label(main_window, textvariable=result_text)
result.grid(row=0, column=0, columnspan=3)

card_frame = create_card_frame()

dealer_score_label = tkinter.IntVar()
tkinter.Label(card_frame, text="Dealer", background="green", fg="white").grid(
    row=0, column=0)
tkinter.Label(card_frame, textvariable=dealer_score_label, background="green",
              fg="white").grid(row=1, column=0)

# embedded frame hold the card images.
dealer_cards_frame = tkinter.Frame(card_frame, background="green")
dealer_cards_frame.grid(row=0, column=1, sticky="ew", rowspan=2)

# embedded frame to hold the card images

button_frame = tkinter.Frame(main_window)
button_frame.grid(row=3, column=0, columnspan=3, sticky='w')

play_img = tkinter.PhotoImage(file="cards_png/play.png")
tkinter.Label(button_frame, image=play_img, relief="raised").grid(
    row=0, column=0)

# load cards
cards = []
load_images(cards)
# print(cards)
# Create a new deck of cards and shuffle
deck = list(cards)
random.shuffle(deck)

# Create the list to store the dealer's and player's hands
dealer_hand = []
players_hand = {}

deal_dealer()
dealer_cards_frame.update()
width_of_cards = dealer_cards_frame.winfo_width()
height_of_cards = dealer_cards_frame.winfo_height()

players_count = 0
popup = build_popup()

main_window.wait_window(popup)
# all_players = {}
# for player in range(1, players_count + 1):
#     players_hand[player] = []
# all_players = draw_player_frames(players_count)
all_players = {}
game_over_pic = tkinter.PhotoImage(file="cards_png/game_over.png")
build_player_count_and_frames()
reached_21 = False
turns(all_players)
main_window.mainloop()
