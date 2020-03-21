def close():
    prog = ''
    prog += 'set_tool_digital_out(0, True)\n'
    prog += 'set_tool_digital_out(1, False)\n'
    prog += 'sleep(0.7)\n'
    return prog

def open():
     prog = ''
     prog += 'set_tool_digital_out(0, False)\n'
     prog += 'set_tool_digital_out(1, True)\n'
     prog += 'sleep(0.7)\n'
     return prog   
