import re

class Cs():

    def __init__(self, client, get_language_script, mods_list):
        self.mods_list = mods_list
        
        self.client = client
        def get_language (option):
            return get_language_script('CSGO', option)
        self.get_language_script = get_language
        self.mods_list = mods_list
        self.bets = []
        self.winner = None
        self.state = 'init'
        @client.on("message")
        def onMessage(response):
            is_mod = self.is_moderator(response["username"])
            action = response["command"]
            score = response["message"]
            username = response["username"]
            if (action == "startbet" or action == "stopbet" or action == "winner" or action == "loser") and is_mod:
                self.update_state(action, score)
            elif (action == "win" or action == "lose") and self.state == "lobby" :
                self.client.print_log("%s's bet : %s" % (username, score))
                self.add_score(username, action, score)
            elif action == "statusbet" and is_mod:
                self.client.sendMessage("%s %s" % (self.get_language_script('status'), self.get_state()))
            elif action == "lastwinner" and is_mod:
                winner = self.get_winner()
                if winner != None:
                    self.client.sendMessage("%s %s" % (self.get_language_script('last_winner'), winner))
                else:
                    self.client.sendMessage(self.get_language_script('no_last_winner'))
            elif action == "cmdbet" :
                self.client.sendMessage("Moderators commands : !startbet, !stopbet, !statusbet, !winner|loser, !lastwinner")
            else :
                self.client.sendMessage(self.get_language_script("error_state"))
 
    def is_state_in_game(self):
        return self.state == 'game'

    def is_state_in_lobby(self):
        return self.state == 'lobby'
    
    def is_state_in_init(self):
        return self.state == 'init'

    def update_state(self, action, score):
        def print_warning():
            self.client.print_log("%s action is invalid to update %s state" % (action, self.state))
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
            if action == 'loser' or action == 'winner':
                self.state = 'init'
                if action == 'loser':
                    self.winner = self.get_first_username_by_bet('lose', score)
                    print self.winner
                if action == 'winner':
                    self.winner = self.get_first_username_by_bet('win', score)
                    print self.winner
                if self.winner != None :
                    self.client.sendMessage("%s %s" % (self.get_language_script("final_winner"), self.winner))
                else :
                    self.client.sendMessage(self.get_language_script("final_no_winner"))
            else:
                print_warning()

    def get_state(self):
        return self.state             
                
    def is_moderator(self, user):
        for mod in self.mods_list:
            if mod == user :
                return True
        return False
    
    def __match_score(self, score):
        results = []
        regex = r"(\d\d?) ?- ?(\d\d?)"
        matches = re.finditer(regex, score)
        for matchNum, match in enumerate(matches):
            matchNum = matchNum + 1
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                results.append(int(match.group(groupNum)))
        return sorted(results)

    def __match_bet(self, cmd):
        regex = r"(win|lose)"
        return re.findall(regex, cmd)[0]

    def add_score(self, username, bet, score):
        for field in self.bets :
            if  field["username"] == username :
                return
        bet = self.__match_bet(bet)
        match_score = self.__match_score(score)
        obj = {}
        obj["username"] = username
        obj["bet"] = bet
        obj["lower_score"] = match_score[0]
        obj["higher_score"] = match_score[1]
        self.bets.append(obj)
    
    def get_first_username_by_bet(self, bet, score):
        match_score = self.__match_score(score)
        print match_score
        for field in self.bets :
            print(field, field["bet"] == bet, field["lower_score"] == match_score[0],  field["higher_score"] == match_score[1])
            if field["bet"] == bet and field["lower_score"] == match_score[0] and field["higher_score"] == match_score[1]:
                return field["username"]
    
    # def get_usernames_by_bet(self, bet):
    #     tab_usernames = []
    #     for field in self.bets :
    #         if field["bet"] == bet :
    #             tab_usernames.append(field["username"])
    #     return tab_usernames
    
    # def get_startbet_state(self):
    #     return self.bets_enable    
    
    def get_winner(self) :
        return self.winner
