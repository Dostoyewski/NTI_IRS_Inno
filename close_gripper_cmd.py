def gripper_close():
    header = "def myProg():\n"
    end = "end\n"
    prog = header # first put header into program code 
    prog += 'set_tool_digital_out(0, True)\n'
    prog += 'set_tool_digital_out(1, False)\n'
    prog += 'sleep(0.7)\n'
    prog += end
    return prog

def gripper_open():
    header = "def myProg():\n"
    end = "end\n"
    prog = header # first put header into program code 
    prog = ''
    prog += 'set_tool_digital_out(0, False)\n'
    prog += 'set_tool_digital_out(1, True)\n'
    prog += 'sleep(0.7)\n'
    prog += end
    return prog   
