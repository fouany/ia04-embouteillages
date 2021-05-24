# -*- coding: utf-8 -*-

# 菅原のＰＣにLocal-Brokerを作成した．
# このためredisを'local-host'にインストールした．その時のport numberは6379だった
# def connect 関数は　'local-host'に接続し、port=6379
# EdgeBaseAgentのインスタンスのcoterie nameはedge_setting.iniのファイルに記述している
# Coterieのすべてのエージェントプログラムを立ち上げるのは、そのフォルダでstart.cmdを実行

from agent_v2.agent_message import AgentMessage


#import paho.mqtt.client as mqtt
#import ssl
import configparser

import redis


class EdgeBaseAgent:
    # Agent Actions
    ACTIONS = {
        # 'TEST' : 'act_debug'
    }

    def load_settings(self):
        # Coterie設定の読み込み
        config = configparser.ConfigParser()
        config.read('edge_settings.ini')

        self.coterie = config['SETTINGS']['CoterieName']
        self.host = config['SETTINGS']['BrokerIP']
        self.topic = 'coterie-' + self.coterie

        print("[LOG]", "Load Settings : Coterie - ", self.coterie)

    def connect(self):
        self.port = 6379    #Redisのインストール時にポート番号が指定される

        # client.tls_set("agent_space.ca", cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
        # client.tls_insecure_set(True)
        self.blackboard = redis.StrictRedis(host=self.host, port=self.port, db=0)

        pubsub = self.blackboard.pubsub()
        pubsub.psubscribe(**{self.topic: self.on_message})
        self.thread = pubsub.run_in_thread(sleep_time=0.01)

        # if not self.input_only:
        #     client.loop_forever()
        self.on_connect()
        print("[LOG] Network Access - OK")

    def reconnect(self):
        self.connect()

    def __init__(self, name, auto_load=True, local=True):
        # エージェントの初期化
        self.name = name
        self.load_settings()
        self.local = local

        if auto_load:
            self.start()


    def start(self):
        self.connect()
        self.initialize()
        self.initialized()


    def stop(self):
        self.thread.stop()


    def on_connect(self):
        print('[LOG] COTERIE status {0}'.format(0))
        # client.subscribe(self.topic, 2)

        msg = AgentMessage()
        msg.Type = "INFORM"
        msg.From = self.name
        msg.To = "ALL"
        msg.Action = "HELLO"
        msg.Args = ""
        self.send_message(msg)

    def on_message(self, msg):
        # AgentMessage型にパース
        data = msg['data'].decode() #msg.payload.decode("utf-8")
        agt_msg = AgentMessage(data)

        if agt_msg.To in (self.name, "ALL") and agt_msg.From != self.name:
            #            print("\033[1;46m" + "[LOG] Received message '" + str(msg.payload) + "' on topic '"
            #              + msg.topic + "' with QoS " + str(msg.qos) + "\033[1;m")

            self.receive_message(agt_msg)

            # キャッシュキューに登録
            #        que.put(msg.payload.decode("utf-8"))

    def send_message(self, msg: AgentMessage, qos=2):
        self.blackboard.publish(self.topic, msg.to_json())

    """
    for override
    """
    def receive_message(self, msg: AgentMessage):
        # print("[DEBUG-NEW]", msg.to_json())
        if msg.Action in self.ACTIONS:
            action_name = self.ACTIONS[msg.Action]
            try:
                method = getattr(self, action_name)
            except AttributeError:
                print("[ERROR]", action_name, "is nothing.")
            method(msg)

    def initialize(self):
        pass

    def initialized(self):
        pass

    # --- Properties ---
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    