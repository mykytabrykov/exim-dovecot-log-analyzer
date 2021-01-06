from document import Document
from es_config import EsConfig
from dovecot import Dovecot
from user_manager import UserManager
from event_manager import EventManager
import uuid

'''
"_source" : {
  "email" : "mykytabrykov@gmail.com ",
  "hostname" : "cp7",
  "logins" : {
    "success" : {
      "locations" : [
        {
          "ip" : "123.123.123.123",
          "country" : "Italy",
          "times" : 5
        },
        {
          "ip" : "322.22.21.11",
          "description" : "Germany",
          "times" : 2
        }
      ]
    }
  }
}
'''


class LogAnalyzer:
    def __init__(self):
        self.es_client = EsConfig().get_es_client()
        self.user_manager = UserManager()
        self.event_manager = EventManager()

    def dovecot(self):
        dovecot = Dovecot(self.es_client, self.user_manager, self.event_manager)
        dovecot.login_successful() # dovecot successful login analise

    def control_country(self):
        logs = self.__get_logs()
        for log in logs:
            user = self.__get_user(log)
            # print("User: ", user)
            if not user.source.check_country(log.source.location):
                print("Raise alert...")
                self.__generate_alert(log, user)
            self.es_client.update(index=log.index, id=log.id, body={"doc": {"pyAnalyzed": "true"}})
        self.update_users()
