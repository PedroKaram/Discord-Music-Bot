def get_response(message: str) -> str:
    p_message = message.lower()

    if p_message == "hello":
        return 'Hello lets play some music!'
    
    if message == "help":
        return '`These are the commands you can use to play some music\n-?play + youtube url => Plays a song\n-?pause => To pause the current song\n-?resume => To resume the paused song\n-?stop => To stop music from playing`'
    
    return 'I didn\'t understand you. Try typing "help"'