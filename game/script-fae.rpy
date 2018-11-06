default persistent.currentmusic = 0
default persistent.playergender = None # False = male, True = female, None = unknown/other
default persistent.playerbdate = get_now().date()
default persistent.first_launch = get_now()

default persistent.s_name = cur_lang().s_names[0]
default persistent.talk_delay = 20

init python:
    update_bg = False
    from_menu = False
    
    config.developer = True # I'm a god of this world too.
    
    def periodic_callback():
        global update_bg, from_menu
    
        if update_bg and from_menu:
            backgrounds.hide_current(True)
            backgrounds.show()
            renpy.restart_interaction()
            update_bg = False
            from_menu = False
    
    config.periodic_callback = periodic_callback
    
    def reset_topics():
        persistent.seen_topics = {}
        for cat in topic_cats:
            cat.update_seen()

    #Look for seen CGs.
    s_clear = 1 # 0 = FLAGS: 1 = All sayori's CGs are clear, 2 = Other girls' any CG is clear (expect monika's and non-school CGs), 4 = Any sayori's CGs is clear
    if persistent.clearall is None: #The current save isn't based on the old one from the original game
        s_clear = 0b111 #I think it's true for the almost DDLC fan.
    else:
        for i in xrange(4):
            if persistent.clear[i]:
                s_clear |= 2
                break
        for i in xrange(6, 9):
            if persistent.clear[i]:
                s_clear |= 4
            else:
                s_clear &= 0b110
    
    #Getting the current user name
    import subprocess
    import os
    process_list = []
    currentuser = ""
    if renpy.windows:
        try:
            process_list = subprocess.check_output("wmic process get Description", shell=True).lower().replace("\r", "").replace(" ", "").split("\n")
        except:
            pass
        try:
            for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
                user = os.environ.get(name)
                if user:
                    currentuser = user
        except:
            pass
    
    
    #Add special flag for the waiting state
    justIsSitting = False
    
    #Adding special screenshot callback
    screenshot_notice = config.screenshot_callback
    
    def screenshot_topic(location):
        screenshot_notice(location)
        if not persistent.seen_topics.get("s_screenshot") and justIsSitting:
            special_topics("firstscreenshot", location)
    
    config.screenshot_callback = screenshot_topic
    
    ## Mood codes:
    ## 'h' = happy
    ## 'vh' = very happy
    ## 's' = sad
    ## 'b' = bored
    ## 'a' = angry
    ## 'hr' = horny
    
    s_mood = 'h' #happy
    
    def show_s_mood(at = ss1, look_at_right = False, mood = None):
        if not mood:
            mood = s_mood
        
        code = '7aaaa'
        
        if mood == 'vh':
            code = '7aeaa'
        elif mood == 's':
            code = '7afbb'
        elif mood == 'b':
            code = '7affb'
        elif mood == 'a':
            code = '6afac'
        elif mood == 'hr':
            code = '7bafa'
        
        if look_at_right:
            code = code[:-2] + 'b' + code[-1]
        
        renpy.show("sayori " + code, at_list = [at])
    
    random_topics_said = 0
    RANDOM_TOPICS_LIMIT = 8
    RANDOM_TOPICS_BAN_HOURS = 6
    random_topics_banned = None #None = non-banned, [timedate] = banned from
    
    ## New poems
    
    
default persistent.lastVersion = config.version

label change_s_name(name = "Sayori"):
    python:
        s_name = name
        if persistent.s_name != name:
            persistent.s_name = name
    return

label s_intro:
    #$ persistent.clearall = True
    $ s_name = glitchtext(6)

    #$ persistent.autoload = "ch30_main"
    #if not config.developer:
    #    $ style.say_dialogue = style.default_monika
    $ delete_all_saves()
    stop music fadeout 2.0
    
    call s_intro_1
    
    $persistent.playthrough = 5
    $ persistent.autoload = "s_autoload"
    $renpy.quit()
    return
    
    
label s_autoload(test = False):
    $ s_name = persistent.s_name or "Sayori"
    $ gender = persistent.playergender

    $backgrounds.show('spaceroom')
    
    $music_switch(persistent.currentmusic or 0)

    if persistent.playthrough == 5:
        call s_intro_2
        $persistent.playthrough = 6
    else:
        if persistent.lastVersion != config.version:
            show sayori 7aaaa at ss1
            
            s "Hello, [player]!"
            s 7aaca "The game had been a bit buggy for a pretty long time but I've found a way to fix it."
            s 7aaaa "I hope, I did all right this time."
            s "I also added some new topics and one feature, that you'll like."
            s "I've finally added the poem list, so you now can read any of my old poems again."
            s 7aeca "But what's more, I'll use this menu also to share my new poems with you."
            if "s_topics_hobbies_poems" in persistent.seen_topics:
                s 7acaa "I've already told you about my new poems, haven't I?"
                s 7aaaa "Anyway, I hope you'll like them too..."
            else:
                s "I hope you'll like them too..."
            s 7acaa "And that you too have something good for me."
            s 7aaaa "So tell me, if you really have."
            
            if not test:
                $persistent.lastVersion = config.version
        elif persistent.lastLaunch and persistent.lastLaunch.date() != get_now().date():
            $renpy.call(first_greeting, get_time_of_day())
        else:
            call expression get_random_gretting().label
    
    $ launch_dt = get_now()
    jump s_loop

label s_loop:
    hide screen topic_ui
    show screen feat_ui()
    
    $justIsSitting = True
    
    $show_s_mood()
    
    python:
        config.skipping = False
        config.allow_skipping = False
        config.skip_indicator = False
    
    
    # Wait before saying something new
    if not random_topics_banned:
        window hide(config.window_hide_transition)
        $ waittime = renpy.random.randint(40 + round(persistent.talk_delay * 0.75), 40 + persistent.talk_delay)
        $ renpy.pause(waittime)
        window auto
    else:
        python:
            if (random_topics_banned - get_now()).seconds >= RANDOM_TOPICS_BAN_HOURS * 3600:
                random_topics_banned = None
                random_topics_said = 0
        pause 5 #To prevent negavite infinity loop effects
    
    # Pick a random Sayori topic
    python:
        random_topic()
        
    jump s_loop
    


label s_react(id):
    show sayori 6aaaa at ss1 zorder 2
    hide screen topic_ui
    $justIsSitting = False
    
    $ config.allow_skipping = True
    $ config.skip_indicator = True
    call expression "s_reaction_" + id
    $s_mood = _return or s_mood
    
    jump s_loop

