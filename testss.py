def gen1(): 
    print("start")
    try: 
        print("yielding 1 ...")
        yield 1
    finally: 
        print("clean")
        
        
        
def gen2():
    return gen1()
    
    
next(gen2())