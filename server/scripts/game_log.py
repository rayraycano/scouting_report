from crawlers.tdl.game_log import get_game_log

if __name__ == '__main__':
    print('enter event id')
    event_id = input()
    game_log = get_game_log(event_id)
    print(game_log)