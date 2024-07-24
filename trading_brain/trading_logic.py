from ig import IgUsa

def main():
    trade_api = IgUsa("demo_config.json")
    trade_api.create_session(trade_api.pt_ws)

if __name__=="__main__":
    main()