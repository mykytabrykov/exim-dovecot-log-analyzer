from alert_system import AlertSystem


class ScoreSystem:
    def __init__(self, service):
        self.service = service
        self.alert_system = AlertSystem()



    def evaluate_risk(self, revealed_event, user, options):
        if self.service == "dovecot":
            if revealed_event == 'new-region':
                user.score += 5
                self.alert_system.generate_alert(self.service, 'new-region', user, options)
            if revealed_event == 'login-failed':
                print("bef:",user.score)
                user.score += options.doc_count / 1000
                print("after:", user.score)

