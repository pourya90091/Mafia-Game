import re


__version__ = 0.2
defined_roles = ["doctor", "don", "silencer", "detective", "normalpolice", "normalmafia", "terrorist"]


def check_choice_exist(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                func(*args, **kwargs)
            except ValueError:
                print(f"Chosen player is not exist.")
                continue
            else:
                break
    return wrapper


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.healed = False
        self.alive = True

    def __str__(self) -> str:
        return self.name

    def night_op(self) -> None:
        raise NotImplementedError()
    
    def take_shot(self):
        if self.healed:
            self.healed = False
        else:
            self.alive = False


class Doctor(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.side = "police"
        self.role = "doctor"
        self.inquiry = False
        self.silenced = False
        self.description = ""

    @check_choice_exist
    def night_op(self) -> None:
        global night_narrate

        players = game.get_players_by_name()

        choice = input(f"\nDoctor ({self.name}) choice to heal: ")

        target = game.players[players.index(choice)]

        for player in game.players:
            if player.healed:
                player.healed = False # Release the player who healed last night.
                break

        target.healed = True

        night_narrate += f"Doctor heals {target}. "


class Don(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.side = "mafia"
        self.role = "don"
        self.inquiry = False
        self.silenced = False
        self.description = ""

    @check_choice_exist
    def night_op(self) -> None:
        global night_narrate

        players = game.get_players_by_name()

        choice = input(f"\nDon ({self.name}) choice to shoot: ")

        target = game.players[players.index(choice)]
        target.take_shot()

        night_narrate += f"{target} takes shot from Don. {target} is {'alive' if target.alive else 'dead'}. "


class Silencer(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.side = "police" # Silencer is on the mafia side, but in counting, counted as police.
        self.role = "silencer"
        self.inquiry = False
        self.silenced = False
        self.description = ""

    @check_choice_exist
    def night_op(self) -> None:
        global night_narrate

        players = game.get_players_by_name()

        while True:
            choice = input(f"\nSilencer ({self.name}) choice to silence: ")

            target = game.players[players.index(choice)]

            if target.silenced: # Silencer can't silence a player for two nights in a row.
                print("Silencer can't silence a player for two nights in a row.")
                continue

            for player in game.players:
                if player.silenced:
                    player.silenced = False # Release the player who silenced last night.
                    break

            target.silenced = True

            night_narrate += f"Silencer silenced {target}. "

            break


class Detective(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.side = "police"
        self.role = "detective"
        self.inquiry = False
        self.silenced = False
        self.description = ""

    @check_choice_exist
    def night_op(self) -> None:
        global night_narrate

        players = game.get_players_by_name()

        choice = input(f"\nDetective ({self.name}) choice to inquiry: ")

        target = game.players[players.index(choice)]

        night_narrate += f"{target}'s inquiry: {target.inquiry if target.alive else 'No Result'}. "


class NormalPolice(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.side = "police"
        self.role = "normalpolice"
        self.inquiry = False
        self.silenced = False
        self.description = ""
    
    def night_op(self) -> None:
        """This role doesn't have operation at night."""


class NormalMafia(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.side = "mafia"
        self.role = "normalmafia"
        self.inquiry = True
        self.silenced = False
        self.description = ""
        self.heir_priority = 1 # Heir priority for make night shot decision (when Don is dead)
        self.inherited = False

    @check_choice_exist
    def night_op(self) -> None:
        if self.inherited:
            global night_narrate

            players = game.get_players_by_name()

            choice = input(f"\nNormalmafia ({self.name}) choice to shoot: ")

            target = game.players[players.index(choice)]
            target.take_shot()

            night_narrate += f"{target} takes shot from Don (decision made by {self.name} with {self.role} role). {target} is {'alive' if target.alive else 'dead'}. " 


class Terrorist(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.side = "mafia"
        self.role = "terrorist"
        self.inquiry = True
        self.silenced = False
        self.description = ""
        self.heir_priority = 2 # Heir priority for make night shot decision (when Don is dead)
        self.inherited = False

    @check_choice_exist
    def night_op(self) -> None:
        if self.inherited:
            global night_narrate

            players = game.get_players_by_name()

            choice = input(f"\nTerrorist ({self.name}) choice to shoot: ")

            target = game.players[players.index(choice)]
            target.take_shot()

            night_narrate += f"{target} takes shot from Don (decision made by {self.name} with {self.role} role). {target} is {'alive' if target.alive else 'dead'}. " 


class Game:
    def __init__(self, start_msg: str) -> None:
        self.start_msg = start_msg
        self.players: list[Player] = []
        self.roles = []
        self.distributed = False
        self.phase = "day"
        self.current_day = 1

    def voting(self):
        print()

        def get_votes(players: list, all_players):
            previous_players = []
            votes = []

            print("Vote between this players:", ", ".join(all_players))
            while True:
                for player in players:
                    if self.players[players.index(player)].silenced:
                        continue

                    vote = input(f"{player}'s vote: ")
                    if vote not in all_players:
                        for player in previous_players:
                            players.pop(players.index(player))
                        else:
                            previous_players = []

                        print(f"Please vote between this players:", ", ".join(all_players))
                        break
                    votes.append(vote)
                    previous_players.append(player)
                else:
                    print()
                    break
            
            return votes

        def get_voting_result(votes: list):
            new_votes = []
            votes_count = []
            for vote in votes:
                if vote not in new_votes:
                    new_votes.append(vote)
                    votes_count.append(votes.count(vote))
            else:
                return new_votes, votes_count

        def get_double_voters(double_voters: list, new_votes: list, votes_count: list):
            double_voters_names = []
            for double_voter in double_voters:
                double_voter = new_votes[votes_count.index(double_voter)]

                votes_count.pop(new_votes.index(double_voter))
                new_votes.pop(new_votes.index(double_voter))

                double_voters_names.append(double_voter)
            else:
                return double_voters_names # Names of double voters

        def double_voters_loop(double_voters: list, players: list):
            all_players = [*players]

            while True:
                if len(double_voters) == 1:
                    target = self.players[all_players.index(double_voters[0])]
                    elimination(target)
                elif len(double_voters) > 1:
                    votes = get_votes([*players], [*double_voters])
                    new_votes, votes_count = get_voting_result(votes)

                    double_voters = [vote_count for vote_count in votes_count if vote_count == max(votes_count)]
                    double_voters = get_double_voters(double_voters, new_votes, votes_count)

                    double_voters_loop(double_voters, [*players])
                else:
                    print("I DON'T KNOW.")

                break

        def elimination(target: Player, spot_role=True):
            target.alive = False
            print(f"{target} eliminated with {target.role if spot_role else 'Unknown'} role.")

            if not spot_role: # If player eliminated by terrorist.
                return None

            if target.role == "terrorist":
                self.update_alive_players()
                players = self.get_players_by_name()

                while True:
                    victim = input("\nVictim name (to assassinate by the eliminated terrorist): ")
                    if victim not in players:
                        print(f"Chosen player is not exist.")
                        continue

                    print()
                    target = self.players[players.index(victim)]
                    elimination(target, spot_role=False)
                    break

        players = self.get_players_by_name()

        votes = get_votes([*players], [*players])
        new_votes, votes_count = get_voting_result(votes)

        double_voters = [vote_count for vote_count in votes_count if vote_count > 1]

        if max(votes_count) > (len(self.players) / 2):
            target_index = votes_count.index(max(votes_count))
            target = self.players[players.index(new_votes[target_index])]
            elimination(target)
        elif len(double_voters) == 1:
            print("No one eliminated.")
        elif len(double_voters) > 1:
            double_voters = get_double_voters(double_voters, new_votes, votes_count)

            votes = get_votes([*players], [*double_voters])
            new_votes, votes_count = get_voting_result(votes)

            double_voters = [vote_count for vote_count in votes_count if vote_count == max(votes_count)]
            double_voters = get_double_voters(double_voters, new_votes, votes_count)

            double_voters_loop(double_voters, [*players])
        else:
            print("No one eliminated.")

    def day_phase(self) -> None:
        while True:
            command = input("\nType a command (Type \"commands\" to see all commands): ")
            if command == "commands":
                print("""
=====================================================================
God Commands:
    END - Day ends, voting begins and then night phase begins.
    status - Show status of all players.
    remove <player_name> - Removes selected player from the game.
=====================================================================""")
            elif command == "END":
                self.voting()
                self.update_alive_players()
                break # Ends day.
            elif command == "status":
                print()
                [print(f"{i + 1} - {player} is {player.role}{' (silenced)' if player.silenced else ''}") for i, player in enumerate(self.players)]
            elif re.search(r"^remove", command):
                choice = re.findall(r"^remove (\w+)", command)
                if choice:
                    players = self.get_players_by_name()

                    choice = choice[0]
                    if choice in players:
                        target = self.players[players.index(choice)]
                        target.alive = False

                        print(f"{target} removed with {target.role} role.")

                        self.update_alive_players()
                    else:
                        print(f"Chosen player is not exist.")

        self.phase = "night"

    def night_phase(self) -> None:
        global night_narrate; night_narrate = ""

        players = self.get_prioritize_players()

        for player in players:
            player.night_op()
        else:
            self.update_alive_players()
            self.phase = "day"

        print("\n" + f"Night {self.current_day}'s narrate: " + night_narrate)

    def update_alive_players(self):
        self.players = [player for player in self.players if player.alive]

    def check_winner(self) -> bool:
        police_team = 0
        mafia_team = 0

        for player in self.players:
            if player.side == "police":
                police_team += 1
            elif player.side == "mafia":
                mafia_team += 1
        else:
            if mafia_team == 0:
                print("\nPolice Won!")
                return True
            elif police_team <= mafia_team:
                print("\nMafia Won!")
                return True
            else:
                return False

    def get_prioritize_players(self) -> list[Player]:
        prioritize_players: list[Player] = []
        players = [player for player in self.players]

        doctor = [player for player in players if player.role == "doctor"]
        if doctor:
            doctor = doctor[0]
            prioritize_players.append(players.pop(players.index(doctor)))

        don = [player for player in players if player.role == "don"]
        if don:
            don = don[0]
            prioritize_players.append(players.pop(players.index(don)))
        else:
            mafia_side = [player for player in players if player.side == "mafia"]
            if not len(mafia_side) < 1:    
                inheritance_priorities = [player.heir_priority for player in mafia_side]

                preferred_mafia = mafia_side[inheritance_priorities.index(min(inheritance_priorities))]
                preferred_mafia.inherited = True

                prioritize_players.append(players.pop(players.index(preferred_mafia)))

        silencer = [player for player in players if player.role == "silencer"]
        if silencer:
            silencer = silencer[0]
            prioritize_players.append(players.pop(players.index(silencer)))

        detective = [player for player in players if player.role == "detective"]
        if detective:
            detective = detective[0]
            prioritize_players.append(players.pop(players.index(detective)))

        for player in players:
            prioritize_players.append(player)
        else:
            return prioritize_players

    def get_players_by_name(self):
        return [player.name for player in self.players]

    def get_players(self):
        try:
            self.players = input("\nPlayers: ")
            self.players = re.findall(r"\w+", self.players)

            if len(self.players) < 6:
                raise Exception("Mafia game require 6 or more than 6 players to start.")
            elif len(set(self.players)) < len((self.players)):
                raise Exception("Each player must have a unique name.")
        except Exception as err:
            self.players: list[Player] = []
            raise Exception(err)

    def get_roles(self):
        try:
            self.roles = input("\nRoles: ").lower()
            self.roles = re.findall(r"\w+", self.roles)

            for _ in range(len(self.players) - len(self.roles)):
                self.roles.append("normalpolice")

            for role in self.roles:
                if role not in defined_roles:
                    raise Exception(f'"{role}" is not in defined roles.')

            if self.roles.count("don") > 1:
                raise Exception(f'Mafia Game only supports 1 Don in the game.')
            elif self.roles.count("doctor") > 1:
                raise Exception(f'Mafia Game only supports 1 Doctor in the game.')
            elif self.roles.count("silencer") > 1:
                raise Exception(f'Mafia Game only supports 1 Silencer in the game.')
        except Exception as err:
            self.roles = []
            raise Exception(err)

    def distribute_roles(self):
        temp_list = []

        self.players = set(self.players) # Randomize players.
        self.players = list(self.players)

        for i, player_name in enumerate(self.players):
            if self.roles[i] == "doctor":
                temp_list.append(Doctor(player_name))
            elif self.roles[i] == "don":
                temp_list.append(Don(player_name))
            elif self.roles[i] == "silencer":
                temp_list.append(Silencer(player_name))
            elif self.roles[i] == "detective":
                temp_list.append(Detective(player_name))
            elif self.roles[i] == "normalpolice":
                temp_list.append(NormalPolice(player_name))
            elif self.roles[i] == "normalmafia":
                temp_list.append(NormalMafia(player_name))
            elif self.roles[i] == "terrorist":
                temp_list.append(Terrorist(player_name))
        else:
            self.players = temp_list
            self.distributed = True                

    def run(self):
        if self.start_msg:
            print(self.start_msg); self.start_msg = None
        else:
            exit()

        while True:
            try:
                if not self.players:
                    self.get_players()

                if not self.roles:
                    self.get_roles()

                if not self.distributed:
                    self.distribute_roles()
            except Exception as err:
                print(err)
                continue

            if self.check_winner():
                exit()

            if self.phase == "day":
                print(f"\n---------- Day {self.current_day} ----------")
                self.day_phase()

            if self.phase == "night":
                print(f"\n---------- Night {self.current_day} ----------")
                self.night_phase()

            self.current_day += 1

global game
game = Game(f"Mafia Game {__version__}")

try:
    game.run()
except KeyboardInterrupt:
    print()
    exit()
