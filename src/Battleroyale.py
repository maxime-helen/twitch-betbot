import string
import datetime
import time


class Battleroyale():

    def __init__(self, client, get_language_script, mods_list):
        self.client = client
        def get_language (option):
            return get_language_script('BATTLEROYALE', option)
        self.get_language_script = get_language
        self.mods_list = mods_list
        self.bets = []
        self.winner = None
        self.state = 'init'

        moderators_command_message = "Moderators commands : !startbet, !stopbet, !statusbet, !final <final top>, !lastwinner"

        @client.on("message")
        def onMessage(response):
            is_mod = self.is_moderator(response["username"])
            action = response["command"]
            bet = response["message"]
            username = response["username"]
            if (action == "startbet" or action == "stopbet" or action == "final") and is_mod:
                self.update_state(action, bet)
            elif action == "top" and self.is_state_in_lobby() :
                self.client.print_log("%s's bet : %s" % (username, bet))
                self.add_bet(username, bet)
            elif action == "statusbet" and is_mod:
                self.client.sendMessage("%s %s" % (self.get_language_script('status'), self.get_state()))
            elif action == "lastwinner" and is_mod:
                winner = self.get_winner()
                if winner != None:
                    self.client.sendMessage("%s %s" % (self.get_language_script('last_winner'), winner))
                else:
                    self.client.sendMessage(self.get_language_script('no_last_winner'))
            elif action == "cmdbet" :
                self.client.sendMessage(moderators_command_message)

    def is_state_in_game(self):
        return self.state == 'game'

    def is_state_in_lobby(self):
        return self.state == 'lobby'
    
    def is_state_in_init(self):
        return self.state == 'init'

    def update_state(self, action, bet):
        def print_warning():
            self.client.print_log("warning: %s action is invalid to update %s state" % (action, self.state))
        if self.is_state_in_init() :
            if action == 'startbet' :
                self.state = 'lobby'
                self.client.sendMessage(self.get_language_script("start_bet"))
            else:
                print_warning()
        elif self.is_state_in_lobby() :
            if action == 'stopbet' :
                self.state = 'game'
                self.client.sendMessage(self.get_language_script("stop_bet"))
            else:
                print_warning()
        elif self.is_state_in_game() :
            if action == 'final' :
                self.state = 'init'
                self.winner = self.get_username_by_first_bet(int(bet))
                self.bets = []
                if self.winner != None :
                    self.client.sendMessage("%s %s" % (self.get_language_script("final_winner"), self.winner))
                else :
                    self.client.sendMessage(self.get_language_script("final_no_winner"))
            else:
                print_warning()
        else :
            self.client.sendMessage(self.get_language_script("error_state"))

    def get_state(self):
        return self.state             
                
    def is_moderator(self, user):
        for mod in self.mods_list:
            if mod == user :
                return True
        return False
        
    def add_bet(self, username, bet):
        for field in self.bets :
            if  field["username"] == username :
                field["bet"] = bet
                return
        obj = {}
        obj["username"] = username
        obj["bet"] = bet
        self.bets.append(obj)
    
    def get_username_by_first_bet(self, bet):
        for field in self.bets :
            if int(field["bet"]) == bet :
                return field["username"]
    
    def get_usernames_by_bet(self, bet):
        tab_usernames = []
        for field in self.bets :
            if field["bet"] == bet :
                tab_usernames.append(field["username"])
        return tab_usernames   
    
    def get_winner(self) :
        return self.winner
