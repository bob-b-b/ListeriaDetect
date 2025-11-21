class display: #The idea is that the different displays set the screen, the show actually sends it to the screen

    async def display_graph():
        raise NotImplementedError()
    
    async def display_buffer_next():
        raise NotImplementedError()
    
    async def display_sample_next():
        raise NotImplementedError()
    
    async def display_cleaning_next():
        raise NotImplementedError()
    
    async def display_result():
        raise NotImplementedError()
    
    async def display_cleaning():
        raise NotImplementedError()

    async def show_screen():#maybe check if screen changed, so no unnecessary computation
        raise NotImplementedError()