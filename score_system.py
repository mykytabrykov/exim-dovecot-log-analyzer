from action_system import ActionSystem
import configparser
import os
import statistics


class ScoreSystem:
    def __init__(self):
        self.__config = configparser.ConfigParser()
        self.__config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        self.__config = self.__config['score']
        self.__action_system = ActionSystem()

    def evaluate_risk(self, revealed_event, user, options):
        score_increment = 0
        if revealed_event == 'dovecot-new-region':
            score_increment += 5
        if revealed_event == 'dovecot-login-failed':
            score_increment += options.doc_count / 1000
        if revealed_event == 'exim-sending-rate':
            print("New day ", options)
            new_day = options
            variance = statistics.variance(user.profile.exim.emails.sent.daily)
            standard_deviation = statistics.stdev(user.profile.exim.emails.sent.daily)
            mean = statistics.mean(user.profile.exim.emails.sent.daily)
            rsd = statistics.stdev(user.profile.exim.emails.sent.daily) / statistics.mean(user.profile.exim.emails.sent.daily)

            print("Daily Variance:", statistics.variance(user.profile.exim.emails.sent.daily))
            print("Daily Deviation:", statistics.stdev(user.profile.exim.emails.sent.daily))
            print("Daily Mean: ", statistics.mean(user.profile.exim.emails.sent.daily))
            print("Day RSD: ",
               statistics.stdev(user.profile.exim.emails.sent.daily) / statistics.mean(user.profile.exim.emails.sent.daily))

            try:
                score_increment += (new_day - mean) / standard_deviation
                score_increment -= rsd
                print("inc:", score_increment)
            except ZeroDivisionError:
                score_increment += 0
        if revealed_event == 'exim-login-failed':
            score_increment += options.doc_count / 1000

        user.profile.score += score_increment

        if user.profile.score >= self.__config.getint('level_1'):
            self.__action_system.generate_alert(revealed_event, user, options)
        if user.profile.score >= self.__config.getint('level_2'):
            devolpment = 'in corso'