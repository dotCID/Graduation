'''
A simple script to provide some dummy data for testing purposes
'''
import zmq, json, random, time

#get current time in milliseconds
millis = lambda: int(round(time.time() * 1000))

## CHANNEL_TARGETDATA
tg_context = zmq.Context()
tg_socket = tg_context.socket(zmq.PUB)
tg_socket.bind(CHANNEL_TARGETDATA)

findTime = millis()
found = False

## CHANNEL_MOVEMENTDATA
md_context = zmq.Context()
md_socket = md_context.socket(zmq.PUB)
md_socket.bind(CHANNEL_MOVEMENTDATA)

## CHANNEL_ENERGYDATA
ed_context = zmq.Context()
ed_socket = ed_context.socket(zmq.PUB)
ed_socket.bind(CHANNEL_ENERGYDATA)

## CHANNEL_MODE
mode_context = zmq.Context()
mode_socket = mode_context.socket(zmq.PUB)
mode_socket.bind(CHANNEL_MODE)


while True:

    ## CHANNEL_TARGETDATA
    if random.random() < 0.5: found = True
    if found: findTime = millis()
    
    tar_x = random.randrange(0, 1920/2)
    tar_y = random.randrange(0, 1080/2)
    deg_x = tar_x * 0.0725
    deg_y = tar_y * 0.0725
    
    tg_message =   {
                    't'       : millis(),
                    'findTime': findTime,
                    'found'   : found,
                    'tar_px'  : {'x':tar_x, 'y':tar_y},
                    'tar_dg'  : {'x':deg_x, 'y':deg_y}
                   }
    tg_socket.send_json(tg_message)
    
    ## CHANNEL_MOVEMENTDATA
    md_message =   {
                    't'       : millis(),
                    'deg_x'   : random.uniform(0.0, 360.0),
                    'deg_y'   : random.uniform(0.0, 360.0),
                    'deg_z'   : random.uniform(0.0, 360.0)
                    }
    md_socket.send_json(md_message)
    
    ## CHANNEL_ENERGYDATA
    energy = random.uniform(0.0, 1000.0)
    eg_label = "none"
    if   energy > 750 : eg_label = "high"
    elif energy > 250 : eg_label = "low"
    
    ed_message =   {
                    't'        : millis(),
                    'energy'   : energy,
                    'eg_label' : eg_label
                   }
    eg_socket.send_json(ed_message)
    
    ## CHANNEL_MODE
    mode = "A"
    if random.random() < 0.5: mode = "B"
    
    mode_message = {
                    't'   : millis(),
                    'mode': mode
                   }
    mode_socket.send_json(mode_message)
    
    time.sleep(50)
